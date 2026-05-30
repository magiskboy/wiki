"""Mục lục — top bài viết nhiều liên kết nhất + lưới tag-card."""

from __future__ import annotations

import html
from pathlib import Path

from ..article import category_slug
from ..config import SKIP_WIKI
from ..template import render_body_template

TOP_N = 10


def render_index_html(
    article_meta: list[tuple[Path, str, str, list[str]]],
    tag_counts: dict[str, int],
    category_counts: dict[str, int],
    *,
    link_counts: dict[str, int],
    root: str,
) -> str:
    # meta tuple = (md_path, slug, title, tags). Slug đã được pre-compute từ
    # title (slugify) để vừa làm node id graph vừa làm tên file HTML output.
    articles = [
        (slug, title, f"{slug}.html")
        for md_path, slug, title, _ in article_meta
        if md_path.stem not in SKIP_WIKI
    ]

    ranked = sorted(
        articles,
        key=lambda a: (-link_counts.get(a[0], 0), a[1].lower()),
    )[:TOP_N]

    top_items = "\n".join(
        f'      <li class="index-top-item">'
        f'<span class="index-top-rank">{idx:02d}</span>'
        f'<a class="index-top-link" href="{root}{href}">{html.escape(title)}</a>'
        f'<span class="index-top-count" title="số liên kết">'
        f'{link_counts.get(slug, 0)}</span>'
        f'</li>'
        for idx, (slug, title, href) in enumerate(ranked, start=1)
    )

    tag_items = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))
    cards = "\n".join(
        f'      <li><a class="tag-card" href="{root}tags/{t}/">'
        f'<span class="tag-card-name">{html.escape(t)}</span>'
        f'<span class="tag-card-count">{c} bài</span>'
        f'</a></li>'
        for t, c in tag_items
    )

    cat_items = sorted(category_counts.items(), key=lambda x: (-x[1], x[0]))
    category_cards = "\n".join(
        f'      <li><a class="tag-card" href="{root}categories/{category_slug(name)}/">'
        f'<span class="tag-card-name">{html.escape(name)}</span>'
        f'<span class="tag-card-count">{c} bài</span>'
        f'</a></li>'
        for name, c in cat_items
    )

    return render_body_template(
        "index_page.html",
        article_count=str(len(articles)),
        tag_count=str(len(tag_counts)),
        category_count=str(len(category_counts)),
        top=top_items,
        cards=cards,
        category_cards=category_cards,
        root=root,
    )
