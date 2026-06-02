"""WikiMarkdown: markdown → HTML với độ trung thực như generator wiki cũ.

Thay 3 plugin built-in ``markdown`` + ``highlight`` + ``mermaid`` của pyssg vì
wiki cần đúng bộ extension cũ: ``codehilite`` (class ``codehilite`` đã có CSS
trong style.css), ``arithmatex`` (bảo vệ LaTeX để KaTeX render client-side),
mermaid fence → ``<pre class="mermaid">``, cùng hậu xử lý ``normalize_article_html``
và rewrite link repo → URL GitHub/GitLab.

- ``load_node``: claim ``*.md`` → ``Document`` + ``meta["__raw__"]`` (frontmatter
  plugin built-in tách YAML và đặt ``__body__`` ở parse stage 100).
- ``parse`` (stage 200): body → ``content_html`` (+ bản ``__content_html_raw__``
  cho link_resolver), ``title`` lấy từ H1 đầu, cờ ``math`` khi có công thức.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

import markdown as md_lib
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from pymdownx.arithmatex import ArithmatexExtension

from pyssg.core.node import Document
from pyssg.core.types import NodeKind
from pyssg.plugins.content_meta import slugify as heading_slug

from ._util import mermaid_to_divs, normalize_article_html, rewrite_repo_links

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder
    from pyssg.core.node import Node

_PARSE_STAGE = 200
# Marker mà ArithmatexExtension(generic=True) ghi ra khi gặp math.
_MATH_MARKER = 'class="arithmatex"'
_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _toc_slugify(value: str, _sep: str) -> str:
    """Adapter để toc extension dùng cùng slugify với link_resolver (fragment)."""
    return heading_slug(value)


def make_md_processor() -> md_lib.Markdown:
    return md_lib.Markdown(
        extensions=[
            "sane_lists",
            "smarty",
            TableExtension(),
            FencedCodeExtension(),
            CodeHiliteExtension(
                css_class="codehilite",
                guess_lang=True,
                linenums=False,
            ),
            ArithmatexExtension(generic=True, smart_dollar=True),
            TocExtension(slugify=_toc_slugify),
        ],
        output_format="html5",
    )


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


def _derive_title(node: Document, toc_tokens: object, body: str) -> str:
    existing = node.meta.get("title")
    if isinstance(existing, str) and existing:
        return existing
    heading = _first_heading(toc_tokens)
    if heading:
        return heading
    m = _H1_RE.search(body)
    if m:
        return m.group(1).strip()
    return Path(node.source_path).stem if node.source_path else node.id


class WikiMarkdown:
    name = "wiki_markdown"
    cache_version = "1.0.0"

    def __init__(self, *, repo_remotes_path: str | Path | None = None) -> None:
        self._processor = make_md_processor()
        self._repo_remotes_path = repo_remotes_path
        self._remotes: dict[str, dict[str, str]] = {}

    def apply(self, builder: Builder) -> None:
        self._remotes = self._load_remotes(builder)

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

                prepared = rewrite_repo_links(text, self._remotes)
                prepared = mermaid_to_divs(prepared)

                self._processor.reset()
                html_body = normalize_article_html(self._processor.convert(prepared))
                toc_tokens = getattr(self._processor, "toc_tokens", [])

                node.ast = list(toc_tokens) if isinstance(toc_tokens, list) else []
                node.meta["content_html"] = html_body
                node.meta["__content_html_raw__"] = html_body
                node.meta["title"] = _derive_title(node, node.ast, text)
                if _MATH_MARKER in html_body:
                    node.meta["math"] = True

    def _load_remotes(self, builder: Builder) -> dict[str, dict[str, str]]:
        path = self._repo_remotes_path
        if path is None and builder.site_dir is not None:
            path = builder.site_dir / "repo-remotes.json"
        if path is None:
            return {}
        p = Path(path)
        if not p.is_file():
            return {}
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return {
            k: v
            for k, v in raw.items()
            if not k.startswith("_") and isinstance(v, dict)
        }


def wiki_markdown(*, repo_remotes_path: str | Path | None = None) -> WikiMarkdown:
    return WikiMarkdown(repo_remotes_path=repo_remotes_path)
