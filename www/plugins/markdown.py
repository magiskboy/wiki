"""WwwMarkdown: markdown → HTML cho blog (codehilite tách riêng qua plugin highlight).

Thay plugin ``markdown`` built-in vì site cần thêm ``arithmatex`` (bảo vệ công
thức ``$...$``/``$$...$$`` để KaTeX render client-side; plugin markdown lõi không
có extension này). Bộ extension còn lại giữ như built-in: ``fenced_code``,
``tables``, ``sane_lists``, ``toc`` (heading id dùng cùng ``slugify`` với core).

- ``load_node``: claim ``*.md`` → ``Document`` + ``meta["__raw__"]``.
- ``parse`` (stage 200): body → ``content_html``; suy ``title`` từ frontmatter/H1;
  bật cờ ``math`` khi có công thức; và tiền tính ``date_display`` + ``tag_links``
  theo locale (``meta["lang"]`` do i18n gán ở stage 150) để template chỉ việc in.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import markdown as md_lib
from markdown.extensions.toc import TocExtension
from pymdownx.arithmatex import ArithmatexExtension

from pyssg.core.node import Document
from pyssg.core.types import NodeKind
from pyssg.plugins.content_meta import slugify

from ._util import format_date, render_description, tag_links

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder
    from pyssg.core.node import Node

_PARSE_STAGE = 200
# Marker mà ArithmatexExtension(generic=True) ghi ra khi gặp công thức.
_MATH_MARKER = 'class="arithmatex"'


def _toc_slugify(value: str, _sep: str) -> str:
    return slugify(value)


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _first_heading(toc_tokens: object) -> str | None:
    if isinstance(toc_tokens, list) and toc_tokens:
        first = toc_tokens[0]
        if isinstance(first, dict):
            name = first.get("name")
            if isinstance(name, str) and name:
                return name
    return None


class WwwMarkdown:
    name = "markdown"
    cache_version = "2.0.0"

    def __init__(self, *, default_locale: str = "vi") -> None:
        self._default_locale = default_locale
        self._md = md_lib.Markdown(
            extensions=[
                "fenced_code",
                "tables",
                "sane_lists",
                ArithmatexExtension(generic=True, smart_dollar=True),
                TocExtension(slugify=_toc_slugify),
            ],
            output_format="html",
        )

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.load_node.tap(self.name)
            def _load(path: str) -> Node | None:
                if not path.endswith(".md"):
                    return None
                node = Document(id=path, kind=NodeKind.MARKDOWN, source_path=path)
                node.meta["__raw__"] = Path(path).read_text(encoding="utf-8")
                return node

            @build.hooks.parse.tap(self.name, stage=_PARSE_STAGE)
            def _parse(node: Node) -> None:
                if node.kind is not NodeKind.MARKDOWN or not isinstance(node, Document):
                    return
                body = node.meta.get("__body__")
                text = _text(body) if body is not None else _text(node.meta.get("__raw__"))

                self._md.reset()
                html = self._md.convert(text)
                raw_toc = getattr(self._md, "toc_tokens", [])
                node.ast = list(raw_toc) if isinstance(raw_toc, list) else []

                node.meta["content_html"] = html
                node.meta["__content_html_raw__"] = html

                existing = node.meta.get("title")
                if not (isinstance(existing, str) and existing):
                    heading = _first_heading(node.ast)
                    node.meta["title"] = heading or Path(node.source_path or node.id).stem

                if _MATH_MARKER in html:
                    node.meta["math"] = True

                # Tiền tính trường hiển thị theo locale cho template single.
                lang = node.meta.get("lang")
                locale = lang if isinstance(lang, str) and lang else self._default_locale
                node.meta["date_display"] = format_date(node.meta.get("date"), locale)
                node.meta["tag_links"] = tag_links(
                    node.meta.get("tags"), locale, self._default_locale
                )
                # Mô tả cũng là markdown → render để hiển thị giống nội dung
                # (RSS vẫn dùng ``description`` thô nên không đụng tới khóa đó).
                node.meta["description_html"] = render_description(node.meta.get("description"))


def wwwmarkdown(*, default_locale: str = "vi") -> WwwMarkdown:
    return WwwMarkdown(default_locale=default_locale)
