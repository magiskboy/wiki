"""Trang category: page-per-category + category index (map).

URL convention song song với tag:
- `web/categories/<slug>/index.html` — danh sách bài trong category.
- `web/category/index.html` — danh sách toàn bộ category.
"""

from __future__ import annotations

import html
import shutil
from collections import defaultdict
from pathlib import Path

from ..article import Article, category_slug, extract_category
from ..config import REPO_ROOT, SKIP_WIKI, WEB_DIR
from ..template import render_body_template, render_page


def build_category_index(
    article_meta: list[tuple[Path, str, str, list[str]]],
) -> dict[str, list[Article]]:
    """Group bài theo tên category (giữ Tiếng Việt để display).

    File ở wiki root (không nằm trong folder) bị bỏ qua khỏi category index.
    """
    by_category: dict[str, list[Article]] = defaultdict(list)
    for md_path, slug, title, _ in article_meta:
        if md_path.stem in SKIP_WIKI:
            continue
        cat = extract_category(md_path)
        if cat is None:
            continue
        article = Article(slug=slug, title=title, href=f"{slug}.html")
        by_category[cat].append(article)
    return dict(by_category)


def render_category_page_html(
    category: str,
    articles: list[Article],
    root: str,
    link_counts: dict[str, int],
) -> str:
    ranked = sorted(
        articles,
        key=lambda a: (-link_counts.get(a.slug, 0), a.title.lower()),
    )
    items = "\n".join(
        f'      <li class="index-top-item">'
        f'<span class="index-top-rank">{idx:02d}</span>'
        f'<a class="index-top-link" href="{root}{a.href}">{html.escape(a.title)}</a>'
        f'<span class="index-top-count" title="số liên kết">'
        f'{link_counts.get(a.slug, 0)}</span>'
        f"</li>"
        for idx, a in enumerate(ranked, start=1)
    )
    return render_body_template(
        "category_page.html",
        label=html.escape(category),
        count=str(len(articles)),
        items=items,
        root=root,
    )


def render_category_index_html(
    category_counts: dict[str, int],
    root: str,
) -> str:
    if not category_counts:
        return '<h1>Bản đồ category</h1>\n<p class="tag-index-note">Chưa có category.</p>'
    items = sorted(category_counts.items(), key=lambda x: (-x[1], x[0]))
    cards = "\n".join(
        f'      <li><a class="tag-card" href="{root}categories/{category_slug(name)}/">'
        f'<span class="tag-card-name">{html.escape(name)}</span>'
        f'<span class="tag-card-count">{count} bài</span>'
        f"</a></li>"
        for name, count in items
    )
    return render_body_template(
        "category_index.html",
        total_categories=str(len(category_counts)),
        cards=cards,
    )


def write_category_pages(
    by_category: dict[str, list[Article]],
    *,
    link_counts: dict[str, int],
) -> int:
    cat_root = WEB_DIR / "categories"
    if cat_root.exists():
        shutil.rmtree(cat_root)
    cat_root.mkdir(parents=True, exist_ok=True)

    count = 0
    for name, articles in sorted(by_category.items()):
        slug = category_slug(name)
        cat_dir = cat_root / slug
        cat_dir.mkdir(parents=True, exist_ok=True)
        content = render_category_page_html(
            name,
            articles,
            root="../../",
            link_counts=link_counts,
        )
        page = render_page(
            title=f"Category: {name}",
            description=f"{len(articles)} bài viết trong category {name}",
            content=content,
            root="../../",
        )
        out = cat_dir / "index.html"
        out.write_text(page, encoding="utf-8")
        count += 1
        print(f"  category:{name} -> {out.relative_to(REPO_ROOT)}")
    return count


def write_category_map(category_counts: dict[str, int]) -> None:
    cat_index_dir = WEB_DIR / "category"
    cat_index_dir.mkdir(parents=True, exist_ok=True)
    content = render_category_index_html(category_counts, root="../")
    page = render_page(
        title="Bản đồ category",
        description="Phân loại bài viết theo chủ đề",
        content=content,
        root="../",
        main_class=" site-main--wide",
    )
    out = cat_index_dir / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"  category index -> {out.relative_to(REPO_ROOT)}")
