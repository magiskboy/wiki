"""Site-local pyssg plugins cho Thanh's wiki.

Các tuỳ biến đặc thù của wiki sống cùng site, không nằm trong kernel pyssg:

- ``WikiMeta``  -- tiêu đề lấy từ H1 đầu tiên + slug ASCII (bỏ dấu tiếng Việt)
  cho URL ``/<slug>/``, và bỏ qua các file không build (``_tags``, ``Tổng quan``).
"""

from __future__ import annotations

from .content import WikiContent
from .external import ExternalSources
from .graph import WikiGraph, WikiGraphPage
from .meta import WikiMeta, slugify
from .taxonomy import WikiTaxonomy

__all__ = [
    "ExternalSources",
    "WikiContent",
    "WikiGraph",
    "WikiGraphPage",
    "WikiMeta",
    "WikiTaxonomy",
    "slugify",
]
