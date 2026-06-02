"""WikiGraph: đồ thị tri thức từ mục "Liên kết tri thức" của mỗi bài.

Chạy ở ``evaluate_collections``: parse các bullet link trong mục "Liên kết tri
thức", dựng ``{nodes, edges}`` và ``link_counts`` (bậc liên kết theo slug) lưu vào
``build.site_data`` để index/taxonomy xếp hạng, đồng thời tạo trang ảo ``/graph/``
(layout ``graph.html.j2``) nhúng dữ liệu inline cho ``graph.js``.

Port từ generator wiki cũ; node id = slug ASCII, url = ``/slug/``.
"""

from __future__ import annotations

import json
import re
import urllib.parse
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

from pyssg.core.node import Document, Page
from pyssg.core.types import NodeKind

from ._util import ascii_slug

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder

PERSONAL_TAGS = {"mindset", "career", "learning", "philosophy", "finance"}

LINK_HEADING_RE = re.compile(r"(?m)^#+\s*[^\n]*Liên kết[^\n]*$")
BULLET_LINK_RE = re.compile(r"^\s*[-*]\s+\[([^\]]*)\]\(([^)]+)\)(.*)$")

_COLLECT_STAGE = 0


def _link_section(txt: str) -> str | None:
    m = LINK_HEADING_RE.search(txt)
    if not m:
        return None
    tail = txt[m.end():]
    nxt = re.search(r"(?m)^#+\s", tail)
    return tail[: nxt.start()] if nxt else tail


def _reason(label: str, trailing: str = "") -> str:
    trailing = trailing.strip()
    if trailing.startswith("-"):
        trailing = trailing[1:].strip()
        if trailing:
            return trailing
    parts = label.split(" - ", 1)
    return parts[1].strip() if len(parts) == 2 else label.strip()


def _target_stem(target: str) -> str:
    base = target.rsplit("/", 1)[-1].split("#")[0]
    stem_encoded = re.sub(r"\.md$", "", base, flags=re.IGNORECASE)
    return urllib.parse.unquote(stem_encoded)


def _body(node: Document) -> str:
    body = node.meta.get("__body__")
    if isinstance(body, str):
        return body
    raw = node.meta.get("__raw__")
    return raw if isinstance(raw, str) else ""


class WikiGraph:
    name = "wiki_graph"
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

    def _collect(self, build: Build) -> None:
        sources = self._content(build)
        slug_by_stem: dict[str, str] = {}
        title_by: dict[str, str] = {}
        tags_by: dict[str, list[str]] = {}
        for node in sources:
            stem = Path(node.source_path or "").stem
            slug = ascii_slug(stem)
            slug_by_stem[stem] = slug
            title_by[slug] = str(node.meta.get("title", slug))
            raw_tags = node.meta.get("tags") or []
            tags_by[slug] = [str(t) for t in raw_tags] if isinstance(raw_tags, list) else []

        slugs = set(slug_by_stem.values())

        pairs: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
        for node in sources:
            slug = slug_by_stem[Path(node.source_path or "").stem]
            sec = _link_section(_body(node))
            if not sec:
                continue
            for line in sec.splitlines():
                m = BULLET_LINK_RE.match(line)
                if not m:
                    continue
                tgt = slug_by_stem.get(_target_stem(m.group(2)))
                if tgt and tgt in slugs and tgt != slug:
                    a, b = sorted((slug, tgt))
                    direction = "fwd" if slug == a else "bwd"
                    pairs[(a, b)].append((direction, _reason(m.group(1), m.group(3))))

        node_deg: dict[str, int] = defaultdict(int)
        edges = []
        for (a, b), items in pairs.items():
            dirs = {d for d, _ in items}
            labels = sorted({r for _, r in items})
            if dirs == {"bwd"}:
                src, dst, bidi = b, a, False
            elif dirs == {"fwd"}:
                src, dst, bidi = a, b, False
            else:
                src, dst, bidi = a, b, True
            edges.append(
                {"source": src, "target": dst, "labels": labels, "bidirectional": bidi}
            )
            node_deg[src] += 1
            node_deg[dst] += 1

        nodes = []
        for slug in sorted(slugs):
            tags = tags_by.get(slug, [])
            group = (
                "personal"
                if tags and all(t in PERSONAL_TAGS for t in tags)
                else "tech"
            )
            nodes.append(
                {
                    "id": slug,
                    "title": title_by.get(slug, slug),
                    "url": f"/{slug}/",
                    "tags": tags,
                    "group": group,
                    "degree": node_deg.get(slug, 0),
                }
            )

        graph_data = {"nodes": nodes, "edges": edges}
        build.site_data["graph_data"] = graph_data
        build.site_data["link_counts"] = {n["id"]: n["degree"] for n in nodes}

        blob = json.dumps(graph_data, ensure_ascii=False).replace("<", "\\u003c")
        build.graph.add_node(
            Page(
                id="page:wiki:graph",
                kind=NodeKind.PAGE,
                url="/graph/",
                template="graph.html.j2",
                meta={
                    "title": "Đồ thị tri thức",
                    "description": "Trực quan hóa mạng liên kết giữa các tri thức",
                    "graph_json": blob,
                },
            )
        )


def wiki_graph() -> WikiGraph:
    return WikiGraph()
