"""Orchestrator của build pipeline.

`build(clean=False)` đầy đủ flow:
  1. (tuỳ chọn) xoá nội dung web/
  2. Copy assets
  3. Quét article metadata + xây tag index
  4. Render từng bài viết (gồm trang _index dùng mục lục)
  5. Render tag pages + tag map
  6. Build graph data + render graph page
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from .article import (
    article_slug,
    extract_tags,
    extract_title,
    wiki_files,
)
from .assets import copy_assets
from .config import SKIP_WIKI, WEB_DIR, WIKI_DIR
from .graph import build_graph_data, compute_link_counts, write_graph_json
from .links import load_repo_remotes
from .markdown_ext import make_md_processor
from .pages.article_page import write_article_page
from .pages.category_page import (
    build_category_index,
    write_category_map,
    write_category_pages,
)
from .pages.graph_page import write_graph_page
from .pages.index_page import render_index_html
from .pages.tag_page import build_tag_index, write_tag_map, write_tag_pages

# Tuple shape của article meta: (md_path, slug, title, tags).
# `slug` là canonical id của bài (filename-stem cho _index/_tags, slugify(title)
# cho các bài thường) — dùng làm node id trong graph và làm tên file HTML output.
ArticleMeta = tuple[Path, str, str, list[str]]


def _scan_articles() -> list[ArticleMeta]:
    meta: list[ArticleMeta] = []
    for md_path in wiki_files():
        if md_path.stem in SKIP_WIKI:
            continue
        md_text = md_path.read_text(encoding="utf-8")
        title = extract_title(md_text, md_path.stem.replace("-", " ").title())
        tags = extract_tags(md_text)
        slug = article_slug(md_path, title)
        meta.append((md_path, slug, title, tags))
    return meta


def _build_slug_index(article_meta: list[ArticleMeta]) -> dict[str, str]:
    """Mapping tên-file-md (không kèm `.md`) → slug HTML.

    Dùng để `rewrite_md_links` đổi link `./Tên File.md` → `slug.html`.
    Key giữ nguyên Unicode (chính là `md_path.stem`).
    """
    return {md_path.stem: slug for md_path, slug, _, _ in article_meta}


def _clean_web() -> None:
    if not WEB_DIR.exists():
        return
    for item in WEB_DIR.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def build(clean: bool = False, link_count: str = "degree") -> int:
    if not WIKI_DIR.is_dir():
        print(f"Không tìm thấy {WIKI_DIR}", file=sys.stderr)
        return 1

    if clean:
        _clean_web()

    WEB_DIR.mkdir(parents=True, exist_ok=True)
    copy_assets()

    processor = make_md_processor()
    repo_remotes = load_repo_remotes()
    article_meta = _scan_articles()
    slug_index = _build_slug_index(article_meta)

    by_tag = build_tag_index(article_meta)
    tag_counts = {tag: len(arts) for tag, arts in by_tag.items()}

    by_category = build_category_index(article_meta)
    category_counts = {name: len(arts) for name, arts in by_category.items()}

    graph_data = build_graph_data(article_meta, slug_index)
    link_counts = compute_link_counts(graph_data, link_count)

    count = 0
    for md_path in wiki_files():
        index_body = None
        if md_path.stem == "_index":
            index_body = render_index_html(
                article_meta,
                tag_counts,
                category_counts,
                link_counts=link_counts,
                root="",
            )
        write_article_page(
            md_path, processor, repo_remotes,
            slug_index=slug_index,
            index_body_html=index_body,
        )
        count += 1

    tag_page_count = write_tag_pages(by_tag, link_counts=link_counts)
    write_tag_map(tag_counts)
    cat_page_count = write_category_pages(by_category, link_counts=link_counts)
    write_category_map(category_counts)
    write_graph_json(graph_data)
    write_graph_page(graph_data)

    print(
        f"\nĐã build {count} trang wiki, {tag_page_count} trang tag, "
        f"{cat_page_count} trang category, "
        f"đồ thị {len(graph_data['nodes'])} node / {len(graph_data['edges'])} cạnh"
    )
    print("Chạy: python -m http.server 8080 --directory web")
    return 0
