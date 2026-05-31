"""KaTeX flag for pages that use math.

``Math`` sets ``meta["math"]`` on any page whose body contains ``$$`` so the
layout can load KaTeX from a CDN only where it is needed.
"""

from __future__ import annotations

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.models import Source


class Math:
    def apply(self, builder: Builder) -> None:
        # After Markdown (default stage 0); the body still holds the delimiters.
        builder.hooks.transform.tap("Math", self._flag, stage=300)

    def _flag(self, source: Source, build: Build) -> Source:
        if "$$" in source.body:
            source.meta["math"] = True
        return source
