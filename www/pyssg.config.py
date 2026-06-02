"""Cấu hình pyssg cho blog nkthanh.dev (pyssg 0.1.0, API node/registry).

Blog đa ngôn ngữ: tiếng Việt (mặc định) ở gốc, tiếng Anh dưới ``/en/``. Bài viết
nằm ở ``content/<locale>/posts/*.md``. Dựng Config thủ công, ghép các plugin
built-in (directory_loader, frontmatter, i18n, content_meta, highlight, permalink,
sitemap, render) với plugin riêng của site trong ``plugins/`` để tái hiện đúng
giao diện và URL của site cũ (xem ``public/``).
"""

from __future__ import annotations

import sys
from pathlib import Path

from pyssg.config import Config
from pyssg.plugins import (
    content_meta,
    directory_loader,
    frontmatter,
    highlight,
    i18n,
    permalink,
    render,
    sitemap,
)

# Config được import theo đường dẫn nên thư mục của nó chưa nằm trên sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plugins import (  # noqa: E402
    HighlightThemes,
    Redirects,
    StaticFiles,
    WwwCollections,
    WwwMarkdown,
    WwwRss,
    WwwTaxonomy,
)

DEFAULT_LOCALE = "vi"
LOCALES = ("vi", "en")

CV_URL = "https://cv.nkthanh.dev"

# Slug tiếng Việt cũ vẫn phải resolve được sau khi migrate.
LEGACY_REDIRECTS = {
    "/posts/": "/",
    "/about/": CV_URL,
    "/en/about/": CV_URL,
    "/posts/bat-dong-bo-trong-python-phan-1-coroutine/": (
        "/posts/asynchronous-in-python-part-1/"
    ),
    "/posts/bat-dong-bo-trong-python-phan-2-coroutine/": (
        "/posts/asynchronous-in-python-part-2/"
    ),
}

SOCIALS = [
    {"title": "Github", "link": "https://github.com/magiskboy"},
    {"title": "LinkedIn", "link": "https://www.linkedin.com/in/thanh-nguyen-khac"},
    {"title": "Twitter", "link": "https://twitter.com/mag1skboy"},
]

NAVS = [
    {"title": "Bài viết", "link": "/"},
    {"title": "CV", "link": "https://cv.nkthanh.dev"},
    {"title": "Danh mục", "link": "/categories/"},
    {"title": "Thẻ", "link": "/tags/"},
]

config = Config(
    content_dir="content",
    output_dir="public",
    layout="layouts/theme",
    base_url="https://nkthanh.dev",
    site={
        "title": "Nguyễn Khắc Thành",
        "description": "Nguyễn Khắc Thành",
        "author": "Nguyễn Khắc Thành",
        "utterances_repo": "magiskboy/www",
        "socials": SOCIALS,
        "navs": NAVS,
    },
    plugins=[
        directory_loader(),
        frontmatter(),
        i18n(default_locale=DEFAULT_LOCALE, locales=LOCALES),
        WwwMarkdown(default_locale=DEFAULT_LOCALE),
        highlight(style="default"),
        content_meta(),
        HighlightThemes(),
        permalink(),
        WwwCollections(default_locale=DEFAULT_LOCALE, page_size=10),
        WwwTaxonomy(default_locale=DEFAULT_LOCALE),
        WwwRss(default_locale=DEFAULT_LOCALE, locales=LOCALES),
        sitemap(),
        Redirects(rules=LEGACY_REDIRECTS),
        StaticFiles(directory="static"),
        render(),
    ],
)
