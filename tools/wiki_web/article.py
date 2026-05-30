"""Article dataclass + extract metadata từ markdown."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .config import SKIP_WIKI, WIKI_DIR

FIRST_H1 = re.compile(r"^#\s+(.+)$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass(frozen=True)
class Article:
    slug: str
    title: str
    href: str  # relative to web root, e.g. foo.html


def wiki_files() -> list[Path]:
    """Đệ quy lấy mọi `.md` trong wiki/ — kể cả trong category subfolder."""
    return sorted(WIKI_DIR.rglob("*.md"))


def slugify(title: str) -> str:
    """Convert title (có dấu Tiếng Việt) sang ASCII slug cho URL.

    Phải giữ đồng bộ với `tools/rename_wiki_files.py::slugify` để filename
    md mới (theo title) và slug HTML output map cùng quy tắc.
    """
    s = title.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def article_slug(md_path: Path, title: str) -> str:
    """Slug canonical của một bài wiki.

    - File đặc biệt (`_index`, `_tags`) giữ nguyên stem để code SKIP_WIKI
      và logic detect index page hoạt động bình thường.
    - Còn lại: slugify(title gốc của bài).
    """
    if md_path.stem in SKIP_WIKI:
        return md_path.stem
    return slugify(title)


def md_to_html_name(md_path: Path, title: str | None = None) -> str:
    """Tên file HTML output.

    `_index.md` → `index.html`. Còn lại = `<slugify(title)>.html`.
    Yêu cầu truyền `title` cho mọi file thường — chỉ optional cho _index.
    """
    if md_path.stem == "_index":
        return "index.html"
    if title is None:
        title = extract_title(
            md_path.read_text(encoding="utf-8"),
            md_path.stem.replace("-", " ").title(),
        )
    return f"{article_slug(md_path, title)}.html"


def tag_url(tag: str) -> str:
    """URL path tới trang tag (thư mục để host /tags/{name}/)."""
    return f"tags/{tag}/"


def parse_frontmatter(md_text: str) -> tuple[dict[str, list[str] | str], str]:
    """Naive YAML parse — hỗ trợ scalar và block list dạng `key:\\n  - item`.

    Return (parsed_dict, body_without_frontmatter). Nếu không có frontmatter,
    trả ({}, md_text).
    """
    m = FRONTMATTER_RE.match(md_text)
    if not m:
        return {}, md_text
    fm_text = m.group(1)
    body = md_text[m.end():]

    data: dict[str, list[str] | str] = {}
    cur_key: str | None = None
    for line in fm_text.split("\n"):
        if not line.strip():
            continue
        if line.startswith("  - ") and cur_key is not None and isinstance(data.get(cur_key), list):
            data[cur_key].append(line[4:].strip())  # type: ignore[union-attr]
            continue
        if ":" in line:
            key, _, rest = line.partition(":")
            key = key.strip()
            rest = rest.strip()
            if not rest:
                data[key] = []
                cur_key = key
            else:
                data[key] = rest
                cur_key = None
    return data, body


def extract_title(md_text: str, fallback: str) -> str:
    _, body = parse_frontmatter(md_text)
    match = FIRST_H1.search(body)
    if match:
        return match.group(1).strip()
    return fallback


def extract_description(md_text: str) -> str:
    _, body = parse_frontmatter(md_text)
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped[:160]
    return "Kho tri thức cá nhân"


def extract_tags(md_text: str) -> list[str]:
    """Đọc tags từ frontmatter YAML.

    Wiki đã migrate khối `# Tags` cuối file sang frontmatter `tags:` block.
    """
    fm, _ = parse_frontmatter(md_text)
    raw = fm.get("tags", [])
    if isinstance(raw, list):
        return [t for t in (s.strip() for s in raw) if t]
    if isinstance(raw, str) and raw:
        # Inline list `[a, b]` hoặc CSV — best effort.
        s = raw.strip().strip("[]")
        return [t.strip() for t in s.split(",") if t.strip()]
    return []


def extract_date(md_text: str) -> str | None:
    """Đọc `date` từ frontmatter."""
    fm, _ = parse_frontmatter(md_text)
    val = fm.get("date")
    if isinstance(val, str) and val.strip():
        return val.strip()
    return None


def extract_category(md_path: Path) -> str | None:
    """Tên category = tên folder cha relative tới WIKI_DIR.

    File ở wiki root → None.
    """
    try:
        rel = md_path.relative_to(WIKI_DIR)
    except ValueError:
        return None
    if len(rel.parts) < 2:
        return None
    return rel.parts[0]


def category_slug(name: str) -> str:
    """Slug ASCII cho URL category."""
    return slugify(name)


def strip_frontmatter(md_text: str) -> str:
    """Trả về body sau khi loại bỏ frontmatter (nếu có)."""
    _, body = parse_frontmatter(md_text)
    return body


def append_tags_and_date(md_body: str, tags: list[str], date_str: str | None, tag_href: str) -> str:
    """Append khối Tags (link tới trang tag) và date vào cuối body.

    Tags render dưới dạng heading `# Tags` + bullet list như trước migration,
    để giữ nguyên UI/CSS có sẵn. Date render dưới dạng dòng nhỏ italic ở cuối.
    """
    body = md_body.rstrip()
    parts: list[str] = [body] if body else []
    if tags:
        tag_lines = ["# Tags", ""]
        for t in tags:
            url = f"{tag_href}{t}/"
            tag_lines.append(f"- [{t}]({url})")
        parts.append("\n".join(tag_lines))
    if date_str:
        parts.append(f"_Cập nhật: {date_str}_")
    return "\n\n".join(parts) + "\n"
