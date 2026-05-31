"""Site-local pyssg plugins for the nkthanh.dev blog.

These customizations live with the site, not in the pyssg kernel:

- ``TemplateHelpers`` -- a locale-aware ``format_date`` template global.
- ``HighlightThemes`` -- ``data-theme``-scoped Pygments stylesheets.
- ``Math`` -- flags pages using ``$$`` so the layout loads KaTeX.
- ``Categories`` -- the ``/categories/`` index and per-category listing pages.
"""

from __future__ import annotations

from .categories import Categories
from .dates import TemplateHelpers, format_date
from .highlighting import HighlightThemes
from .math import Math

__all__ = [
    "Categories",
    "HighlightThemes",
    "Math",
    "TemplateHelpers",
    "format_date",
]
