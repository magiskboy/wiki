"""Trang tag: vừa là page-per-tag, vừa là tag cloud index."""

from __future__ import annotations

import html
import shutil
from collections import defaultdict
from pathlib import Path

from ..article import Article
from ..config import REPO_ROOT, SKIP_WIKI, WEB_DIR
from ..template import render_body_template, render_page


def tag_font_size_rem(count: int, c_min: int, c_max: int) -> float:
    if c_max == c_min:
        return 1.15
    t = (count - c_min) / (c_max - c_min)
    return 0.85 + t * 1.4


def render_tag_index_html(
    tag_counts: dict[str, int],
    root: str,
) -> str:
    if not tag_counts:
        return '<h1>Bản đồ tag</h1>\n<p class="tag-index-note">Chưa có tag.</p>'

    counts = list(tag_counts.values())
    c_min, c_max = min(counts), max(counts)
    items = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))

    links: list[str] = []
    for tag, count in items:
        href = f"{root}tags/{tag}/"
        label = html.escape(tag)
        size = tag_font_size_rem(count, c_min, c_max)
        links.append(
            f'    <a class="tag-cloud-item" href="{href}" '
            f'style="font-size: {size:.3f}rem" '
            f'title="{label} — {count} bài">{label}</a>'
        )

    return render_body_template(
        "tag_index.html",
        total_tags=str(len(tag_counts)),
        links="\n".join(links),
    )


def render_tag_page_html(
    tag: str,
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
        "tag_page.html",
        label=html.escape(tag),
        count=str(len(articles)),
        items=items,
        root=root,
    )


def build_tag_index(
    articles: list[tuple[Path, str, str, list[str]]],
) -> dict[str, list[Article]]:
    # meta tuple = (md_path, slug, title, tags).
    by_tag: dict[str, list[Article]] = defaultdict(list)
    for md_path, slug, title, tags in articles:
        if md_path.stem in SKIP_WIKI:
            continue
        href = f"{slug}.html"
        article = Article(slug=slug, title=title, href=href)
        for tag in tags:
            by_tag[tag].append(article)
    return dict(by_tag)


def write_tag_pages(
    by_tag: dict[str, list[Article]],
    *,
    link_counts: dict[str, int],
) -> int:
    tag_root = WEB_DIR / "tags"
    if tag_root.exists():
        shutil.rmtree(tag_root)
    tag_root.mkdir(parents=True, exist_ok=True)

    count = 0
    for tag, articles in sorted(by_tag.items()):
        tag_dir = tag_root / tag
        tag_dir.mkdir(parents=True, exist_ok=True)
        content = render_tag_page_html(
            tag,
            articles,
            root="../../",
            link_counts=link_counts,
        )
        page = render_page(
            title=f"Tag: {tag}",
            description=f"{len(articles)} bài viết với tag {tag}",
            content=content,
            root="../../",
        )
        out = tag_dir / "index.html"
        out.write_text(page, encoding="utf-8")
        count += 1
        print(f"  tag:{tag} -> {out.relative_to(REPO_ROOT)}")
    return count


def write_tag_map(tag_counts: dict[str, int]) -> None:
    tag_index_dir = WEB_DIR / "tag"
    tag_index_dir.mkdir(parents=True, exist_ok=True)
    content = render_tag_index_html(tag_counts, root="../")
    page = render_page(
        title="Bản đồ tag",
        description="Trực quan hóa tag theo số bài viết",
        content=content,
        root="../",
        main_class=" site-main--wide",
    )
    out = tag_index_dir / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"  tag index -> {out.relative_to(REPO_ROOT)}")
