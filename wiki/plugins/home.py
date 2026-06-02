"""WikiHome: biến ``index.md`` thành dashboard trang chủ.

Chạy ở ``evaluate_collections`` (sau WikiGraph + WikiTaxonomy). Bơm dữ liệu
dashboard (top bài nhiều liên kết, thẻ category, thẻ tag, số đếm) vào ``meta``
của document ``index`` — vì với trang sinh-từ-document, render context đọc
``doc.meta`` (không phải ``page.meta``). Template ``index.html.j2`` được chọn qua
frontmatter ``template`` của ``content/index.md``.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

from pyssg.core.node import Document
from pyssg.core.types import NodeKind

from ._util import ascii_slug

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder

TOP_N = 10
_COLLECT_STAGE = 20


def _slug_of(node: Document) -> str:
    return ascii_slug(Path(node.source_path or "").stem)


def _category_of(node: Document) -> str | None:
    parts = Path(node.source_path or "").parts
    return parts[0] if len(parts) > 1 else None


class WikiHome:
    name = "wiki_home"
    cache_version = "1.0.0"

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name, stage=_COLLECT_STAGE)
            def _eval(b: Build) -> None:
                self._collect(b)

    def _collect(self, build: Build) -> None:
        home: Document | None = None
        content: list[Document] = []
        for node in build.graph.nodes():
            if not (isinstance(node, Document) and node.kind is NodeKind.MARKDOWN):
                continue
            if Path(node.source_path or "").stem == "index":
                home = node
                continue
            content.append(node)
        if home is None:
            return

        raw = build.site_data.get("link_counts")
        link_counts = {str(k): int(v) for k, v in raw.items()} if isinstance(raw, dict) else {}

        by_tag: dict[str, list[Document]] = defaultdict(list)
        by_cat: dict[str, list[Document]] = defaultdict(list)
        for d in content:
            raw_tags = d.meta.get("tags") or []
            for t in raw_tags if isinstance(raw_tags, list) else []:
                by_tag[str(t)].append(d)
            cat = _category_of(d)
            if cat:
                by_cat[cat].append(d)

        ordered = sorted(
            content,
            key=lambda d: (
                -link_counts.get(_slug_of(d), 0),
                str(d.meta.get("title", "")).lower(),
            ),
        )
        home.meta["top"] = [
            {
                "rank": i,
                "title": d.meta.get("title", ""),
                "url": f"/{_slug_of(d)}/",
                "links": link_counts.get(_slug_of(d), 0),
            }
            for i, d in enumerate(ordered[:TOP_N], start=1)
        ]
        home.meta["category_cards"] = [
            {"name": name, "url": f"/categories/{ascii_slug(name)}/", "count": len(v)}
            for name, v in sorted(by_cat.items(), key=lambda x: (-len(x[1]), x[0]))
        ]
        home.meta["tag_cards"] = [
            {"name": t, "url": f"/tags/{t}/", "count": len(v)}
            for t, v in sorted(by_tag.items(), key=lambda x: (-len(x[1]), x[0]))
        ]
        home.meta["counts"] = {
            "articles": len(content),
            "categories": len(by_cat),
            "tags": len(by_tag),
        }


def wiki_home() -> WikiHome:
    return WikiHome()
