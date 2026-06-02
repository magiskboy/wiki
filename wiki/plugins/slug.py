"""WikiSlug: URL phẳng ``/slug/`` với slug ASCII bỏ dấu tiếng Việt.

permalink built-in sinh URL theo đường dẫn file (giữ dấu + thư mục). Wiki cần
URL phẳng ASCII khớp site gốc, nên tap vào ``route`` (WaterfallHook) để ghi đè
URL bằng slug từ tên file. ``index.md`` → ``/`` (trang chủ).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pyssg.core.types import NodeKind

from ._util import ascii_slug

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder
    from pyssg.core.node import Node


class WikiSlug:
    name = "wiki_slug"
    cache_version = "1.0.0"

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.route.tap(self.name)
            def _route(url: str, node: Node) -> str:
                if getattr(node, "kind", None) is not NodeKind.MARKDOWN:
                    return url
                stem = Path(node.source_path or "").stem
                if stem == "index":
                    return "/"
                return f"/{ascii_slug(stem)}/"


def wiki_slug() -> WikiSlug:
    return WikiSlug()
