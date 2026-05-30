"""Rewrite markdown link sang HTML link / GitHub-GitLab URL."""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
from pathlib import Path

from .article import slugify
from .config import FILE_EXTENSIONS, REPO_REMOTES_PATH

# Lưu ý: filename wiki mới chứa Unicode + space + dấu Tiếng Việt, có thể bị
# percent-encoded trong link markdown (vd `%20` cho space). Regex phải cho
# phép cả raw Unicode và % escape — dùng class `[^)\s>]` để bắt rộng.
MD_LINK = re.compile(
    r"(\[[^\]]*\]\()([^)\s>]+\.md)([^)]*)(\))",
    re.IGNORECASE,
)
ANGLE_MD_LINK = re.compile(
    r"(<)([^<>\s]+\.md)(>)",
    re.IGNORECASE,
)
# Match `[text](../references/repos/<repo>[/<sub-path>][:<line>])`.
# Groups: 1=prefix `[text](`, 2=repo name, 3=sub path (with leading `/`) or
# empty, 4=optional line number, 5=closing `)`.
REPO_REF_LINK = re.compile(
    r"(\[[^\]]*\]\()\.\./references/repos/([^/)]+)((?:/[^):\s]+)*/?)(?::(\d+))?(\))",
)


def _target_to_html(target: str, slug_index: dict[str, str] | None) -> str:
    """Convert link target `path/to/Tên File.md[#anchor]` → `slug.html[#anchor]`.

    Filename wiki giờ là title gốc (có dấu, space). HTML output là slug ASCII.
    - Tách basename (đã decode URL nếu cần) → tra `slug_index` để lấy slug.
    - Fallback: slugify basename (cho link tới wiki ngoài snapshot scan, vd
      `_index` cho file đặc biệt giữ stem cũ).
    - Giữ nguyên path prefix (vd `../wiki/`).
    """
    # Tách phần anchor / query.
    if "#" in target:
        path_part, anchor = target.split("#", 1)
        anchor = "#" + anchor
    else:
        path_part, anchor = target, ""

    parts = path_part.rsplit("/", 1)
    prefix = parts[0] + "/" if len(parts) == 2 else ""
    basename = parts[-1]

    # Loại đuôi .md (case-insensitive).
    if basename.lower().endswith(".md"):
        stem_encoded = basename[:-3]
    else:
        stem_encoded = basename
    stem = urllib.parse.unquote(stem_encoded)

    if slug_index and stem in slug_index:
        slug = slug_index[stem]
    elif stem in ("_index", "_tags"):
        # Convention: _index.md → index.html; _tags.md không build trang riêng,
        # nhưng nếu có link thì giữ slug `_tags`.
        slug = "index" if stem == "_index" else stem
    else:
        slug = slugify(stem)

    return f"{prefix}{slug}.html{anchor}"


def rewrite_md_links(
    text: str,
    slug_index: dict[str, str] | None = None,
) -> str:
    """Đổi link `.md` sang `.html`, chuyển basename về slug ASCII.

    `slug_index` map `stem (filename không kèm .md, Unicode raw)` → slug HTML.
    Truyền từ build pipeline (đã pre-compute). Nếu None, fallback slugify
    basename — đủ cho test đơn lẻ.
    """

    def replace_link(match: re.Match[str]) -> str:
        prefix, target, suffix, end = match.groups()
        return f"{prefix}{_target_to_html(target, slug_index)}{suffix}{end}"

    text = MD_LINK.sub(replace_link, text)

    def replace_angle(match: re.Match[str]) -> str:
        open_b, target, close_b = match.groups()
        return f"{open_b}{_target_to_html(target, slug_index)}{close_b}"

    return ANGLE_MD_LINK.sub(replace_angle, text)


def load_repo_remotes() -> dict[str, dict[str, str]]:
    """Load mapping repo-name → {host, owner, repo, branch} từ JSON config.

    File config có thể chứa key `_comment` (bị bỏ qua). Trả về `{}` nếu file
    thiếu hoặc parse lỗi.
    """
    if not REPO_REMOTES_PATH.exists():
        return {}
    try:
        raw = json.loads(REPO_REMOTES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(
            f"[warn] {REPO_REMOTES_PATH.name} không parse được, bỏ qua "
            f"rewrite repo link: {exc}",
            file=sys.stderr,
        )
        return {}
    return {
        k: v for k, v in raw.items()
        if not k.startswith("_") and isinstance(v, dict)
    }


def _looks_like_file(sub_path: str) -> bool:
    """Heuristic: sub_path trỏ tới file (blob) hay directory (tree).

    - Có trailing `/` → directory.
    - Không có trailing `/` nhưng tên cuối có extension quen thuộc → file.
    - Còn lại → directory (an toàn cho path kiểu `service/ml_toolkit`).
    """
    if not sub_path or sub_path.endswith("/"):
        return False
    suffix = Path(sub_path).suffix.lower()
    return suffix in FILE_EXTENSIONS


def _build_repo_url(
    remote: dict[str, str], sub_path: str, line: str | None
) -> str:
    host = remote.get("host", "github").lower()
    owner = remote["owner"]
    repo = remote["repo"]
    branch = remote.get("branch", "main")
    sub = sub_path.lstrip("/").rstrip("/")
    is_file = _looks_like_file(sub_path)
    kind = "blob" if is_file else "tree"
    if host == "gitlab":
        base = f"https://gitlab.com/{owner}/{repo}/-/{kind}/{branch}"
    else:
        base = f"https://github.com/{owner}/{repo}/{kind}/{branch}"
    url = f"{base}/{sub}" if sub else base
    if is_file and line:
        url += f"#L{line}"
    return url


def rewrite_repo_links(
    text: str, remotes: dict[str, dict[str, str]]
) -> str:
    """Thay `../references/repos/<repo>/...` bằng URL GitHub/GitLab tương ứng.

    Link sang repo không có trong `remotes` được giữ nguyên (sẽ thành dead link
    khi host — để cảnh báo cần bổ sung config).
    """
    if not remotes:
        return text

    missing: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        prefix, repo_name, sub_path, line, end = match.groups()
        remote = remotes.get(repo_name)
        if not remote:
            missing.add(repo_name)
            return match.group(0)
        url = _build_repo_url(remote, sub_path or "", line)
        return f"{prefix}{url}{end}"

    out = REPO_REF_LINK.sub(replace, text)
    for name in sorted(missing):
        print(
            f"[warn] repo `{name}` chưa có trong repo-remotes.json — link giữ nguyên",
            file=sys.stderr,
        )
    return out
