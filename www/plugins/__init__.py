"""Plugin riêng còn lại của blog nkthanh.dev (pyssg 0.2.0).

0.2.0 đã cấu hình-hoá gần hết các nhược điểm cũ: ``markdown(extensions=...)``,
``collections``/``taxonomy``/``rss`` i18n-aware, ``redirects`` + ``asset_copy``
mounts built-in. Chỉ còn hai mảnh thực sự không cấu hình-hoá được:

- ``WwwEnrich`` / ``WwwCollections`` -- tiền tính trường hiển thị đã địa phương
  hoá (``render`` chưa có seam đăng ký Jinja filter).
- ``HighlightThemes`` -- CSS Pygments đa ``data-theme`` (``highlight`` chỉ nhận
  một ``style``).
"""

from __future__ import annotations

from .enrich import WwwCollections, WwwEnrich, www_enrich
from .highlighting import HighlightThemes
from .obsidian_images import ObsidianImages, obsidian_images

__all__ = [
    "HighlightThemes",
    "ObsidianImages",
    "WwwCollections",
    "WwwEnrich",
    "obsidian_images",
    "www_enrich",
]
