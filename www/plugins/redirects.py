"""Redirects: trang chuyển hướng tĩnh (meta refresh) cho URL cũ.

Phát một trang HTML nhỏ cho mỗi cặp ``từ → đích``: ``/about/`` và ``/en/about/``
trỏ sang CV ngoài, ``/posts/`` về trang chủ, và vài slug tiếng Việt cũ trỏ sang
slug mới. Trang có ``template=None`` để render plugin emit thẳng HTML.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyssg.core.node import Page
from pyssg.core.types import NodeKind

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder


def _redirect_html(target: str, canonical: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        f'<meta http-equiv="refresh" content="0; url={target}">\n'
        f'<link rel="canonical" href="{canonical}">\n'
        '<meta name="robots" content="noindex">\n'
        "<title>Redirecting</title>\n"
        "</head>\n"
        "<body>\n"
        f'<p>This page has moved to <a href="{target}">{target}</a>.</p>\n'
        f'<script>location.replace("{target}")</script>\n'
        "</body>\n"
        "</html>\n"
    )


class Redirects:
    name = "redirects"
    cache_version = "1.0.0"

    def __init__(self, *, rules: dict[str, str]) -> None:
        self._rules = dict(rules)

    def apply(self, builder: Builder) -> None:
        base_url = builder.config.base_url if builder.config is not None else ""

        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name)
            def _eval(b: Build) -> None:
                for source, target in self._rules.items():
                    canonical = target if target.startswith("http") else f"{base_url}{target}"
                    pid = f"page:redirect:{source}"
                    meta = {"title": "Redirecting", "content_html": _redirect_html(target, canonical)}
                    existing = b.graph.get(pid)
                    if isinstance(existing, Page):
                        existing.url = source
                        existing.template = None
                        existing.meta = meta
                    else:
                        b.graph.add_node(
                            Page(id=pid, kind=NodeKind.PAGE, url=source, template=None, meta=meta)
                        )
