"""WwwRss: feed RSS 2.0 cho mỗi locale (``/feed.xml``, ``/en/feed.xml``).

Built-in ``rss`` chỉ phát một feed gộp mọi locale; site cũ tách feed theo ngôn
ngữ nên dùng plugin riêng. Mỗi feed gồm tối đa 20 bài mới nhất của locale đó với
``title``, ``link``, ``guid``, ``pubDate`` (RFC822) và ``description``.
"""

from __future__ import annotations

import datetime as dt
from collections import defaultdict
from email.utils import format_datetime
from typing import TYPE_CHECKING
from xml.sax.saxutils import escape

from pyssg.core.node import Document, Page
from pyssg.core.types import NodeKind

from ._util import base_path, date_sort_key

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder

_MAX_ITEMS = 20


def _pubdate(value: object) -> str:
    if isinstance(value, dt.datetime):
        d = value
    elif isinstance(value, dt.date):
        d = dt.datetime(value.year, value.month, value.day)
    elif isinstance(value, str):
        try:
            d = dt.datetime.fromisoformat(value[:10])
        except ValueError:
            return ""
    else:
        return ""
    return format_datetime(d.replace(tzinfo=dt.timezone.utc))


class WwwRss:
    name = "www_rss"
    cache_version = "1.0.0"

    def __init__(self, *, default_locale: str = "vi", locales: tuple[str, ...] = ("vi",)) -> None:
        self._default_locale = default_locale
        self._locales = locales

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name, after=("permalink",))
            def _eval(b: Build) -> None:
                self._build(b)

    def _build(self, build: Build) -> None:
        config = build.builder.config
        base_url = config.base_url if config is not None else ""
        title = ""
        if config is not None and isinstance(config.site.get("title"), str):
            title = str(config.site["title"])

        by_locale: dict[str, list[tuple[str, Document]]] = defaultdict(list)
        for node in build.graph.nodes():
            if not (isinstance(node, Page) and node.generated_from):
                continue
            doc = build.graph.get(node.generated_from[0])
            if not (isinstance(doc, Document) and doc.kind is NodeKind.MARKDOWN):
                continue
            if "/posts/" not in (doc.source_path or ""):
                continue
            lang = doc.meta.get("lang")
            locale = lang if isinstance(lang, str) and lang else self._default_locale
            by_locale[locale].append((node.url, doc))

        owned: set[str] = set()
        for locale in self._locales:
            posts = sorted(
                by_locale.get(locale, []),
                key=lambda pair: date_sort_key(pair[1].meta),
                reverse=True,
            )[:_MAX_ITEMS]
            prefix = base_path(locale, self._default_locale).rstrip("/")
            channel_link = f"{base_url}{prefix}"
            xml = self._render(title, channel_link, base_url, posts)
            url = f"{base_path(locale, self._default_locale)}feed.xml"
            pid = f"page:wwwrss:{locale}"
            owned.add(pid)
            meta = {"title": "RSS", "content_html": xml}
            existing = build.graph.get(pid)
            if isinstance(existing, Page):
                existing.url = url
                existing.template = None
                existing.meta = meta
            else:
                build.graph.add_node(
                    Page(id=pid, kind=NodeKind.PAGE, url=url, template=None, meta=meta)
                )

        for node in list(build.graph.nodes()):
            if node.id.startswith("page:wwwrss:") and node.id not in owned:
                build.graph.remove(node.id)

    def _render(
        self, title: str, channel_link: str, base_url: str, posts: list[tuple[str, Document]]
    ) -> str:
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            "  <channel>",
            f"    <title>{escape(title)}</title>",
            f"    <link>{escape(channel_link)}</link>",
            f"    <description>{escape(title)}</description>",
        ]
        for url, doc in posts:
            link = f"{base_url}{url}"
            desc = doc.meta.get("description") or doc.meta.get("excerpt") or ""
            pub = _pubdate(doc.meta.get("date"))
            lines.append("    <item>")
            lines.append(f"      <title>{escape(str(doc.meta.get('title') or url))}</title>")
            lines.append(f"      <link>{escape(link)}</link>")
            lines.append(f"      <guid>{escape(link)}</guid>")
            if pub:
                lines.append(f"      <pubDate>{escape(pub)}</pubDate>")
            lines.append(f"      <description>{escape(str(desc))}</description>")
            lines.append("    </item>")
        lines.append("  </channel>")
        lines.append("</rss>")
        return "\n".join(lines) + "\n"
