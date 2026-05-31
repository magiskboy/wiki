"""Trang tổng hợp: tag, category và dashboard trang chủ.

``WikiTaxonomy`` (collect, sau ``WikiGraph`` để có ``link_counts``) tạo các
synthetic source:

- ``/tags/`` (tag cloud) + ``/tags/<tag>/`` (mỗi tag, xếp theo số liên kết)
- ``/categories/`` (bản đồ) + ``/categories/<slug>/`` (mỗi category)
- biến trang chủ ``/`` (từ ``_index``) thành dashboard: top bài + thẻ cat/tag.

Theo pattern ``www/plugins/categories.py``: gán ``GENERATED``/``url``/``layout``,
truyền dữ liệu qua ``source.meta`` để layout Jinja render.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.content import GENERATED, OUTPUT_PATH, URL, is_generated, url_to_output_path
from pyssg.models import Source

from .meta import slugify

TOP_N = 10
# Sau WikiGraph (-100); trước render.
_COLLECT_STAGE = 10


def _font_size_rem(count: int, c_min: int, c_max: int) -> float:
    if c_max == c_min:
        return 1.15
    t = (count - c_min) / (c_max - c_min)
    return 0.85 + t * 1.4


def _category_of(source: Source) -> str | None:
    parts = source.relpath.parts
    return parts[0] if len(parts) > 1 else None


class WikiTaxonomy:
    def apply(self, builder: Builder) -> None:
        builder.hooks.collect.tap("WikiTaxonomy", self._collect, stage=_COLLECT_STAGE)

    def _content(self, build: Build) -> list[Source]:
        out = []
        for s in build.sources:
            if is_generated(s) or s.meta.get("external_md"):
                continue
            if s.relpath.stem == "_index":
                continue
            out.append(s)
        return out

    def _collect(self, build: Build) -> None:
        link_counts: dict[str, int] = build.meta.get("link_counts", {})  # type: ignore[assignment]
        content = self._content(build)

        by_tag: dict[str, list[Source]] = defaultdict(list)
        by_cat: dict[str, list[Source]] = defaultdict(list)
        for s in content:
            raw_tags = s.frontmatter.get("tags") or []
            for t in raw_tags if isinstance(raw_tags, list) else []:
                by_tag[str(t)].append(s)
            cat = _category_of(s)
            if cat:
                by_cat[cat].append(s)

        def rank(sources: list[Source]) -> list[dict[str, object]]:
            ordered = sorted(
                sources,
                key=lambda s: (
                    -link_counts.get(str(s.meta.get("slug")), 0),
                    str(s.frontmatter.get("title", "")).lower(),
                ),
            )
            return [
                {
                    "rank": i,
                    "title": s.frontmatter.get("title", ""),
                    "url": s.meta.get("url", ""),
                    "links": link_counts.get(str(s.meta.get("slug")), 0),
                }
                for i, s in enumerate(ordered, start=1)
            ]

        # --- per-tag pages ---
        for tag, sources in by_tag.items():
            page = self._synth(build, url=f"/tags/{tag}/", layout="list.html",
                               title=f"Tag: {tag}")
            page.meta["label"] = tag
            page.meta["count"] = len(sources)
            page.meta["entries"] = rank(sources)
            page.meta["map_url"] = "/tags/"
            page.meta["map_label"] = "Bản đồ tag"

        # --- tag cloud /tags/ ---
        tag_counts = {t: len(v) for t, v in by_tag.items()}
        cloud = self._synth(build, url="/tags/", layout="tag-cloud.html", title="Tags")
        cloud.meta["total"] = len(tag_counts)
        if tag_counts:
            c_min, c_max = min(tag_counts.values()), max(tag_counts.values())
        else:
            c_min = c_max = 0
        cloud.meta["cloud"] = [
            {
                "tag": t,
                "count": c,
                "url": f"/tags/{t}/",
                "size": round(_font_size_rem(c, c_min, c_max), 3),
            }
            for t, c in sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))
        ]

        # --- per-category pages ---
        for name, sources in by_cat.items():
            slug = slugify(name)
            page = self._synth(build, url=f"/categories/{slug}/", layout="list.html",
                               title=f"Category: {name}")
            page.meta["label"] = name
            page.meta["count"] = len(sources)
            page.meta["entries"] = rank(sources)
            page.meta["map_url"] = "/categories/"
            page.meta["map_label"] = "Bản đồ category"

        # --- category map /categories/ ---
        cat_counts = {c: len(v) for c, v in by_cat.items()}
        cmap = self._synth(build, url="/categories/", layout="category-map.html",
                          title="Bản đồ category")
        cmap.meta["total"] = len(cat_counts)
        cmap.meta["cards"] = [
            {"name": name, "url": f"/categories/{slugify(name)}/", "count": c}
            for name, c in sorted(cat_counts.items(), key=lambda x: (-x[1], x[0]))
        ]

        # --- home dashboard (trang chủ /) ---
        self._build_home(build, content, by_tag, by_cat, link_counts, rank)

    def _build_home(self, build, content, by_tag, by_cat, link_counts, rank) -> None:
        home = next(
            (s for s in build.sources if s.meta.get(URL) == "/"
             and s.relpath.stem == "_index"),
            None,
        )
        if home is None:
            return
        home.frontmatter["layout"] = "index.html"
        home.frontmatter.setdefault("title", "Mục lục tri thức")
        home.meta["top"] = rank(content)[:TOP_N]
        home.meta["category_cards"] = [
            {"name": name, "url": f"/categories/{slugify(name)}/", "count": len(v)}
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

    def _synth(self, build: Build, *, url: str, layout: str, title: str) -> Source:
        output_path = url_to_output_path(url)
        source = Source(path=Path(output_path), relpath=Path(output_path))
        source.frontmatter = {"title": title, "layout": layout}
        source.meta[GENERATED] = True
        source.meta[URL] = url
        source.meta[OUTPUT_PATH] = output_path
        build.sources.append(source)
        return source
