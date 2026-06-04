"""Tiền tính dữ liệu hiển thị mà core 0.2.0 không tự lo.

pyssg 0.2.0 đã có sẵn ``markdown(extensions=...)`` (thêm arithmatex), và
``collections``/``taxonomy``/``rss`` đều i18n-aware. Hai thứ duy nhất còn thiếu
cho blog này — vì ``render`` chưa expose seam đăng ký Jinja filter/global — là
các trường *đã định dạng theo locale*:

- ``WwwEnrich``: tap parse, bơm ``date_display`` / ``tag_links`` /
  ``description_html`` (+ cờ ``math``) vào ``doc.meta`` cho trang bài đơn
  (``single.html.j2`` đọc ``page`` = ``doc.meta``).
- ``WwwCollections``: subclass ``CollectionsPlugin`` mỏng, chỉ override hai hook
  ``make_item`` / ``item_to_dict`` để thẻ bài (``postitem.html.j2``) có
  ``date_display`` / ``description`` (mô tả đã render) / ``tag_links``. Toàn bộ
  cơ chế phân trang + i18n vẫn của built-in.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from pyssg.core.node import Document
from pyssg.core.types import NodeKind
from pyssg.plugins.collections import CollectionItem, CollectionsPlugin

from ._util import format_date, render_description, tag_links

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder
    from pyssg.core.node import Node, Page

_ENRICH_STAGE = 260  # sau markdown (200) + highlight (250)
_MATH_MARKER = 'class="arithmatex"'


class WwwEnrich:
    """Bơm các trường hiển thị đã địa phương hoá vào ``doc.meta`` cho trang bài."""

    name = "www_enrich"
    cache_version = "1.0.0"

    def __init__(self, *, default_locale: str = "vi") -> None:
        self._default = default_locale

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.parse.tap(self.name, stage=_ENRICH_STAGE)
            def _parse(node: Node) -> None:
                if node.kind is not NodeKind.MARKDOWN or not isinstance(node, Document):
                    return
                lang = node.meta.get("lang")
                locale = lang if isinstance(lang, str) and lang else self._default
                node.meta["date_display"] = format_date(node.meta.get("date"), locale)
                node.meta["tag_links"] = tag_links(
                    node.meta.get("tags"), locale, self._default
                )
                node.meta["description_html"] = render_description(
                    node.meta.get("description")
                )
                html = node.meta.get("content_html")
                if isinstance(html, str) and _MATH_MARKER in html:
                    node.meta["math"] = True


def www_enrich(*, default_locale: str = "vi") -> WwwEnrich:
    return WwwEnrich(default_locale=default_locale)


class WwwCollections(CollectionsPlugin):
    """Collections built-in + thẻ bài đã địa phương hoá (date/desc/tag_links)."""

    def __init__(self, *specs: object, default_locale: str = "vi") -> None:
        super().__init__(specs=tuple(specs))  # type: ignore[arg-type]
        self._default = default_locale

    def make_item(self, doc: Document, page: Page) -> CollectionItem:
        # Giữ mô tả curated (frontmatter ``description``) cho thẻ; built-in chỉ
        # lấy ``excerpt`` tự sinh. Nhét vào ô ``excerpt`` (chuỗi tự do) để
        # ``item_to_dict`` render — không cần thêm field vào dataclass frozen.
        item = super().make_item(doc, page)
        description = doc.meta.get("description")
        if isinstance(description, str) and description:
            item = dataclasses.replace(item, excerpt=description)
        return item

    def item_to_dict(self, item: CollectionItem) -> dict[str, object]:
        return {
            "url": item.url,
            "title": item.title,
            "date": item.date,
            "date_display": format_date(item.date, item.locale or self._default),
            "description": render_description(item.excerpt),
            "tags": list(item.tags),
            "tag_links": tag_links(item.tags, item.locale or self._default, self._default),
        }
