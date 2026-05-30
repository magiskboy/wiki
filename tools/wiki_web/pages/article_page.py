"""Render trang cho một bài viết wiki — body HTML đã convert + KaTeX nếu cần."""

from __future__ import annotations

from pathlib import Path

import markdown

from ..article import (
    append_tags_and_date,
    extract_date,
    extract_description,
    extract_tags,
    extract_title,
    md_to_html_name,
    strip_frontmatter,
)
from ..config import KATEX_SNIPPET, REPO_ROOT, WEB_DIR
from ..markdown_ext import convert_body, has_math
from ..template import render_page


def write_article_page(
    md_path: Path,
    processor: markdown.Markdown,
    repo_remotes: dict[str, dict[str, str]],
    *,
    slug_index: dict[str, str] | None = None,
    index_body_html: str | None = None,
) -> None:
    """Convert một file wiki/*.md sang web/*.html.

    `index_body_html` (nếu có) thay thế body cho `_index.md` — vì _index dùng
    mục lục dựng từ article_meta thay vì convert markdown.

    `slug_index`: mapping `md stem → slug HTML`, dùng để rewrite link `.md`
    sang slug `.html` (filename Tiếng Việt → slug ASCII).
    """
    md_text = md_path.read_text(encoding="utf-8")
    title = extract_title(md_text, md_path.stem.replace("-", " ").title())
    description = extract_description(md_text)

    if index_body_html is not None:
        body_html = index_body_html
        main_class = " site-main--index"
    else:
        body = strip_frontmatter(md_text)
        tags = extract_tags(md_text)
        date_str = extract_date(md_text)
        prepared = append_tags_and_date(body, tags, date_str, tag_href="tags/")
        body_html = convert_body(
            prepared, processor,
            repo_remotes=repo_remotes,
            slug_index=slug_index,
        )
        main_class = ""

    extra_scripts = KATEX_SNIPPET if has_math(body_html) else ""
    page = render_page(
        title=title,
        description=description,
        content=body_html,
        main_class=main_class,
        extra_scripts=extra_scripts,
    )
    out = WEB_DIR / md_to_html_name(md_path, title)
    out.write_text(page, encoding="utf-8")
    print(f"  {md_path.name} -> {out.relative_to(REPO_ROOT)}")
