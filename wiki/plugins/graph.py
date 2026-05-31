"""Dữ liệu đồ thị tri thức từ section ``Liên kết tri thức``.

``WikiGraph`` (collect, sau WikiMeta) parse các bullet link trong mục
``Liên kết tri thức`` của từng bài, dựng:

- ``build.meta["graph_data"]`` = {nodes, edges} (cho trang ``/graph/`` ở Phase 4)
- ``build.meta["link_counts"]`` = {slug: bậc liên kết} (cho xếp hạng index/tag/category)

Port từ generator wiki_web cũ (đã gỡ); node id = slug (đã ASCII), url = pretty URL.
"""

from __future__ import annotations

import json
import re
import urllib.parse
from collections import defaultdict
from pathlib import Path

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.content import GENERATED, OUTPUT_PATH, URL, is_generated, url_to_output_path
from pyssg.models import Output, Source

from .meta import slugify

# Tag thuộc nhóm "cá nhân" — node mà mọi tag đều thuộc set này → group personal.
PERSONAL_TAGS = {"mindset", "career", "learning", "philosophy", "finance"}

LINK_HEADING_RE = re.compile(r"(?m)^#+\s*[^\n]*Liên kết[^\n]*$")
BULLET_LINK_RE = re.compile(r"^\s*[-*]\s+\[([^\]]*)\]\(([^)]+)\)(.*)$")

# WikiGraph chạy sau WikiMeta (-300) để có slug; trước taxonomy (10).
_COLLECT_STAGE = -100


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


class WikiGraph:
    def apply(self, builder: Builder) -> None:
        builder.hooks.collect.tap("WikiGraph", self._collect, stage=_COLLECT_STAGE)

    def _content_sources(self, build: Build) -> list[Source]:
        out = []
        for s in build.sources:
            if is_generated(s) or s.meta.get("external_md"):
                continue
            if s.relpath.stem == "_index":
                continue
            out.append(s)
        return out

    def _collect(self, build: Build) -> None:
        sources = self._content_sources(build)
        slug_by_stem: dict[str, str] = {}
        title_by: dict[str, str] = {}
        tags_by: dict[str, list[str]] = {}
        url_by: dict[str, str] = {}
        for s in sources:
            slug = str(s.meta.get("slug", ""))
            slug_by_stem[s.relpath.stem] = slug
            title_by[slug] = str(s.frontmatter.get("title", slug))
            raw_tags = s.frontmatter.get("tags") or []
            tags_by[slug] = [str(t) for t in raw_tags] if isinstance(raw_tags, list) else []
            url_by[slug] = str(s.meta.get("url", f"/{slug}/"))

        slugs = set(slug_by_stem.values())

        # key: (sorted_a, sorted_b) -> list of (direction, reason)
        pairs: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
        for s in sources:
            slug = str(s.meta.get("slug", ""))
            sec = _link_section(s.body)
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
                    "url": url_by.get(slug, f"/{slug}/"),
                    "tags": tags,
                    "group": group,
                    "degree": node_deg.get(slug, 0),
                }
            )

        build.meta["graph_data"] = {"nodes": nodes, "edges": edges}
        build.meta["link_counts"] = {n["id"]: n["degree"] for n in nodes}


class WikiGraphPage:
    """Trang trực quan ``/graph/`` + file ``/assets/graph.json``.

    - ``collect`` (sau WikiGraph): tạo synthetic source ``/graph/`` (layout
      ``graph.html``), nhúng dữ liệu inline qua ``page.graph_json`` — đúng cách
      ``graph.js`` ưu tiên đọc (``<script id="graph-data">``).
    - ``generate``: ghi ``/assets/graph.json`` làm artifact độc lập.

    Tái dùng ``graph.js`` nguyên bản; chỉ cần ``window.KB_ROOT=""`` để href node
    (pretty ``/slug/``) resolve đúng.
    """

    # Sau WikiGraph (-100) để có graph_data.
    _COLLECT_STAGE = 20

    def apply(self, builder: Builder) -> None:
        builder.hooks.collect.tap("WikiGraphPage", self._page, stage=self._COLLECT_STAGE)
        builder.hooks.generate.tap("WikiGraphPage", self._json)

    def _data(self, build: Build) -> dict:
        data = build.meta.get("graph_data")
        return data if isinstance(data, dict) else {"nodes": [], "edges": []}

    def _page(self, build: Build) -> None:
        blob = json.dumps(self._data(build), ensure_ascii=False).replace("<", "\\u003c")
        url = "/graph/"
        output_path = url_to_output_path(url)
        source = Source(path=Path(output_path), relpath=Path(output_path))
        source.frontmatter = {"title": "Đồ thị tri thức", "layout": "graph.html"}
        source.meta[GENERATED] = True
        source.meta[URL] = url
        source.meta[OUTPUT_PATH] = output_path
        source.meta["graph_json"] = blob
        source.meta["description"] = "Trực quan hóa mạng liên kết giữa các tri thức"
        build.sources.append(source)

    def _json(self, build: Build) -> None:
        content = json.dumps(self._data(build), ensure_ascii=False, indent=0)
        build.outputs.append(Output(path=Path("assets/graph.json"), content=content))
