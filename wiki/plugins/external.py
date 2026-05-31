"""Tài nguyên ngoài ``content/`` — đưa vào artifact để site tự chứa.

Hai việc:

- ``discover`` (stage 10, sau ReadFile): nạp các ghi chú ``.md`` ngoài content
  (vd ``references/interviews/``) làm Source — chúng đi qua đúng pipeline để
  render thành trang HTML ``/references/interviews/<slug>/``.
- ``emit`` (stage 100, sau WriteFile): copy các file nhị phân (pdf/ảnh…) mà bài
  viết tham chiếu — đã được ``rewrite_asset_links`` ghi nhận vào
  ``build.meta["external_assets"]`` — sang ``public/references/...``.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.models import Source

# external.py taps cùng stage với ReadFile.load (mặc định) nên Source thêm ở
# discover stage 10 vẫn được ReadFile.load đọc raw bình thường.
_DISCOVER_STAGE = 10
_EMIT_STAGE = 100


class ExternalSources:
    def __init__(
        self,
        *,
        md_dirs: list[tuple[Path, str]],
        asset_base: Path,
    ) -> None:
        # md_dirs: (thư mục .md trên đĩa, tiền tố relpath, vd "references/interviews")
        self._md_dirs = md_dirs
        self._asset_base = Path(asset_base)

    def apply(self, builder: Builder) -> None:
        builder.hooks.discover.tap(
            "ExternalSources", self._discover, stage=_DISCOVER_STAGE
        )
        builder.hooks.emit.tap("ExternalSources", self._copy_assets, stage=_EMIT_STAGE)

    def _discover(self, build: Build) -> None:
        for disk_dir, rel_prefix in self._md_dirs:
            disk_dir = Path(disk_dir)
            if not disk_dir.is_dir():
                continue
            for path in sorted(disk_dir.glob("*.md")):
                relpath = Path(rel_prefix) / path.name
                source = Source(path=path, relpath=relpath)
                source.meta["external_md"] = True
                build.sources.append(source)

    def _copy_assets(self, build: Build) -> None:
        assets = build.meta.get("external_assets")
        if not isinstance(assets, set) or not assets:
            return
        out = build.config.out
        for tail in sorted(assets):
            src = self._asset_base / tail
            if not src.is_file():
                continue
            dest = out / "references" / tail
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
