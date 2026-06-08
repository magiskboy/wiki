"""Cấu hình pyssg cho blog nkthanh.dev (pyssg 0.2.0, API node/registry).

Blog đa ngôn ngữ: tiếng Việt (mặc định) ở gốc, tiếng Anh dưới ``/en/``. Bài viết
nằm ở ``content/<locale>/posts/*.md``.

0.2.0 lo phần lớn bằng plugin built-in:

- ``markdown(extensions=[arithmatex])`` -- bộ extension không còn đóng cứng.
- ``collections`` / ``taxonomy`` / ``rss`` -- đều i18n-aware (sinh trang theo
  từng locale, tách feed ``/feed.xml`` + ``/en/feed.xml``).
- ``redirects`` / ``asset_copy(mounts=...)`` -- chuyển hướng URL cũ và copy
  ``static/`` ra gốc, đều built-in.

Plugin riêng chỉ còn ``WwwEnrich`` + ``WwwCollections`` (tiền tính trường hiển
thị đã địa phương hoá) và ``HighlightThemes`` (CSS code đa ``data-theme``).
"""

from __future__ import annotations

import sys
from pathlib import Path

from pymdownx.arithmatex import ArithmatexExtension

from pyssg.config import Config
from pyssg.plugins import (
    CollectionSpec,
    Pagination,
    asset_copy,
    content_meta,
    directory_loader,
    frontmatter,
    highlight,
    i18n,
    markdown,
    permalink,
    redirects,
    render,
    rss,
    sitemap,
    taxonomy,
)

# Config được import theo đường dẫn nên thư mục của nó chưa nằm trên sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plugins import (  # noqa: E402
    HighlightThemes,
    ObsidianImages,
    WwwCollections,
    WwwEnrich,
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

# Danh sách bài: lọc theo ``section == "posts"`` (đã strip tiền tố ``/en/``),
# mới nhất trước, phân trang tại gốc mỗi locale (``/`` + ``/page/N/``).
POSTS = CollectionSpec(
    name="posts",
    select=lambda item: item.section == "posts",
    sort_key=lambda item: item.date,
    reverse=True,
    pagination=Pagination(size=10, route="/", template="list.html.j2"),
    title="Nguyễn Khắc Thành",
)

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
        "default_locale": DEFAULT_LOCALE,
    },
    plugins=[
        directory_loader(),
        frontmatter(),
        i18n(default_locale=DEFAULT_LOCALE, locales=LOCALES),
        markdown(extensions=[ArithmatexExtension(generic=True, smart_dollar=True)]),
        highlight(style="default"),
        content_meta(),
        # Ảnh kiểu Obsidian (![[...]] và src tên-trần) -> URL thật; cùng mount
        # với asset_copy bên dưới (static -> /).
        ObsidianImages(mounts=(("static", "/"),)),
        WwwEnrich(default_locale=DEFAULT_LOCALE),
        HighlightThemes(),
        permalink(),
        WwwCollections(POSTS, default_locale=DEFAULT_LOCALE),
        taxonomy(),
        rss(),
        redirects(rules=LEGACY_REDIRECTS),
        sitemap(),
        asset_copy(mounts=[("static", "/")]),
        render(),
    ],
)
