"""HighlightThemes: stylesheet Pygments scope theo ``data-theme``.

Plugin ``highlight`` built-in chỉ sinh một bộ màu (``site.highlight_css``). Site
này đổi giao diện bằng thuộc tính ``data-theme`` nên cần một stylesheet riêng cho
mỗi theme, mỗi cái scope dưới ``[data-theme=...]``. Ghi đè thẳng
``config.site["highlight_css"]`` để base template nhúng vào ``<style>``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyssg.core.builder import Builder

# Class Pygments dùng bởi plugin highlight built-in (cssclass="highlight").
_CSS_CLASS = "highlight"


class HighlightThemes:
    name = "highlight_themes"
    cache_version = "1.0.0"

    def __init__(
        self,
        *,
        themes: dict[str, str] | None = None,
        css_class: str = _CSS_CLASS,
    ) -> None:
        self._themes = themes or {
            "light": "default",
            "dark": "github-dark",
            "papyrus": "gruvbox-dark",
        }
        self._css_class = css_class

    def apply(self, builder: Builder) -> None:
        if builder.config is None:
            return
        builder.config.site["highlight_css"] = self._stylesheet()

    def _stylesheet(self) -> str:
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
        return "\n".join(blocks)
