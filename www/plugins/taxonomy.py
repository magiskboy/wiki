"""WwwTaxonomy: trang tag và category theo locale.

Tái hiện site cũ: với mỗi locale tạo trang chỉ mục ``/tags/`` & ``/categories/``
(và ``/en/tags/`` ...), kèm trang liệt kê cho từng term ``/tags/<slug>/``,
``/categories/<slug>/``. Built-in ``taxonomy`` không phân biệt locale (gộp vi+en,
không có tiền tố ``/en/``) nên site dùng plugin riêng này.

Chạy ở ``evaluate_collections`` (sau permalink): lặp trên các bài đã publish, gom
theo (locale, term), rồi sinh Page ảo khớp template ``term*.html.j2``.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyssg.core.node import Document, Page
from pyssg.core.types import NodeKind
from pyssg.plugins.content_meta import slugify

from ._util import base_path, date_sort_key, locale_prefix, post_card

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder


@dataclass(frozen=True, slots=True)
class _Dim:
    """Một chiều phân loại."""

    field: str  # khóa frontmatter
    segment: str  # segment URL: "tags" | "categories"
    index_title: str  # tiêu đề trang chỉ mục
    is_tag: bool


_DIMS = (
    _Dim(field="tags", segment="tags", index_title="Thẻ", is_tag=True),
    _Dim(field="categories", segment="categories", index_title="Danh mục", is_tag=False),
)


def _as_str_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    return []


def _post_pages(build: Build) -> list[tuple[str, Document, str]]:
    """(url, doc, locale) cho mỗi bài viết đã publish."""
    out: list[tuple[str, Document, str]] = []
    for node in build.graph.nodes():
        if not (isinstance(node, Page) and node.generated_from):
            continue
        doc = build.graph.get(node.generated_from[0])
        if not (isinstance(doc, Document) and doc.kind is NodeKind.MARKDOWN):
            continue
        if "/posts/" not in (doc.source_path or ""):
            continue
        lang = doc.meta.get("lang")
        locale = lang if isinstance(lang, str) and lang else ""
        out.append((node.url, doc, locale))
    return out


class WwwTaxonomy:
    name = "www_taxonomy"
    cache_version = "1.0.0"

    def __init__(self, *, default_locale: str = "vi") -> None:
        self._default_locale = default_locale

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name, after=("permalink",))
            def _eval(b: Build) -> None:
                self._build(b)

    def _build(self, build: Build) -> None:
        pages = _post_pages(build)
        locales = sorted({loc for _, _, loc in pages if loc})
        owned: set[str] = set()
        for dim in _DIMS:
            owned |= self._build_dim(build, dim, pages, locales)

        for node in list(build.graph.nodes()):
            if node.id.startswith("page:wwwtax:") and node.id not in owned:
                build.graph.remove(node.id)

    def _build_dim(
        self,
        build: Build,
        dim: _Dim,
        pages: list[tuple[str, Document, str]],
        locales: list[str],
    ) -> set[str]:
        # Gom theo (locale, slug) chứ không theo term thô: các biến thể khác nhau
        # về hoa/thường ("Python" vs "python") cùng slug nên phải trộn vào một
        # trang, nếu không trang sinh sau sẽ ghi đè trang trước (cùng id) và mất
        # bài. Mỗi nhóm giữ số lần xuất hiện từng tên thô (để chọn tên hiển thị)
        # và bài viết khử trùng theo URL.
        groups: dict[tuple[str, str], dict[str, object]] = {}
        for url, doc, locale in pages:
            for term in _as_str_list(doc.meta.get(dim.field)):
                slug = slugify(term)
                if not slug:
                    continue
                g = groups.setdefault(
                    (locale, slug), {"names": defaultdict(int), "items": {}}
                )
                names = g["names"]
                names[term] += 1  # type: ignore[index]
                items = g["items"]
                items[url] = doc  # type: ignore[index]

        def _display_name(names: dict[str, int]) -> str:
            # Tên hay gặp nhất; hòa thì theo thứ tự chữ cái cho ổn định.
            return sorted(names.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

        slugs_by_locale: dict[str, set[str]] = defaultdict(set)
        for (locale, slug) in groups:
            slugs_by_locale[locale].add(slug)

        owned: set[str] = set()

        # --- trang liệt kê từng term ---
        for (locale, slug), g in groups.items():
            name = _display_name(g["names"])  # type: ignore[arg-type]
            items = g["items"]  # type: ignore[assignment]
            base = base_path(locale, self._default_locale)
            url = f"{base}{dim.segment}/{slug}/"
            posts = sorted(
                items.items(), key=lambda kv: date_sort_key(kv[1].meta), reverse=True
            )
            cards = [
                post_card(doc.meta, purl, locale, self._default_locale)
                for purl, doc in posts
            ]
            translations = [
                {
                    "lang": loc,
                    "url": f"{base_path(loc, self._default_locale)}{dim.segment}/{slug}/",
                    "active": loc == locale,
                }
                for loc in locales
                if slug in slugs_by_locale.get(loc, set())
            ]
            pid = f"page:wwwtax:{dim.segment}:{locale}:{slug}"
            owned.add(pid)
            self._set_page(
                build,
                pid,
                url,
                "termlist.html.j2",
                {
                    "title": name,
                    "lang": locale,
                    "locale_prefix": locale_prefix(locale, self._default_locale),
                    "is_tag": dim.is_tag,
                    "count": len(cards),
                    "entries": cards,
                    "translations": translations,
                },
            )

        # --- trang chỉ mục mỗi locale ---
        index: dict[str, list[dict[str, object]]] = defaultdict(list)
        for (locale, slug), g in groups.items():
            name = _display_name(g["names"])  # type: ignore[arg-type]
            base = base_path(locale, self._default_locale)
            index[locale].append(
                {
                    "name": name,
                    "url": f"{base}{dim.segment}/{slug}/",
                    "count": len(g["items"]),  # type: ignore[arg-type]
                }
            )
        for locale in locales:
            base = base_path(locale, self._default_locale)
            entries = sorted(index.get(locale, []), key=lambda e: str(e["name"]).lower())
            translations = [
                {
                    "lang": loc,
                    "url": f"{base_path(loc, self._default_locale)}{dim.segment}/",
                    "active": loc == locale,
                }
                for loc in locales
            ]
            pid = f"page:wwwtax:{dim.segment}:{locale}:__index__"
            owned.add(pid)
            self._set_page(
                build,
                pid,
                f"{base}{dim.segment}/",
                "termindex.html.j2",
                {
                    "title": dim.index_title,
                    "lang": locale,
                    "locale_prefix": locale_prefix(locale, self._default_locale),
                    "entries": entries,
                    "translations": translations,
                },
            )
        return owned

    @staticmethod
    def _set_page(
        build: Build, pid: str, url: str, template: str, meta: dict[str, object]
    ) -> None:
        existing = build.graph.get(pid)
        if isinstance(existing, Page):
            existing.url = url
            existing.template = template
            existing.meta = meta
        else:
            build.graph.add_node(
                Page(id=pid, kind=NodeKind.PAGE, url=url, template=template, meta=meta)
            )


def www_taxonomy(*, default_locale: str = "vi") -> WwwTaxonomy:
    return WwwTaxonomy(default_locale=default_locale)
