"""Hàm thuần dùng chung cho các plugin wiki (không phụ thuộc pyssg).

Tách riêng để dễ test và tái dùng: slug ASCII (bỏ dấu tiếng Việt), rewrite link
repo → URL GitHub/GitLab, chuyển mermaid fence → div, và chuẩn hóa HTML bài viết
(hạ H1 thừa, đánh dấu heading phụ, bọc bảng).
"""

from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

# --- slug ASCII -----------------------------------------------------------


def ascii_slug(title: str) -> str:
    """Slug ASCII bỏ dấu tiếng Việt: "Tổng quan về Flask" -> "tong-quan-ve-flask"."""
    s = title.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# --- rewrite link repo ----------------------------------------------------

REPO_REF_LINK = re.compile(
    r"(\[[^\]]*\]\()(?:\.\./)*references/repos/([^/)]+)((?:/[^):\s]+)*/?)(?::(\d+))?(\))"
)

FILE_EXTENSIONS = {
    ".cpp", ".h", ".hpp", ".c", ".py", ".pyi", ".js", ".ts", ".tsx", ".jsx",
    ".md", ".mdx", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
    ".sh", ".bash", ".zsh", ".rs", ".go", ".java", ".kt", ".rb",
    ".html", ".css", ".scss", ".sql", ".xml", ".txt", ".env",
    ".dockerfile", ".lock", ".proto",
}


def _looks_like_file(sub_path: str) -> bool:
    if not sub_path or sub_path.endswith("/"):
        return False
    return Path(sub_path).suffix.lower() in FILE_EXTENSIONS


def _build_repo_url(remote: dict[str, str], sub_path: str, line: str | None) -> str:
    host = remote.get("host", "github").lower()
    owner = remote["owner"]
    repo = remote["repo"]
    branch = remote.get("branch", "main")
    sub = sub_path.lstrip("/").rstrip("/")
    is_file = _looks_like_file(sub_path)
    kind = "blob" if is_file else "tree"
    if host == "gitlab":
        base = f"https://gitlab.com/{owner}/{repo}/-/{kind}/{branch}"
    else:
        base = f"https://github.com/{owner}/{repo}/{kind}/{branch}"
    url = f"{base}/{sub}" if sub else base
    if is_file and line:
        url += f"#L{line}"
    return url


def rewrite_repo_links(text: str, remotes: dict[str, dict[str, str]]) -> str:
    """``(../)*references/repos/<repo>/...[:line]`` → URL GitHub/GitLab."""
    if not remotes:
        return text

    def replace(match: re.Match[str]) -> str:
        prefix, repo_name, sub_path, line, end = match.groups()
        remote = remotes.get(repo_name)
        if not remote:
            return match.group(0)
        return f"{prefix}{_build_repo_url(remote, sub_path or '', line)}{end}"

    return REPO_REF_LINK.sub(replace, text)


# --- chuẩn hóa HTML bài viết ----------------------------------------------

META_SECTION_TITLES = {
    "Tags",
    "Nguồn tham khảo",
    "Nguồn",
    "Liên kết tri thức",
    "Liên kết",
}

MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
H1_RE = re.compile(r"<h1([^>]*)>(.*?)</h1>", re.DOTALL)
H2_RE = re.compile(r"<h2([^>]*)>(.*?)</h2>", re.DOTALL)
STRIP_TAGS_RE = re.compile(r"<[^>]+>")


def mermaid_to_divs(text: str) -> str:
    def to_div(match: re.Match[str]) -> str:
        body = match.group(1).strip()
        escaped = html.escape(body)
        return f'<pre class="mermaid">{escaped}</pre>\n'

    return MERMAID_BLOCK.sub(to_div, text)


def normalize_article_html(body_html: str) -> str:
    """Hạ H1 thừa → H2, đánh dấu heading phụ (Nguồn/Liên kết) và bọc bảng."""
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
