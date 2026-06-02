"""WwwCollections: danh sách bài viết phân trang theo locale.

Tái hiện hành vi blog của site cũ: bài viết mỗi locale gom lại, sắp mới nhất
trước theo ``date``, phân trang tại gốc locale — trang 1 là trang chủ
(``/`` hoặc ``/en/``), trang N là ``<gốc>page/N/``.

Chạy ở ``evaluate_collections`` (sau permalink nên trang bài đã có URL cuối). Lặp
trên các ``Page`` sinh từ document (draft không sinh page nên tự loại) và đọc URL
đã được i18n định tuyến.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from pyssg.core.node import Document, Page
from pyssg.core.types import NodeKind

from ._util import base_path, date_sort_key, locale_prefix, post_card

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder


def _post_pages(build: Build) -> list[tuple[str, Document]]:
    """(url, doc) cho mỗi bài viết đã publish (Page sinh từ Document markdown)."""
    out: list[tuple[str, Document]] = []
    for node in build.graph.nodes():
        if not (isinstance(node, Page) and node.generated_from):
            continue
        doc = build.graph.get(node.generated_from[0])
        if not (isinstance(doc, Document) and doc.kind is NodeKind.MARKDOWN):
            continue
        # Chỉ lấy bài trong .../posts/ (loại các trang khác nếu có sau này).
        if "/posts/" not in (doc.source_path or ""):
            continue
        out.append((node.url, doc))
    return out


class WwwCollections:
    name = "www_collections"
    cache_version = "1.0.0"

    def __init__(self, *, default_locale: str = "vi", page_size: int = 10) -> None:
        self._default_locale = default_locale
        self._page_size = max(1, page_size)

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name, after=("permalink",))
            def _eval(b: Build) -> None:
                self._build(b)

    def _site_title(self, build: Build) -> str:
        config = build.builder.config
        if config is not None:
            title = config.site.get("title")
            if isinstance(title, str):
                return title
        return "Posts"

    def _build(self, build: Build) -> None:
        by_locale: dict[str, list[tuple[str, Document]]] = defaultdict(list)
        for url, doc in _post_pages(build):
            lang = doc.meta.get("lang")
            locale = lang if isinstance(lang, str) and lang else self._default_locale
            by_locale[locale].append((url, doc))

        locales = sorted(by_locale)
        owned: set[str] = set()
        for locale in locales:
            posts = sorted(
                by_locale[locale],
                key=lambda pair: date_sort_key(pair[1].meta),
                reverse=True,
            )
            cards = [
                post_card(doc.meta, url, locale, self._default_locale)
                for url, doc in posts
            ]
            owned |= self._paginate(build, locale, locales, cards)

        for node in list(build.graph.nodes()):
            if node.id.startswith("page:wwwlist:") and node.id not in owned:
                build.graph.remove(node.id)

    def _switcher(self, current: str, locales: list[str]) -> list[dict[str, object]]:
        return [
            {
                "lang": loc,
                "url": base_path(loc, self._default_locale),
                "active": loc == current,
            }
            for loc in locales
        ]

    def _paginate(
        self, build: Build, locale: str, locales: list[str], cards: list[dict[str, object]]
    ) -> set[str]:
        base = base_path(locale, self._default_locale)
        size = self._page_size
        total = max(1, (len(cards) + size - 1) // size)
        translations = self._switcher(locale, locales)
        owned: set[str] = set()
        for n in range(1, total + 1):
            chunk = cards[(n - 1) * size : n * size]
            url = base if n == 1 else f"{base}page/{n}/"
            prev_url = None if n == 1 else (base if n == 2 else f"{base}page/{n - 1}/")
            next_url = f"{base}page/{n + 1}/" if n < total else None
            pid = f"page:wwwlist:{locale}:{n}"
            owned.add(pid)
            self._set_page(
                build,
                pid,
                url,
                {
                    "title": self._site_title(build),
                    "lang": locale,
                    "locale_prefix": locale_prefix(locale, self._default_locale),
                    "entries": chunk,
                    "translations": translations,
                    "paginator": {
                        "number": n,
                        "total_pages": total,
                        "prev_url": prev_url,
                        "next_url": next_url,
                    },
                },
            )
        return owned

    @staticmethod
    def _set_page(build: Build, pid: str, url: str, meta: dict[str, object]) -> None:
        existing = build.graph.get(pid)
        if isinstance(existing, Page):
            existing.url = url
            existing.template = "list.html.j2"
            existing.meta = meta
        else:
            build.graph.add_node(
                Page(id=pid, kind=NodeKind.PAGE, url=url, template="list.html.j2", meta=meta)
            )


def www_collections(*, default_locale: str = "vi", page_size: int = 10) -> WwwCollections:
    return WwwCollections(default_locale=default_locale, page_size=page_size)
