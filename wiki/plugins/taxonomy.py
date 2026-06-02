"""WikiTaxonomy: trang tag, category và dashboard trang chủ.

Chạy ở ``evaluate_collections`` (sau WikiGraph để có ``link_counts``), tạo các
trang ảo khớp layout wiki:

- ``/tags/`` (tag cloud) + ``/tags/<tag>/`` (mỗi tag, xếp theo số liên kết)
- ``/categories/`` (bản đồ) + ``/categories/<slug>/`` (mỗi category)

Category suy từ thư mục cha của bài (taxonomy built-in chỉ đọc frontmatter).
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

from pyssg.core.node import Document, Page
from pyssg.core.types import NodeKind

from ._util import ascii_slug

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder

_COLLECT_STAGE = 10


def _font_size_rem(count: int, c_min: int, c_max: int) -> float:
    if c_max == c_min:
        return 1.15
    t = (count - c_min) / (c_max - c_min)
    return 0.85 + t * 1.4


def _slug_of(node: Document) -> str:
    return ascii_slug(Path(node.source_path or "").stem)


def _category_of(node: Document) -> str | None:
    parts = Path(node.source_path or "").parts
    return parts[0] if len(parts) > 1 else None


class WikiTaxonomy:
    name = "wiki_taxonomy"
    cache_version = "1.0.0"

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name, stage=_COLLECT_STAGE)
            def _eval(b: Build) -> None:
                self._collect(b)

    def _content(self, build: Build) -> list[Document]:
        out: list[Document] = []
        for node in build.graph.nodes():
            if not (isinstance(node, Document) and node.kind is NodeKind.MARKDOWN):
                continue
            if Path(node.source_path or "").stem == "index":
                continue
            out.append(node)
        return out

    def _link_counts(self, build: Build) -> dict[str, int]:
        raw = build.site_data.get("link_counts")
        return {str(k): int(v) for k, v in raw.items()} if isinstance(raw, dict) else {}

    def _rank(self, docs: list[Document], link_counts: dict[str, int]) -> list[dict[str, object]]:
        ordered = sorted(
            docs,
            key=lambda d: (
                -link_counts.get(_slug_of(d), 0),
                str(d.meta.get("title", "")).lower(),
            ),
        )
        return [
            {
                "rank": i,
                "title": d.meta.get("title", ""),
                "url": f"/{_slug_of(d)}/",
                "links": link_counts.get(_slug_of(d), 0),
            }
            for i, d in enumerate(ordered, start=1)
        ]

    def _add(self, build: Build, *, pid: str, url: str, template: str, meta: dict[str, object]) -> None:
        build.graph.add_node(
            Page(id=pid, kind=NodeKind.PAGE, url=url, template=template, meta=meta)
        )

    def _collect(self, build: Build) -> None:
        link_counts = self._link_counts(build)
        content = self._content(build)

        by_tag: dict[str, list[Document]] = defaultdict(list)
        by_cat: dict[str, list[Document]] = defaultdict(list)
        for d in content:
            raw_tags = d.meta.get("tags") or []
            for t in raw_tags if isinstance(raw_tags, list) else []:
                by_tag[str(t)].append(d)
            cat = _category_of(d)
            if cat:
                by_cat[cat].append(d)

        # --- per-tag pages ---
        for tag, docs in by_tag.items():
            self._add(
                build,
                pid=f"page:wiki:tag:{tag}",
                url=f"/tags/{tag}/",
                template="list.html.j2",
                meta={
                    "title": f"Tag: {tag}",
                    "count": len(docs),
                    "entries": self._rank(docs, link_counts),
                    "map_url": "/tags/",
                    "map_label": "Bản đồ tag",
                },
            )

        # --- tag cloud ---
        tag_counts = {t: len(v) for t, v in by_tag.items()}
        c_min = min(tag_counts.values()) if tag_counts else 0
        c_max = max(tag_counts.values()) if tag_counts else 0
        cloud = [
            {
                "tag": t,
                "count": c,
                "url": f"/tags/{t}/",
                "size": round(_font_size_rem(c, c_min, c_max), 3),
            }
            for t, c in sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))
        ]
        self._add(
            build,
            pid="page:wiki:tagcloud",
            url="/tags/",
            template="tag-cloud.html.j2",
            meta={"title": "Tags", "total": len(tag_counts), "cloud": cloud},
        )

        # --- per-category pages ---
        for name, docs in by_cat.items():
            self._add(
                build,
                pid=f"page:wiki:cat:{ascii_slug(name)}",
                url=f"/categories/{ascii_slug(name)}/",
                template="list.html.j2",
                meta={
                    "title": f"Category: {name}",
                    "count": len(docs),
                    "entries": self._rank(docs, link_counts),
                    "map_url": "/categories/",
                    "map_label": "Bản đồ category",
                },
            )

        # --- category map ---
        cards = [
            {"name": name, "url": f"/categories/{ascii_slug(name)}/", "count": len(v)}
            for name, v in sorted(by_cat.items(), key=lambda x: (-len(x[1]), x[0]))
        ]
        self._add(
            build,
            pid="page:wiki:catmap",
            url="/categories/",
            template="category-map.html.j2",
            meta={"title": "Bản đồ category", "total": len(by_cat), "cards": cards},
        )


def wiki_taxonomy() -> WikiTaxonomy:
    return WikiTaxonomy()
