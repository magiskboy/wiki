"""CLI entry: argparse + gọi build()."""

from __future__ import annotations

import argparse
import sys

from .build import build


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chuyển wiki/*.md sang HTML tĩnh trong web/"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="xóa nội dung web/ trước khi build (giữ .gitkeep)",
    )
    parser.add_argument(
        "--link-count",
        choices=("degree", "outgoing", "incoming"),
        default="degree",
        help=(
            "cách tính số liên kết cho top bài trên trang index: "
            "degree (mặc định, tổng bậc), outgoing (liên kết đi ra), "
            "incoming (được trỏ tới)"
        ),
    )
    args = parser.parse_args()
    sys.exit(build(clean=args.clean, link_count=args.link_count))
