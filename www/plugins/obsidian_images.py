"""ObsidianImages: nhúng ảnh kiểu Obsidian cho blog.

Obsidian phân giải ảnh theo *tên file*, bất kể nó nằm ở thư mục nào trong vault.
Khi xuất sang web, đường dẫn trần đó không còn đúng: trang ``/posts/x/`` mà tham
chiếu ``anh.png`` thì trình duyệt đi tìm ``/posts/x/anh.png`` -> 404. Plugin này
tái lập hành vi Obsidian ngay trên HTML đã render:

- ``![[anh.png]]`` / ``![[anh.png|chú thích]]`` / ``![[anh.png|300]]`` (cú pháp
  wikilink-embed của Obsidian, Python-Markdown để nguyên thành text) -> ``<img>``.
- ``![alt](anh.png)`` -> Markdown đã sinh ``<img src="anh.png">``; ta viết lại
  ``src`` tên-trần (hoặc đường dẫn tương đối không phân giải được) về URL thật.

Ảnh được phân giải qua *cùng các mount của* ``asset_copy`` (mặc định
``static`` -> ``/``): quét cây thư mục nguồn, lập chỉ mục ``tên file`` (và đường
dẫn tương đối) -> URL phục vụ. Khớp chính xác trước, rồi fallback không phân biệt
hoa thường. Không tìm thấy thì giữ nguyên (không bịa ``src`` sai, lỗi vẫn lộ rõ).

Chạy ở tap ``finalize_content`` (sau khi Markdown đã render), khớp với cách
``wikilink`` built-in xử lý ``[[...]]``. Chỉ động tới ảnh; ``![[note]]`` (nhúng
tài liệu) không phải ảnh thì để yên.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder
    from pyssg.core.node import Document

# Phần mở rộng được coi là ảnh (Obsidian embed chỉ thành <img> với các đuôi này).
_IMAGE_EXTS = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".bmp", ".ico"}
)

# ![[target]] / ![[target|opt]] / ![[target|opt|opt]] -- embed kiểu Obsidian.
_EMBED = re.compile(r"!\[\[([^\]]+?)\]\]")
# Thẻ <img ... src="..." ...> do Markdown sinh ra cho ![alt](src).
_IMG_TAG = re.compile(r"<img\b([^>]*?)\bsrc=\"([^\"]*)\"([^>]*)>")
# Kích thước Obsidian: "300" hoặc "300x200".
_SIZE = re.compile(r"^(\d+)(?:x(\d+))?$")

_INDEX_KEY = "__obsidian_image_index__"
# Mount mặc định: trùng asset_copy(mounts=[("static", "/")]) trong config.
_DEFAULT_MOUNTS = (("static", "/"),)


def _is_external(src: str) -> bool:
    """True nếu ``src`` đã là URL/đường dẫn tuyệt đối -> không cần phân giải."""
    if not src:
        return True
    if src[0] in "/#?":
        return True
    if src.startswith("//") or src.startswith("data:"):
        return True
    # scheme:... (http:, https:, mailto:, ...)
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", src))


def _url_for(dest: str, rel_posix: str) -> str:
    """Ghép ``dest`` (URL gốc của mount) với đường dẫn tương đối -> URL phục vụ."""
    base = "/" + dest.strip("/")
    base = "" if base == "/" else base
    return f"{base}/" + quote(rel_posix)


def _build_index(build: Build, mounts: tuple[tuple[str, str], ...]) -> dict[str, str]:
    """Lập chỉ mục khóa-tra-cứu -> URL ảnh, một lần mỗi build (cache site_data).

    Mỗi ảnh được đăng ký dưới nhiều khóa: đường dẫn tương đối (so với gốc mount),
    tên file, và bản lowercase của cả hai. Khóa chính xác được ưu tiên qua thứ tự
    chèn; bản thường (lowercase) chỉ điền nếu chưa có để không đè khóa chính xác.
    """
    cached = build.site_data.get(_INDEX_KEY)
    if isinstance(cached, dict):
        return cached

    site_dir: Path = build.builder.site_dir
    index: dict[str, str] = {}

    def add(key: str, url: str) -> None:
        index.setdefault(key, url)

    for source, dest in mounts:
        root = Path(source)
        if not root.is_absolute():
            root = site_dir / root
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in _IMAGE_EXTS:
                continue
            rel = path.relative_to(root).as_posix()
            url = _url_for(dest, rel)
            add(rel, url)
            add(path.name, url)
    # Lượt hai: khóa lowercase (fallback), không đè khóa chính xác đã có.
    for key in list(index):
        add(key.lower(), index[key])

    build.site_data[_INDEX_KEY] = index
    return index


def _resolve(index: dict[str, str], target: str) -> str | None:
    """Phân giải tên/đường dẫn ảnh -> URL; thử chính xác rồi lowercase."""
    target = target.strip().lstrip("/")
    for key in (target, Path(target).name):
        if key in index:
            return index[key]
    for key in (target.lower(), Path(target).name.lower()):
        if key in index:
            return index[key]
    return None


def _img_tag(url: str, *, alt: str = "", width: str = "", height: str = "") -> str:
    attrs = [f'src="{url}"', f'alt="{alt}"']
    if width:
        attrs.append(f'width="{width}"')
    if height:
        attrs.append(f'height="{height}"')
    return "<img " + " ".join(attrs) + ">"


def _rewrite_embeds(html: str, index: dict[str, str]) -> str:
    """``![[anh.png|alt|size]]`` -> ``<img>`` (chỉ với target là ảnh)."""

    def repl(match: re.Match[str]) -> str:
        parts = [p.strip() for p in match.group(1).split("|")]
        target = parts[0]
        if Path(target).suffix.lower() not in _IMAGE_EXTS:
            return match.group(0)  # không phải ảnh -> để nguyên
        url = _resolve(index, target)
        if url is None:
            return match.group(0)  # không phân giải được -> giữ lại, lỗi lộ rõ
        alt, width, height = "", "", ""
        for opt in parts[1:]:
            size = _SIZE.match(opt)
            if size:
                width, height = size.group(1), size.group(2) or ""
            else:
                alt = opt
        return _img_tag(url, alt=alt, width=width, height=height)

    return _EMBED.sub(repl, html)


def _rewrite_img_src(html: str, index: dict[str, str]) -> str:
    """Viết lại ``src`` tên-trần trong ``<img>`` do ``![alt](anh.png)`` sinh ra."""

    def repl(match: re.Match[str]) -> str:
        pre, src, post = match.group(1), match.group(2), match.group(3)
        if _is_external(src):
            return match.group(0)
        url = _resolve(index, src)
        if url is None:
            return match.group(0)
        return f'<img{pre}src="{url}"{post}>'

    return _IMG_TAG.sub(repl, html)


class ObsidianImages:
    """Phân giải ảnh kiểu Obsidian (``![[...]]`` và ``src`` tên-trần)."""

    name = "obsidian_images"
    cache_version = "1.0.0"

    def __init__(
        self, *, mounts: tuple[tuple[str, str], ...] = _DEFAULT_MOUNTS
    ) -> None:
        self._mounts = mounts

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.finalize_content.tap(self.name, stage=150)
            def _rewrite(html: str, doc: Document) -> str:
                index = _build_index(build, self._mounts)
                html = _rewrite_embeds(html, index)
                return _rewrite_img_src(html, index)


def obsidian_images(
    *, mounts: tuple[tuple[str, str], ...] = _DEFAULT_MOUNTS
) -> ObsidianImages:
    """Factory dùng trong ``pyssg.config.py``."""
    return ObsidianImages(mounts=mounts)
