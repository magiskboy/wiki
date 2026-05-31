"""Tiêu đề + slug + URL cho mỗi bài wiki.

pyssg mặc định lấy slug từ tên file và KHÔNG bỏ dấu tiếng Việt, nên URL sinh ra
sẽ chứa khoảng trắng/dấu. ``WikiMeta`` chạy trước ``Permalink`` (collect stage
-300 < -200) để gán sẵn ``url``/``output_path`` theo slug ASCII — khi đó
``Permalink._assign`` thấy URL đã có và bỏ qua.

Đồng thời:
- Tiêu đề lấy từ H1 đầu tiên trong body (wiki không có ``title`` ở frontmatter).
- File đặc biệt: ``_index`` → trang chủ ``/``; ``_tags``/``Tổng quan`` không
  build thành trang độc lập (loại khỏi ``build.sources``).

Quy tắc ``slugify`` kế thừa từ generator wiki_web cũ để slug khớp output cũ.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.content import OUTPUT_PATH, URL, is_generated, url_to_output_path
from pyssg.models import Source

# Stem các file KHÔNG build thành trang độc lập (ngoài _index = trang chủ).
SKIP_WIKI = {"_tags", "Tổng quan"}

FIRST_H1 = re.compile(r"^#\s+(.+)$", re.MULTILINE)

# WikiMeta phải chạy trước Permalink (collect stage -200).
_COLLECT_STAGE = -300


def slugify(title: str) -> str:
    """Convert title (có dấu tiếng Việt) sang ASCII slug cho URL.

    Kế thừa từ ``slugify`` của generator wiki_web cũ.
    """
    s = title.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def extract_title(body: str, fallback: str) -> str:
    match = FIRST_H1.search(body)
    if match:
        return match.group(1).strip()
    return fallback


def _is_external(source: Source) -> bool:
    return bool(source.meta.get("external_md"))


def _page_url(source: Source, title: str) -> tuple[str, str]:
    """Trả về (url, slug). Bài thường: phẳng ``/slug/`` (khớp web cũ).

    Ghi chú ngoài content (relpath bắt đầu bằng thư mục ngoài, vd
    ``references/interviews``): giữ tiền tố thư mục, slug từ tên file (đã ASCII).
    """
    stem = source.relpath.stem
    if stem == "_index":
        return "/", "_index"
    if _is_external(source):
        slug = slugify(stem)
        prefix = source.relpath.parent.as_posix()
        return f"/{prefix}/{slug}/", slug
    return f"/{slugify(title)}/", slugify(title)


class WikiMeta:
    """Gán tiêu đề/slug/URL cho mỗi source và dựng dữ liệu build dùng chung."""

    def __init__(self, *, repo_remotes_path: Path | str | None = None) -> None:
        self._repo_remotes_path = (
            Path(repo_remotes_path) if repo_remotes_path else None
        )

    def apply(self, builder: Builder) -> None:
        builder.hooks.collect.tap("WikiMeta", self._collect, stage=_COLLECT_STAGE)

    def _collect(self, build: Build) -> None:
        kept: list[Source] = []
        slug_index: dict[str, str] = {}
        for source in build.sources:
            if is_generated(source):
                kept.append(source)
                continue

            stem = source.relpath.stem
            if stem in SKIP_WIKI and not _is_external(source):
                continue

            title = extract_title(source.body, stem.replace("-", " ").title())
            source.frontmatter.setdefault("title", title)

            url, slug = _page_url(source, title)
            source.meta[URL] = url
            source.meta[OUTPUT_PATH] = url_to_output_path(url)
            source.meta["slug"] = slug
            # Key theo stem tên file (giống link trong markdown). Bài thường
            # ưu tiên hơn ghi chú ngoài nếu trùng tên (setdefault).
            slug_index.setdefault(stem, url)
            kept.append(source)

        build.sources[:] = kept
        build.meta["slug_index"] = slug_index
        build.meta["repo_remotes"] = self._load_repo_remotes()
        build.meta.setdefault("external_assets", set())

    def _load_repo_remotes(self) -> dict[str, dict[str, str]]:
        path = self._repo_remotes_path
        if not path or not path.exists():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"[warn] {path.name} không parse được: {exc}", file=sys.stderr)
            return {}
        return {
            k: v
            for k, v in raw.items()
            if not k.startswith("_") and isinstance(v, dict)
        }
