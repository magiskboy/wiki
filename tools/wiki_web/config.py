"""Tập trung các path và hằng số cấu hình của build pipeline.

Đây là nơi duy nhất nên sửa khi muốn:
- Thêm/bớt section "meta" được nhận diện trong bài viết.
- Đổi danh sách tag cá nhân để tô màu nhóm "personal" trong đồ thị.
- Đổi pin version KaTeX hoặc cách inject KaTeX.
"""

from __future__ import annotations

from pathlib import Path

# --- Path layout ---------------------------------------------------------
PACKAGE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = PACKAGE_DIR.parent
REPO_ROOT = TOOLS_DIR.parent
WIKI_DIR = REPO_ROOT / "wiki"
WEB_DIR = REPO_ROOT / "web"

# Code và data sống chung trong package wiki_web/. Asset, template HTML và
# config repo-remotes đều đặt cạnh các module .py.
ASSETS_SRC = PACKAGE_DIR / "assets"
TEMPLATES_DIR = PACKAGE_DIR / "templates"
PAGE_TEMPLATE_PATH = TEMPLATES_DIR / "page.html"
REPO_REMOTES_PATH = PACKAGE_DIR / "repo-remotes.json"

# --- Wiki convention -----------------------------------------------------
# Slug stem của các file markdown KHÔNG được build thành trang độc lập.
SKIP_WIKI = {"_index", "_tags", "Tổng quan"}

# Heading được nhận diện là "meta section" để tô class article-meta-heading.
META_SECTION_TITLES = {
    "Tags",
    "Nguồn tham khảo",
    "Nguồn",
    "Liên kết tri thức",
    "Liên kết",
}

# Tag thuộc nhóm "cá nhân" — node mà tất cả tag đều thuộc set này sẽ
# được gắn group="personal" trong graph data.
PERSONAL_TAGS = {"mindset", "career", "learning", "philosophy", "finance"}

# Extension phổ biến — heuristic phân biệt blob (file) vs tree (directory)
# khi rewrite link ../references/repos/<repo>/...
FILE_EXTENSIONS = {
    ".cpp", ".h", ".hpp", ".c", ".py", ".pyi", ".js", ".ts", ".tsx", ".jsx",
    ".md", ".mdx", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
    ".sh", ".bash", ".zsh", ".rs", ".go", ".java", ".kt", ".rb",
    ".html", ".css", ".scss", ".sql", ".xml", ".txt", ".env",
    ".dockerfile", ".lock", ".proto",
}

# --- KaTeX (math rendering) ---------------------------------------------
KATEX_VERSION = "0.16.11"

KATEX_SNIPPET = f"""<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.css" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.js" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/contrib/auto-render.min.js" crossorigin="anonymous"
  onload="renderMathInElement(document.body, {{delimiters: [{{left: '\\\\[', right: '\\\\]', display: true}}, {{left: '\\\\(', right: '\\\\)', display: false}}], throwOnError: false}});"></script>"""

# Marker mà ArithmatexExtension(generic=True) ghi vào HTML khi gặp math.
# Dùng để detect trang nào cần load KaTeX (tránh tải tốn băng thông cho phần
# lớn bài không có math).
MATH_MARKER = 'class="arithmatex"'
