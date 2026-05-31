"""Chuyển markdown wiki → HTML với độ trung thực như generator wiki_web cũ.

Plugin thay thế ``Markdown`` + ``Highlight`` mặc định của pyssg vì wiki cần đúng
bộ extension cũ (codehilite class-based đã có sẵn CSS trong ``static/style.css``,
arithmatex bảo vệ LaTeX, mermaid), cùng hậu xử lý ``normalize_article_html``
(hạ H1 thừa, đánh dấu meta heading, bọc bảng) và phần phụ Tags/ngày cập nhật.

``transform`` (waterfall, stage 0): ``source.body`` → ``source.content``.
Đồng thời gắn ``page.math = True`` cho trang có công thức để layout nạp KaTeX.

Rewrite link ``.md``/repo được tách sang plugin riêng (Phase 2).
"""

from __future__ import annotations

import html
import re

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from pymdownx.arithmatex import ArithmatexExtension

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.content import is_generated
from pyssg.models import Source

from .links import rewrite_asset_links, rewrite_md_links, rewrite_repo_links

# Heading được nhận diện là "meta section" để tô class article-meta-heading.
META_SECTION_TITLES = {
    "Tags",
    "Nguồn tham khảo",
    "Nguồn",
    "Liên kết tri thức",
    "Liên kết",
}

# Marker mà ArithmatexExtension(generic=True) ghi vào HTML khi gặp math.
MATH_MARKER = 'class="arithmatex"'

MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
H1_RE = re.compile(r"<h1([^>]*)>(.*?)</h1>", re.DOTALL)
H2_RE = re.compile(r"<h2([^>]*)>(.*?)</h2>", re.DOTALL)
STRIP_TAGS_RE = re.compile(r"<[^>]+>")


def make_md_processor() -> markdown.Markdown:
    return markdown.Markdown(
        extensions=[
            "sane_lists",
            "smarty",
            TableExtension(),
            FencedCodeExtension(),
            CodeHiliteExtension(
                css_class="codehilite",
                guess_lang=True,
                linenums=False,
            ),
            ArithmatexExtension(generic=True, smart_dollar=True),
        ],
        output_format="html5",
    )


def mermaid_to_divs(text: str) -> str:
    def to_div(match: re.Match[str]) -> str:
        body = match.group(1).strip()
        escaped = html.escape(body)
        return f'<pre class="mermaid">{escaped}</pre>\n'

    return MERMAID_BLOCK.sub(to_div, text)


def normalize_article_html(body_html: str) -> str:
    """Chuẩn hóa cấu trúc bài viết để render nhất quán.

    - Mỗi bài chỉ giữ một <h1>; các <h1> còn lại hạ xuống <h2>.
    - Các mục phụ trợ (Nguồn tham khảo, Liên kết tri thức, Tags) gắn class meta.
    - Danh sách Tags gắn class tag-list để hiển thị dạng chip.
    - Bọc bảng để cuộn ngang trên màn hình hẹp.
    """
    state = {"seen": 0}

    def demote_h1(match: re.Match[str]) -> str:
        state["seen"] += 1
        if state["seen"] == 1:
            return match.group(0)
        return f"<h2{match.group(1)}>{match.group(2)}</h2>"

    body_html = H1_RE.sub(demote_h1, body_html)

    def mark_meta(match: re.Match[str]) -> str:
        attrs, inner = match.group(1), match.group(2)
        text = STRIP_TAGS_RE.sub("", inner).strip()
        if text in META_SECTION_TITLES and "article-meta-heading" not in attrs:
            return f'<h2{attrs} class="article-meta-heading">{inner}</h2>'
        return match.group(0)

    body_html = H2_RE.sub(mark_meta, body_html)

    body_html = re.sub(
        r"(>Tags</h2>\s*<ul)>",
        r'\1 class="tag-list">',
        body_html,
        count=1,
    )

    body_html = re.sub(
        r"<table>(.*?)</table>",
        r'<div class="table-wrap"><table>\1</table></div>',
        body_html,
        flags=re.DOTALL,
    )
    return body_html


def append_tags_and_date(
    md_body: str, tags: list[str], date_str: str | None
) -> str:
    """Append khối Tags (link tới trang tag) và ngày cập nhật vào cuối body."""
    body = md_body.rstrip()
    parts: list[str] = [body] if body else []
    if tags:
        tag_lines = ["# Tags", ""]
        for t in tags:
            tag_lines.append(f"- [{t}](/tags/{t}/)")
        parts.append("\n".join(tag_lines))
    if date_str:
        parts.append(f"_Cập nhật: {date_str}_")
    return "\n\n".join(parts) + "\n"


def _tags_of(source: Source) -> list[str]:
    raw = source.frontmatter.get("tags")
    if isinstance(raw, list):
        return [str(t).strip() for t in raw if str(t).strip()]
    if isinstance(raw, str) and raw.strip():
        s = raw.strip().strip("[]")
        return [t.strip() for t in s.split(",") if t.strip()]
    return []


def _date_of(source: Source) -> str | None:
    val = source.frontmatter.get("date")
    if val is None:
        return None
    text = str(val).strip()
    return text or None


class WikiContent:
    def __init__(self) -> None:
        self._processor = make_md_processor()

    def apply(self, builder: Builder) -> None:
        builder.hooks.transform.tap("WikiContent", self._transform)

    def _transform(self, source: Source, build: Build) -> Source:
        if is_generated(source):
            return source
        slug_index = build.meta.get("slug_index") or {}
        repo_remotes = build.meta.get("repo_remotes") or {}
        assets = build.meta.setdefault("external_assets", set())

        md = source.body
        md = rewrite_repo_links(md, repo_remotes)
        md = rewrite_asset_links(md, assets)
        md = rewrite_md_links(md, slug_index)

        prepared = append_tags_and_date(md, _tags_of(source), _date_of(source))
        prepared = mermaid_to_divs(prepared)
        self._processor.reset()
        html_body = normalize_article_html(self._processor.convert(prepared))
        source.content = html_body
        if MATH_MARKER in html_body:
            source.meta["math"] = True
        return source
