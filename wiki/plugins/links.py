"""Rewrite link trong markdown wiki.

Ba loại link được xử lý (theo thứ tự, không chồng lấn vì khác đuôi):

1. ``references/repos/<repo>/...[:line]`` → URL GitHub/GitLab (repo-remotes.json).
2. ``references/<...>.<ext nhị phân>`` → ``/references/<...>`` (asset copy vào
   artifact). Loại ``references/repos/`` ra khỏi nhóm này (đã thành URL ở (1)).
3. ``*.md`` → URL trang đích (``/slug/`` hoặc ``/references/interviews/slug/``)
   tra qua ``slug_index`` (key = stem tên file, đã decode URL).

Khác generator wiki_web cũ: output là **pretty URL** (``/slug/``) thay vì
``slug.html``; và regex repo/asset **bỏ qua số lượng ``../``** (nhận diện theo
đuôi ``references/...``) để không phụ thuộc độ sâu thư mục — vốn đã đổi khi dồn
nội dung vào ``content/``.
"""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path

from .meta import slugify

# --- .md links -----------------------------------------------------------
MD_LINK = re.compile(r"(\[[^\]]*\]\()([^)\s>]+\.md)([^)]*)(\))", re.IGNORECASE)
ANGLE_MD_LINK = re.compile(r"(<)([^<>\s]+\.md)(>)", re.IGNORECASE)

# --- repo refs: (../)*references/repos/<repo>[/sub][:line] ---------------
REPO_REF_LINK = re.compile(
    r"(\[[^\]]*\]\()(?:\.\./)*references/repos/([^/)]+)((?:/[^):\s]+)*/?)(?::(\d+))?(\))"
)

# --- binary assets ngoài content -----------------------------------------
ASSET_EXTS = ("pdf", "png", "jpe?g", "gif", "svg", "webp")
_ASSET_TAIL = "|".join(ASSET_EXTS)
# Hỗ trợ cả ``](path)`` và ``](<path có khoảng trắng>)``; loại references/repos.
ASSET_LINK = re.compile(
    r"(\[[^\]]*\]\()<?((?:\.\./)*references/(?!repos/)[^)>]+?\.(?:" + _ASSET_TAIL + r"))>?(\))",
    re.IGNORECASE,
)

# Extension quen thuộc — heuristic phân biệt blob (file) vs tree (directory).
FILE_EXTENSIONS = {
    ".cpp", ".h", ".hpp", ".c", ".py", ".pyi", ".js", ".ts", ".tsx", ".jsx",
    ".md", ".mdx", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
    ".sh", ".bash", ".zsh", ".rs", ".go", ".java", ".kt", ".rb",
    ".html", ".css", ".scss", ".sql", ".xml", ".txt", ".env",
    ".dockerfile", ".lock", ".proto",
}


def _target_to_url(target: str, slug_index: dict[str, str] | None) -> str:
    """``path/to/Tên File.md[#anchor]`` → ``/slug/[#anchor]`` qua slug_index."""
    if "#" in target:
        path_part, anchor = target.split("#", 1)
        anchor = "#" + anchor
    else:
        path_part, anchor = target, ""

    basename = path_part.rsplit("/", 1)[-1]
    stem_encoded = basename[:-3] if basename.lower().endswith(".md") else basename
    stem = urllib.parse.unquote(stem_encoded)

    if slug_index and stem in slug_index:
        return slug_index[stem] + anchor
    if stem == "_index":
        return "/" + anchor
    return f"/{slugify(stem)}/" + anchor


def rewrite_md_links(text: str, slug_index: dict[str, str] | None = None) -> str:
    def replace_link(match: re.Match[str]) -> str:
        prefix, target, suffix, end = match.groups()
        return f"{prefix}{_target_to_url(target, slug_index)}{suffix}{end}"

    text = MD_LINK.sub(replace_link, text)

    def replace_angle(match: re.Match[str]) -> str:
        open_b, target, close_b = match.groups()
        return f"{open_b}{_target_to_url(target, slug_index)}{close_b}"

    return ANGLE_MD_LINK.sub(replace_angle, text)


def _looks_like_file(sub_path: str) -> bool:
    if not sub_path or sub_path.endswith("/"):
        return False
    return Path(sub_path).suffix.lower() in FILE_EXTENSIONS


def _build_repo_url(remote: dict[str, str], sub_path: str, line: str | None) -> str:
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


def rewrite_repo_links(text: str, remotes: dict[str, dict[str, str]]) -> str:
    if not remotes:
        return text

    def replace(match: re.Match[str]) -> str:
        prefix, repo_name, sub_path, line, end = match.groups()
        remote = remotes.get(repo_name)
        if not remote:
            return match.group(0)
        return f"{prefix}{_build_repo_url(remote, sub_path or '', line)}{end}"

    return REPO_REF_LINK.sub(replace, text)


def rewrite_asset_links(text: str, registry: set[str]) -> str:
    """``(../)*references/<tail>.<ext>`` → ``/references/<tail>`` và ghi nhận
    ``tail`` (đã decode) vào ``registry`` để copy sang artifact."""

    def replace(match: re.Match[str]) -> str:
        prefix, target, end = match.groups()
        # Bỏ mọi tiền tố ../ , lấy phần từ "references/".
        idx = target.find("references/")
        rel = target[idx + len("references/"):]
        tail = urllib.parse.unquote(rel)
        registry.add(tail)
        encoded = urllib.parse.quote(tail)
        return f"{prefix}/references/{encoded}{end}"

    return ASSET_LINK.sub(replace, text)
