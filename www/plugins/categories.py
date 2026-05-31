"""Taxonomy index and per-term listing pages (categories and tags).

URLs follow the locale-at-root scheme: ``/<segment>/`` and
``/<segment>/<slug>/`` for the default locale, ``/<locale>/<segment>/...``
otherwise. Pages are paired across locales by ``translation_key`` so the I18n
plugin builds their language switcher.

``Categories`` groups posts by their ``categories`` front-matter field and
emits both the ``/categories/`` index and a page per category. ``Tags`` emits
only the ``/tags/`` index; the per-tag ``/tags/<name>/`` listings already come
from the preset's built-in tag Listing. Both reuse the term-agnostic
``category*.html`` layouts.
"""

from __future__ import annotations

from pathlib import Path

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.content import (
    GENERATED,
    LOCALE,
    LOCALE_PREFIX,
    OUTPUT_PATH,
    TRANSLATION_KEY,
    URL,
    is_draft,
    is_generated,
    page_ref,
    url_to_output_path,
)
from pyssg.models import Source
from pyssg_plugins.collections import sort_pages
from pyssg_plugins.permalink import slugify


class Categories:
    def __init__(
        self,
        *,
        field: str = "categories",
        segment: str = "categories",
        index_title: str = "Danh mục",
        layout: str = "category.html",
        index_layout: str = "category-index.html",
        term_pages: bool = True,
    ):
        self._field = field
        self._segment = segment
        self._index_title = index_title
        self._layout = layout
        self._index_layout = index_layout
        # Whether to emit a listing page per term. Categories owns its term
        # pages; tags reuse the preset's built-in ``/tags/<name>/`` listings,
        # so Tags sets this False and only contributes the index.
        self._term_pages = term_pages

    def apply(self, builder: Builder) -> None:
        # After Permalink (-200) so posts already carry their URLs. The tap name
        # is per-segment so Categories and Tags register distinct hooks.
        builder.hooks.collect.tap(f"Taxonomy:{self._segment}", self._collect, stage=10)

    def _collect(self, build: Build) -> None:
        groups: dict[tuple[str, str], list[Source]] = {}
        prefixes: dict[str, str] = {}
        for source in build.sources:
            if is_generated(source) or is_draft(source):
                continue
            locale = str(source.meta.get(LOCALE, ""))
            prefixes.setdefault(locale, str(source.meta.get(LOCALE_PREFIX, "")))
            for name in _values(source.frontmatter.get(self._field)):
                groups.setdefault((locale, name), []).append(source)

        index: dict[str, list[tuple[str, str, int]]] = {}
        for (locale, name), posts in groups.items():
            prefix = prefixes.get(locale, "")
            slug = slugify(name)
            url = f"{_base(prefix)}{self._segment}/{slug}/"
            if self._term_pages:
                source = self._new_source(
                    build,
                    url=url,
                    title=name,
                    locale=locale,
                    prefix=prefix,
                    translation_key=f"/{self._segment}/{slug}/",
                    layout=self._layout,
                )
                source.meta["entries"] = [
                    page_ref(p) for p in sort_pages(posts, "date")
                ]
            index.setdefault(locale, []).append((name, url, len(posts)))

        for locale, items in index.items():
            prefix = prefixes.get(locale, "")
            entries = [
                {"name": name, "url": url, "count": count}
                for name, url, count in sorted(items)
            ]
            source = self._new_source(
                build,
                url=f"{_base(prefix)}{self._segment}/",
                title=self._index_title,
                locale=locale,
                prefix=prefix,
                translation_key=f"/{self._segment}/",
                layout=self._index_layout,
            )
            source.meta["entries"] = entries

    def _new_source(
        self,
        build: Build,
        *,
        url: str,
        title: str,
        locale: str,
        prefix: str,
        translation_key: str,
        layout: str,
    ) -> Source:
        output_path = url_to_output_path(url)
        source = Source(path=Path(output_path), relpath=Path(output_path))
        source.frontmatter = {"title": title, "layout": layout}
        source.meta[GENERATED] = True
        source.meta[URL] = url
        source.meta[OUTPUT_PATH] = output_path
        source.meta[LOCALE] = locale
        source.meta[LOCALE_PREFIX] = prefix
        source.meta[TRANSLATION_KEY] = translation_key
        build.sources.append(source)
        return source


class Tags(Categories):
    """The ``/tags/`` index, grouped by the ``tags`` field.

    The i18n_blog preset already emits the per-tag ``/tags/<name>/`` listings,
    so this only adds the index that links to them (``term_pages=False``).
    """

    def __init__(self) -> None:
        super().__init__(
            field="tags", segment="tags", index_title="Thẻ", term_pages=False
        )


def _values(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [value]
    return []


def _base(prefix: str) -> str:
    return "/" if prefix == "" else f"/{prefix}/"
