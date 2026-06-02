"""Hàm thuần dùng chung cho các plugin của site (không phụ thuộc pyssg core).

Gồm: định dạng ngày theo locale (tái hiện "Thứ X, ngày D tháng M năm Y" cho vi và
"March 19, 2021" cho en), helper tiền tố URL theo locale, và bộ dựng "card" bài
viết cho các trang danh sách (trang chủ, tag, category).
"""

from __future__ import annotations

from datetime import date, datetime

import markdown as md_lib

from pyssg.plugins.content_meta import slugify

# Bộ render markdown nhẹ cho phần mô tả/preview bài viết: mô tả trong frontmatter
# cũng là markdown (đậm ``__...__``, link ``[x](y)``...) nên cần render giống nội
# dung thay vì in literal. reset() trước mỗi lần dùng để không rò trạng thái.
_DESC_MD = md_lib.Markdown(extensions=["fenced_code"], output_format="html")


def render_description(text: object) -> str:
    """Render mô tả markdown → HTML; bỏ thẻ ``<p>`` bao ngoài nếu chỉ một đoạn."""
    if not text:
        return ""
    _DESC_MD.reset()
    html = _DESC_MD.convert(str(text))
    if html.startswith("<p>") and html.endswith("</p>") and html.count("<p>") == 1:
        html = html[3:-4]
    return html

_VI_DAYS = [
    "Chủ nhật",
    "Thứ hai",
    "Thứ ba",
    "Thứ tư",
    "Thứ năm",
    "Thứ sáu",
    "Thứ bảy",
]
_EN_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _as_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def format_date(value: object, locale: str = "vi") -> str:
    """Ngày đã định dạng theo locale; chuỗi rỗng nếu không parse được."""
    parsed = _as_date(value)
    if parsed is None:
        return ""
    if locale == "en":
        return f"{_EN_MONTHS[parsed.month - 1]} {parsed.day}, {parsed.year}"
    # Python: Monday=0..Sunday=6; nhãn tiếng Việt đánh chỉ số Sunday=0.
    weekday = (parsed.weekday() + 1) % 7
    return (
        f"{_VI_DAYS[weekday]}, ngày {parsed.day} tháng {parsed.month} năm {parsed.year}"
    )


def base_path(locale: str, default_locale: str) -> str:
    """Tiền tố URL của một locale: "/" cho locale mặc định, "/<locale>/" còn lại."""
    return "/" if locale == default_locale else f"/{locale}/"


def locale_prefix(locale: str, default_locale: str) -> str:
    """Phần segment locale trong URL: "" cho mặc định, "<locale>" còn lại."""
    return "" if locale == default_locale else locale


def _as_str_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    return []


def tag_links(tags: object, locale: str, default_locale: str) -> list[dict[str, str]]:
    """Danh sách {name, url} liên kết tới trang tag theo locale."""
    base = base_path(locale, default_locale)
    return [
        {"name": tag, "url": f"{base}tags/{slugify(tag)}/"}
        for tag in _as_str_list(tags)
    ]


def post_card(meta: dict[str, object], url: str, locale: str, default_locale: str) -> dict[str, object]:
    """Dữ liệu một bài viết để hiển thị trong danh sách (postitem)."""
    description = meta.get("description") or meta.get("excerpt") or ""
    return {
        "url": url,
        "title": str(meta.get("title") or url),
        "date": meta.get("date"),
        "date_display": format_date(meta.get("date"), locale),
        "description": render_description(description),
        "tags": _as_str_list(meta.get("tags")),
        "tag_links": tag_links(meta.get("tags"), locale, default_locale),
    }


def date_sort_key(meta: dict[str, object]) -> str:
    value = meta.get("date")
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value) if value is not None else ""
