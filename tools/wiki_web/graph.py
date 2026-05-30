"""Build dữ liệu đồ thị tri thức từ section `Liên kết tri thức` trong wiki.

Mỗi cạnh trong graph data có format:
    {source, target, labels, bidirectional}
Trong đó:
- source/target đã được chuẩn hoá thành chiều forward (nếu cạnh chỉ một
  chiều mà ngược thứ tự sorted, source/target được swap).
- bidirectional=True khi cả hai phía đều liên kết tới nhau.
- labels: list các "reason" rút gọn (dedup, sort).
"""

from __future__ import annotations

import json
import re
import urllib.parse
from collections import defaultdict
from pathlib import Path

from .article import slugify
from .config import PERSONAL_TAGS, SKIP_WIKI, WEB_DIR

LINK_HEADING_RE = re.compile(r"(?m)^#+\s*[^\n]*Liên kết[^\n]*$")
BULLET_LINK_RE = re.compile(
    r"^\s*[-*]\s+\[([^\]]*)\]\(([^)]+)\)(.*)$"
)


def _link_section(txt: str) -> str | None:
    m = LINK_HEADING_RE.search(txt)
    if not m:
        return None
    tail = txt[m.end():]
    nxt = re.search(r"(?m)^#+\s", tail)
    return tail[: nxt.start()] if nxt else tail


def _target_to_slug(
    target: str,
    slug_index: dict[str, str] | None = None,
) -> str:
    """Map link target `path/to/Tên File.md[#anchor]` → canonical slug.

    Filename giờ là title gốc (có dấu, space) — phải tra mapping `stem → slug`
    để khớp với node id trong graph. Fallback: slugify(basename).
    """
    base = target.rsplit("/", 1)[-1].split("#")[0]
    stem_encoded = re.sub(r"\.md$", "", base, flags=re.IGNORECASE)
    stem = urllib.parse.unquote(stem_encoded)
    if slug_index and stem in slug_index:
        return slug_index[stem]
    if stem in ("_index", "_tags"):
        return stem
    return slugify(stem)


def _reason(label: str, trailing: str = "") -> str:
    """Trích "reason" từ bullet liên kết.

    Hỗ trợ hai cú pháp song song trong wiki:
    - `[Title - reason](url)`   → reason nằm trong `[]`
    - `[Title](url) - reason`   → reason nằm sau `](url)`
    Ưu tiên dạng sau (mới hơn, dominant trong wiki); fallback về dạng trước.
    """
    trailing = trailing.strip()
    if trailing.startswith("-"):
        trailing = trailing[1:].strip()
        if trailing:
            return trailing
    parts = label.split(" - ", 1)
    return parts[1].strip() if len(parts) == 2 else label.strip()


def build_graph_data(
    article_meta: list[tuple[Path, str, str, list[str]]],
    slug_index: dict[str, str] | None = None,
) -> dict:
    # meta tuple = (md_path, slug, title, tags). Slug = node id canonical.
    slugs = {slug for md, slug, _, _ in article_meta if md.stem not in SKIP_WIKI}
    title_by = {slug: title for _, slug, title, _ in article_meta}
    tags_by = {slug: tags for _, slug, _, tags in article_meta}
    slug_by_md = {md: slug for md, slug, _, _ in article_meta}

    # key: (sorted_a, sorted_b) -> list of (direction, reason)
    pairs: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for md, slug, _, _ in article_meta:
        if md.stem in SKIP_WIKI:
            continue
        sec = _link_section(md.read_text(encoding="utf-8"))
        if not sec:
            continue
        for line in sec.splitlines():
            m = BULLET_LINK_RE.match(line)
            if not m:
                continue
            tgt = _target_to_slug(m.group(2), slug_index)
            if tgt in slugs and tgt != slug:
                s, d = sorted((slug, tgt))
                direction = "fwd" if slug == s else "bwd"
                pairs[(s, d)].append((direction, _reason(m.group(1), m.group(3))))

    node_deg: dict[str, int] = defaultdict(int)
    edges = []
    for (s, d), items in pairs.items():
        dirs = {direction for direction, _ in items}
        labels = sorted({reason for _, reason in items})
        if dirs == {"bwd"}:
            src, dst, bidi = d, s, False
        elif dirs == {"fwd"}:
            src, dst, bidi = s, d, False
        else:
            src, dst, bidi = s, d, True
        edges.append({
            "source": src,
            "target": dst,
            "labels": labels,
            "bidirectional": bidi,
        })
        node_deg[src] += 1
        node_deg[dst] += 1

    nodes = []
    for slug in sorted(slugs):
        tags = tags_by.get(slug, [])
        group = (
            "personal"
            if tags and all(t in PERSONAL_TAGS for t in tags)
            else "tech"
        )
        nodes.append({
            "id": slug,
            "title": title_by.get(slug, slug),
            "url": f"{slug}.html",
            "tags": tags,
            "group": group,
            "degree": node_deg.get(slug, 0),
        })
    return {"nodes": nodes, "edges": edges}


def compute_link_counts(graph_data: dict, mode: str) -> dict[str, int]:
    """Tính {slug: số liên kết} theo `mode`.

    - degree: tổng bậc (đã có sẵn ở node["degree"]).
    - outgoing/incoming: đếm theo chiều, cạnh `bidirectional` tính cho cả hai.
    """
    if mode == "degree":
        return {node["id"]: node["degree"] for node in graph_data["nodes"]}
    if mode not in {"outgoing", "incoming"}:
        raise ValueError(f"link_count mode không hợp lệ: {mode}")

    counts: dict[str, int] = {node["id"]: 0 for node in graph_data["nodes"]}
    for edge in graph_data["edges"]:
        src, dst = edge["source"], edge["target"]
        bidi = edge["bidirectional"]
        if mode == "outgoing":
            counts[src] = counts.get(src, 0) + 1
            if bidi:
                counts[dst] = counts.get(dst, 0) + 1
        else:
            counts[dst] = counts.get(dst, 0) + 1
            if bidi:
                counts[src] = counts.get(src, 0) + 1
    return counts


def write_graph_json(graph_data: dict) -> None:
    from .config import REPO_ROOT
    out = WEB_DIR / "assets" / "graph.json"
    out.write_text(
        json.dumps(graph_data, ensure_ascii=False, indent=0),
        encoding="utf-8",
    )
    print(f"  graph data -> {out.relative_to(REPO_ROOT)}")
