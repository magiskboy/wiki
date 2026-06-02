from __future__ import annotations

import sys
from pathlib import Path

from pyssg.config import Config
from pyssg.plugins import (
    asset_copy,
    directory_loader,
    frontmatter,
    link_resolver,
    permalink,
    render,
    rss,
    sitemap,
    transclude,
    wikilink,
)

# Config được import theo đường dẫn nên thư mục của nó chưa nằm trên sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plugins import (  # noqa: E402
    wiki_graph,
    wiki_home,
    wiki_markdown,
    wiki_slug,
    wiki_taxonomy,
)

config = Config(
    content_dir="content",
    output_dir="public",
    layout="layouts/theme",
    base_url="https://wiki.nkthanh.dev",
    site={"title": "Thanh's wiki", "description": "Kho tri thức cá nhân"},
    plugins=[
        directory_loader(exclude=["_tags.md"]),
        frontmatter(),
        wiki_markdown(),
        permalink(),
        wiki_slug(),
        wikilink(),
        link_resolver(),
        transclude(),
        wiki_graph(),
        wiki_taxonomy(),
        wiki_home(),
        sitemap(),
        rss(title="Thanh's wiki"),
        asset_copy(),
        render(),
    ],
)
