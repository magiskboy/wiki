"""Cấu hình pyssg cho Thanh's wiki.

Nội dung wiki (``content/*.md``, một thư mục mỗi category) được build thành site
tĩnh trong ``public/``. Pipeline lắp tay (không dùng preset) vì wiki cần:

- slug ASCII bỏ dấu tiếng Việt cho URL (``WikiMeta``),
- và sẽ thêm dần: rewrite link ``.md``/repo, math/mermaid, tag/category, đồ thị.

Layout Jinja2 nằm ở ``layouts/`` (pyssg phân giải theo ``src.parent/layouts``),
asset tĩnh ở ``static/`` được copy nguyên vào gốc site.
"""

import sys
from pathlib import Path

from pyssg.config import Config
from pyssg_plugins import (
    Frontmatter,
    Permalink,
    ReadFile,
    StaticFiles,
    Template,
    WriteFile,
)

# Config được pyssg import theo đường dẫn nên thư mục của nó chưa nằm trên
# sys.path — thêm vào để import package ``plugins`` cạnh file này.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plugins import (  # noqa: E402
    ExternalSources,
    WikiContent,
    WikiGraph,
    WikiGraphPage,
    WikiMeta,
    WikiTaxonomy,
)

# Tài nguyên ngoài content/ (sống ở gốc repo, cạnh thư mục wiki/).
REFERENCES_DIR = Path("../references")
REPO_REMOTES_PATH = Path("repo-remotes.json")

# Ghi chú .md ngoài content được build thành trang: (thư mục đĩa, tiền tố URL).
EXTERNAL_MD_DIRS = [
    (REFERENCES_DIR / "interviews", "references/interviews"),
]


def config() -> Config:
    plugins = [
        ReadFile(),
        ExternalSources(md_dirs=EXTERNAL_MD_DIRS, asset_base=REFERENCES_DIR),
        Frontmatter(),
        WikiContent(),
        WikiMeta(repo_remotes_path=REPO_REMOTES_PATH),
        WikiGraph(),
        WikiGraphPage(),
        WikiTaxonomy(),
        Permalink(),
        Template(directory="layouts"),
        WriteFile(clean=True),
        StaticFiles(directory="static", dest="assets"),
    ]

    return Config(
        src=Path("content"),
        out=Path("public"),
        options={
            "title": "Thanh's wiki",
            "description": "Kho tri thức cá nhân",
            "base_url": "https://wiki.nkthanh.dev",
            "author": "Nguyễn Khắc Thành",
        },
        plugins=plugins,
    )
