"""Trang đồ thị tri thức: embed graph data + load 2D/3D viewer."""

from __future__ import annotations

import hashlib
import json

from ..config import REPO_ROOT, WEB_DIR
from ..template import render_body_template, render_page


def render_graph_page_html(data: dict) -> str:
    blob = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return render_body_template("graph_page.html", json_blob=blob)


def _graph_js_version() -> str:
    """Hash 8-ký-tự của graph.js để cache-bust khi file đổi."""
    graph_js = WEB_DIR / "assets" / "graph.js"
    if not graph_js.exists():
        return "x"
    return hashlib.md5(graph_js.read_bytes()).hexdigest()[:8]


def write_graph_page(data: dict) -> None:
    graph_dir = WEB_DIR / "graph"
    graph_dir.mkdir(parents=True, exist_ok=True)
    js_ver = _graph_js_version()
    extra = (
        '<script>window.KB_ROOT="../";</script>\n'
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js"></script>\n'
        '<script src="https://cdn.jsdelivr.net/npm/layout-base@2.0.1/layout-base.js"></script>\n'
        '<script src="https://cdn.jsdelivr.net/npm/cose-base@2.2.0/cose-base.js"></script>\n'
        '<script src="https://cdn.jsdelivr.net/npm/cytoscape-fcose@2.2.0/cytoscape-fcose.js"></script>\n'
        f'<script src="../assets/graph.js?v={js_ver}" defer></script>'
    )
    page = render_page(
        title="Đồ thị tri thức",
        description="Trực quan hóa mạng liên kết giữa các tri thức",
        content=render_graph_page_html(data),
        root="../",
        main_class=" site-main--graph",
        extra_scripts=extra,
    )
    out = graph_dir / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"  graph page -> {out.relative_to(REPO_ROOT)}")
