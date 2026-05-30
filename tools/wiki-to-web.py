#!/usr/bin/env python3
"""
Chuyển toàn bộ markdown trong wiki/ sang HTML tĩnh trong web/.

Cách dùng:
  pip install -r tools/wiki-web-requirements.txt
  python tools/wiki-to-web.py

Host tĩnh (ví dụ):
  python -m http.server 8080 --directory web

Code build pipeline nằm trong package `wiki_web/` cùng thư mục.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from wiki_web.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
