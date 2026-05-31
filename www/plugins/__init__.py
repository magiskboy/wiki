"""Site-local pyssg plugins for the nkthanh.dev blog.

These customizations live with the site, not in the pyssg kernel:

- ``TemplateHelpers`` -- a locale-aware ``format_date`` template global.
- ``HighlightThemes`` -- ``data-theme``-scoped Pygments stylesheets.
- ``Math`` -- flags pages using ``$$`` so the layout loads KaTeX.
- ``Categories`` -- the ``/categories/`` index and per-category listing pages.
- ``Tags`` -- the ``/tags/`` index (per-tag pages come from the preset).
"""

from __future__ import annotations

from .categories import Categories, Tags
from .dates import TemplateHelpers, format_date
from .highlighting import HighlightThemes
from .math import Math

__all__ = [
    "Categories",
    "HighlightThemes",
    "Math",
    "Tags",
    "TemplateHelpers",
    "format_date",
]
