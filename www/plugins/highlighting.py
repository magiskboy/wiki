"""``data-theme``-scoped Pygments stylesheets.

The built-in Highlight plugin only switches code colors via
``prefers-color-scheme``, but this site toggles themes with a ``data-theme``
attribute. ``HighlightThemes`` replaces the ``highlight_css()`` global with one
Pygments stylesheet per theme, each scoped under its ``[data-theme=...]``
selector, so code blocks follow the theme switcher.
"""

from __future__ import annotations

from pyssg.build import Build
from pyssg.builder import Builder


class HighlightThemes:
    def __init__(
        self,
        *,
        themes: dict[str, str] | None = None,
        css_class: str = "highlight",
    ) -> None:
        self._themes = themes or {
            "light": "default",
            "dark": "github-dark",
            "papyrus": "gruvbox-dark",
        }
        self._css_class = css_class
        self._css: str | None = None

    def apply(self, builder: Builder) -> None:
        # After Highlight's collect (stage 0) so this global wins.
        builder.hooks.collect.tap("HighlightThemes", self._register, stage=500)

    def _register(self, build: Build) -> None:
        try:
            from markupsafe import Markup
        except ImportError:
            return
        css = Markup(self._stylesheet())
        globals_ = build.meta.setdefault("template_globals", {})
        if isinstance(globals_, dict):
            globals_["highlight_css"] = lambda: css

    def _stylesheet(self) -> str:
        if self._css is not None:
            return self._css
        from pygments.formatters import HtmlFormatter

        blocks = []
        for theme, style in self._themes.items():
            selector = f'[data-theme="{theme}"] .{self._css_class}'
            blocks.append(
                str(
                    HtmlFormatter(style=style, cssclass=self._css_class).get_style_defs(
                        selector
                    )
                )
            )
        self._css = "\n".join(blocks)
        return self._css
