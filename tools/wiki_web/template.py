"""Helpers cho 2 lớp template (đều nằm trong `wiki_web/templates/`):

- `page.html` (wrapper toàn trang) — substitute qua `render_page`.
- Body template `<page-type>.html` — substitute qua `render_body_template`.
  Body được render TRƯỚC, kết quả dùng làm giá trị của `{content}` khi gọi
  render_page.
"""

from __future__ import annotations

import html
from functools import lru_cache

from .config import PAGE_TEMPLATE_PATH, TEMPLATES_DIR


@lru_cache(maxsize=None)
def main_template() -> str:
    return PAGE_TEMPLATE_PATH.read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def _read_body_template(name: str) -> str:
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


def render_body_template(name: str, **vars: str) -> str:
    """Render body template — giá trị KHÔNG được escape (vì chúng là HTML đã sẵn).

    Người gọi tự lo escape phần text user-supplied trước khi truyền vào.
    """
    text = _read_body_template(name)
    for k, v in vars.items():
        text = text.replace("{" + k + "}", v)
    return text


def render_page(
    *,
    title: str,
    description: str,
    content: str,
    root: str = "",
    main_class: str = "",
    extra_scripts: str = "",
) -> str:
    """Bọc content (đã là HTML) vào template.html toàn trang.

    title/description được escape; content/root/main_class/extra_scripts là
    HTML thô và không escape.
    """
    return (
        main_template()
        .replace("{title}", html.escape(title))
        .replace("{description}", html.escape(description))
        .replace("{content}", content)
        .replace("{root}", root)
        .replace("{main_class}", main_class)
        .replace("{extra_scripts}", extra_scripts)
    )
