"""Markdown processor + post-processing HTML body."""

from __future__ import annotations

import html
import re

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from pymdownx.arithmatex import ArithmatexExtension

from .config import MATH_MARKER, META_SECTION_TITLES
from .links import rewrite_md_links, rewrite_repo_links

MERMAID_BLOCK = re.compile(
    r"```mermaid\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)

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
            # Bảo vệ LaTeX khỏi markdown parser (vd: `d_{model}` bị thành italic),
            # giữ TeX nguyên trong delimiter `\(...\)` / `\[...\]` để KaTeX render
            # phía client. generic=True bật cả delimiter `$...$` và `$$...$$`.
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


def has_math(body_html: str) -> bool:
    return MATH_MARKER in body_html


def normalize_article_html(body_html: str) -> str:
    """Chuẩn hóa cấu trúc bài viết để render nhất quán.

    - Mỗi bài chỉ giữ một <h1> (tiêu đề); các <h1> còn lại hạ xuống <h2>.
    - Các mục phụ trợ (Nguồn tham khảo, Liên kết tri thức, Tags) được gắn
      class để tạo phong cách meta nhẹ nhàng.
    - Danh sách Tags được gắn class tag-list để hiển thị dạng chip.
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

    # Bọc bảng để cuộn ngang trên màn hình hẹp.
    body_html = re.sub(
        r"<table>(.*?)</table>",
        r'<div class="table-wrap"><table>\1</table></div>',
        body_html,
        flags=re.DOTALL,
    )
    return body_html


def convert_body(
    md_text: str,
    processor: markdown.Markdown,
    repo_remotes: dict[str, dict[str, str]] | None = None,
    slug_index: dict[str, str] | None = None,
) -> str:
    rewritten = rewrite_md_links(md_text, slug_index=slug_index)
    if repo_remotes:
        rewritten = rewrite_repo_links(rewritten, repo_remotes)
    prepared = mermaid_to_divs(rewritten)
    processor.reset()
    return normalize_article_html(processor.convert(prepared))
