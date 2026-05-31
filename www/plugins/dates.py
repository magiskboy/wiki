"""Locale-aware date formatting exposed to templates.

``format_date`` reproduces the original site's "Thứ X, ngày D tháng M năm Y"
(vi) and "March 19, 2021" (en) formats. ``TemplateHelpers`` registers it as a
Jinja global through pyssg's ``template_globals`` seam.
"""

from __future__ import annotations

from datetime import date, datetime

from pyssg.build import Build
from pyssg.builder import Builder

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
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
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
    parsed = _as_date(value)
    if parsed is None:
        return ""
    if locale == "en":
        return f"{_EN_MONTHS[parsed.month - 1]} {parsed.day}, {parsed.year}"
    # Python: Monday=0..Sunday=6; the Vietnamese labels are indexed Sunday=0.
    weekday = (parsed.weekday() + 1) % 7
    return (
        f"{_VI_DAYS[weekday]}, ngày {parsed.day} tháng {parsed.month} năm {parsed.year}"
    )


class TemplateHelpers:
    """Register the localized date formatter as a template global."""

    def apply(self, builder: Builder) -> None:
        builder.hooks.collect.tap("TemplateHelpers", self._register, stage=-1000)

    def _register(self, build: Build) -> None:
        globals_ = build.meta.setdefault("template_globals", {})
        if isinstance(globals_, dict):
            globals_["format_date"] = format_date
