"""Plugin tùy biến cho Thanh's wiki (pyssg 0.2.0, API node/registry).

Đây là tính năng *bespoke* nên 0.2.0 không cấu hình-hoá thay được:

- ``WikiMarkdown`` -- markdown→HTML (codehilite giữ class CSS sẵn có, arithmatex,
  mermaid→div tiền-markdown để không xung đột codehilite, normalize HTML,
  rewrite link repo → GitHub/GitLab). Built-in ``mermaid()`` không dùng được ở
  đây vì codehilite "nuốt" fence mermaid trước.
- ``WikiSlug``     -- URL phẳng ``/slug/`` ASCII bỏ dấu (route tap).
- ``WikiGraph``    -- đồ thị tri thức từ mục "Liên kết tri thức" + ``link_counts``
  + trang ``/graph/`` (khác mô hình link của contrib ``graph()``).
- ``WikiTaxonomy`` -- ``/tags/``, ``/categories/`` (category theo thư mục cha,
  xếp hạng theo ``link_counts``, tag-cloud) — built-in chỉ đọc frontmatter.
- ``WikiHome``     -- dashboard trang chủ từ ``index.md``.
"""

from __future__ import annotations

from .graph import WikiGraph, wiki_graph
from .home import WikiHome, wiki_home
from .markdown import WikiMarkdown, wiki_markdown
from .slug import WikiSlug, wiki_slug
from .taxonomy import WikiTaxonomy, wiki_taxonomy

__all__ = [
    "WikiGraph",
    "WikiHome",
    "WikiMarkdown",
    "WikiSlug",
    "WikiTaxonomy",
    "wiki_graph",
    "wiki_home",
    "wiki_markdown",
    "wiki_slug",
    "wiki_taxonomy",
]
