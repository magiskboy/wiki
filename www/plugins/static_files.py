"""StaticFiles: copy một thư mục tĩnh vào gốc output.

``asset_copy`` built-in chỉ copy ``assets/`` của layout sang ``/assets/...``. Site
này phục vụ ``/style.css``, ``/robots.txt`` và ``/images/...`` ở gốc (bài viết
tham chiếu ``/images/...``), nên cần copy nguyên ``static/`` ra gốc output.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder


def _needs_copy(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return True
    return src.read_bytes() != dst.read_bytes()


class StaticFiles:
    name = "static_files"
    cache_version = "1.0.0"

    def __init__(self, directory: str = "static") -> None:
        self._directory = directory

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name)
            def _eval(b: Build) -> None:
                self._copy(b)

    def _copy(self, build: Build) -> None:
        config = build.builder.config
        if config is None:
            return
        src_root = build.builder.site_dir / self._directory
        if not src_root.is_dir():
            return
        dest_root = build.builder.site_dir / config.output_dir
        for src in sorted(p for p in src_root.rglob("*") if p.is_file()):
            dst = dest_root / src.relative_to(src_root)
            if _needs_copy(src, dst):
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
