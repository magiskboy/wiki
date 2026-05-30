"""Copy static assets từ tools/wiki-web/assets/ sang web/assets/.

Build pipeline xoá toàn bộ web/assets/ trước khi copy lại — vì vậy nguồn
sự thật cho graph.js/style.css/app.js là `tools/wiki-web/assets/`, không
phải `web/assets/`.
"""

from __future__ import annotations

import shutil

from .config import ASSETS_SRC, WEB_DIR


def copy_assets() -> None:
    dest = WEB_DIR / "assets"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ASSETS_SRC, dest)
