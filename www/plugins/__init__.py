"""Plugin riêng cho blog nkthanh.dev (pyssg 0.1.0, API node/registry).

- ``WwwMarkdown``    -- markdown→HTML (thêm arithmatex cho công thức + cờ math,
  tiền tính ngày & link tag theo locale).
- ``WwwCollections`` -- danh sách bài viết phân trang theo locale (trang chủ).
- ``WwwTaxonomy``    -- trang tag/category (chỉ mục + từng term) theo locale.
- ``WwwRss``         -- feed RSS theo locale.
- ``HighlightThemes``-- stylesheet Pygments scope theo ``data-theme``.
- ``Redirects``      -- trang chuyển hướng tĩnh cho URL cũ.
- ``StaticFiles``    -- copy ``static/`` ra gốc output.
"""

from __future__ import annotations

from .collections import WwwCollections, www_collections
from .highlighting import HighlightThemes
from .markdown import WwwMarkdown, wwwmarkdown
from .redirects import Redirects
from .rss import WwwRss
from .static_files import StaticFiles
from .taxonomy import WwwTaxonomy, www_taxonomy

__all__ = [
    "HighlightThemes",
    "Redirects",
    "StaticFiles",
    "WwwCollections",
    "WwwMarkdown",
    "WwwRss",
    "WwwTaxonomy",
    "www_collections",
    "www_taxonomy",
    "wwwmarkdown",
]
