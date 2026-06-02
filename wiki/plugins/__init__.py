"""Plugin tùy biến cho Thanh's wiki (pyssg 0.1.0, API node/registry).

- ``WikiMarkdown`` -- markdown→HTML (codehilite, arithmatex, mermaid, normalize)
  thay 3 plugin built-in markdown/highlight/mermaid.
- ``WikiSlug``     -- URL phẳng ``/slug/`` ASCII bỏ dấu (route tap).
- ``WikiGraph``    -- đồ thị tri thức + ``link_counts`` + trang ``/graph/``.
- ``WikiTaxonomy`` -- trang ``/tags/``, ``/categories/`` khớp layout wiki.
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
