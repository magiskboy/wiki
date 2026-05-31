"""pyssg configuration for the migrated nkthanh.dev blog.

The Next.js source (``contents/*.mdx``) was converted to plain Markdown under
``content/`` by ``migrate_mdx.py``. This builds it with the multilingual blog
preset: Vietnamese (default) at the root, English under ``/en/``.
"""

import sys
from pathlib import Path

from pyssg.config import Config
from pyssg_cli.presets import i18n_blog
from pyssg_plugins import Highlight, Redirects, StaticFiles, Statistics

# The config is imported by path, so its directory is not on sys.path yet.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plugins import (  # noqa: E402
    Categories,
    HighlightThemes,
    Math,
    TemplateHelpers,
)

# Old Vietnamese slugs that must keep resolving after the migration.
LEGACY_REDIRECTS = {
    "/posts/": "/",
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
]


def config() -> Config:
    plugins = i18n_blog(
        locales=("vi", "en"),
        default_locale="vi",
        posts_dir="posts",
        page_size=10,
        markdown_extensions=("fenced_code", "tables", "toc"),
        rss=True,
        sitemap=True,
        robots=True,
        seo=True,
        highlight=True,
    )
    # Code blocks were highlighted client-side by rehype-highlight; do it at
    # build time with Pygments instead. Highlight only emits the class markup;
    # HighlightThemes provides the per-theme colors scoped by data-theme.
    plugins.append(Highlight(dark_style=None))
    # Post images live under /images, copied verbatim (no build-time resizing).
    plugins.append(StaticFiles(directory="static"))
    # Site-local extensions: localized dates, KaTeX flag, category pages.
    plugins.append(TemplateHelpers())
    plugins.append(HighlightThemes())
    plugins.append(Math())
    plugins.append(Categories())
    plugins.append(Redirects(rules=LEGACY_REDIRECTS))
    plugins.append(Statistics())

    return Config(
        src=Path("content"),
        out=Path("public"),
        options={
            "title": "Nguyễn Khắc Thành",
            "base_url": "https://nkthanh.dev",
            "author": "Nguyễn Khắc Thành",
            "utterances_repo": "magiskboy/www",
            "socials": SOCIALS,
            "navs": NAVS,
        },
        plugins=plugins,
    )
