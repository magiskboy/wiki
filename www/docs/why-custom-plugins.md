# Vì sao phải viết plugin mới thay vì tái dùng/kế thừa plugin pyssg

Báo cáo này giải thích, cho từng plugin tự viết trong `www/plugins/`, lý do **không
thể** dùng lại plugin built-in của pyssg 0.1.0 hay kế thừa (subclass) nó.

Tham chiếu mã built-in: `.venv/lib/python3.13/site-packages/pyssg/plugins/`.

---

## TL;DR

1. **Kiến trúc pyssg không thiết kế để kế thừa.** Mỗi plugin built-in là một class
   mỏng (`name`, `cache_version`, `apply`) chỉ *tap hook*; toàn bộ logic nằm ở các
   **hàm module thuần** (vd `build_collections`, `build_taxonomies`, `_items`,
   `_to_dict`) — không phải method override được. Điểm mở rộng chính thức của pyssg
   là **viết plugin mới và tap hook**, không phải subclass. Subclass cũng vẫn phải
   chép lại các hàm module ⇒ tương đương viết mới.
2. **Site này đa ngôn ngữ (vi mặc định ở `/`, en ở `/en/`).** Ba plugin built-in lo
   danh sách/phân loại/feed (`collections`, `taxonomy`, `rss`) đều **mù locale** —
   gộp vi+en, không sinh tiền tố `/en/`. Không có tham số nào bật i18n cho chúng.
3. **Render plugin mới bỏ cơ chế đăng ký Jinja global/filter.** Không còn cách cấp
   hàm như `format_date()` / `highlight_css()` cho template ⇒ phải *tiền tính* dữ
   liệu đã định dạng vào `meta` / `config.site`.

Những gì **đã tái dùng nguyên** (để giảm code mới): `directory_loader`,
`frontmatter`, `i18n`, `content_meta`, `highlight` (tô màu code), `permalink`,
`sitemap`, `render`, và hàm `content_meta.slugify`.

---

## Bảng tổng quan

| Nhu cầu | Built-in | Tái dùng được? | Giải pháp |
|---|---|---|---|
| Tải file, tách frontmatter | `directory_loader`, `frontmatter` | ✅ nguyên | dùng thẳng |
| Định tuyến locale vi/en | `i18n` | ✅ nguyên | dùng thẳng |
| TOC, excerpt, reading time | `content_meta` | ✅ nguyên | dùng thẳng |
| Sinh trang từ document | `permalink` | ✅ nguyên | dùng thẳng |
| sitemap.xml | `sitemap` | ✅ nguyên | dùng thẳng |
| Tô màu cú pháp code | `highlight` | ✅ phần tô màu | giữ; chỉ thay CSS |
| Markdown + công thức LaTeX | `markdown` | ❌ | `WwwMarkdown` |
| Danh sách bài phân trang theo locale | `collections` | ❌ | `WwwCollections` |
| Tag/category theo locale | `taxonomy` | ❌ | `WwwTaxonomy` |
| Feed RSS theo locale | `rss` | ❌ | `WwwRss` |
| CSS code theo `data-theme` | `highlight` (CSS) | ❌ | `HighlightThemes` |
| Chuyển hướng URL cũ | *(không có)* | — | `Redirects` |
| Copy `static/` ra gốc | `asset_copy` | ❌ | `StaticFiles` |

---

## Chi tiết từng plugin tự viết

### 1. `WwwMarkdown` — vì bộ extension của `markdown` bị "đóng cứng"

Plugin `markdown` built-in khởi tạo trình parse với danh sách extension **cố định,
hard-code trong `__init__`**:

```python
self._md = md_lib.Markdown(
    extensions=["fenced_code", "tables", "sane_lists", TocExtension(...)],
    output_format="html",
)
```

Không có tham số nào để thêm extension. Site cần `pymdownx.arithmatex` (generic) để
bảo vệ `$...$`/`$$...$$` cho KaTeX render client-side (8 bài có công thức). Muốn
thêm thì phải **override trọn `__init__`** — tức viết lại, không còn là kế thừa có
ý nghĩa. Tiện thể, vì lý do (3) bên dưới, `WwwMarkdown` còn tiền tính `math`,
`date_display`, `tag_links`, `description_html` theo locale ngay trong stage parse.

### 2. `WwwCollections` — vì `collections` mù locale và "card" thiếu dữ liệu

`CollectionItem.section` được định nghĩa là **segment URL đầu tiên**. Với i18n:

- bài vi → URL `/posts/...` ⇒ `section = "posts"`
- bài en → URL `/en/posts/...` ⇒ `section = "en"`

Một `CollectionSpec` không thể vừa chọn đúng bài vừa phân trang ở đúng gốc mỗi
locale (`/` + `/page/N/` cho vi, `/en/` + `/en/page/N/` cho en). Ngoài ra, dict mà
built-in dựng (`_to_dict`) **cố định** chỉ có `url/title/date/excerpt/tags` — thiếu
ngày đã địa phương hoá (`date_display`), mô tả đã render markdown, `tag_links`, và
dữ liệu chuyển ngữ. Các hàm này là hàm module ⇒ subclass `CollectionsPlugin` cũng
không đổi được hình dạng output.

### 3. `WwwTaxonomy` — vì `taxonomy` mù locale (và lỗi đè slug)

`taxonomy` built-in duyệt **mọi** document bất kể locale và sinh `/tags/<term>/`
trộn vi+en, không có `/en/tags/`. Subclass `TaxonomyPlugin` chỉ cho đổi *danh sách
chiều phân loại* (`taxonomy(tag(), category())`), **không** đổi được tính
locale-aware hay template/định dạng output (logic nằm ở `build_taxonomies` /
`_build_one`). Bản tự viết còn xử lý một lỗi mà cách gom theo *term thô* gây ra:
"Python" và "python" cùng slug `python` sẽ ghi đè trang của nhau và mất bài — nên
phải **gom theo slug** rồi trộn.

### 4. `WwwRss` — vì `rss` chỉ một feed gộp, thiếu trường

Built-in phát **một** `/feed.xml` (`_PAGE_URL` là hằng module), trộn mọi locale,
cap 20, mỗi `<item>` chỉ có `title/link/description` (không `<guid>`, không
`<pubDate>`). Site cũ có `/feed.xml` (vi) **và** `/en/feed.xml`, kèm guid + pubDate.
Factory `rss(title)` chỉ nhận tiêu đề — không có tham số locale, không đổi URL/định
dạng được. Bản tự viết giữ nguyên ý tưởng nhưng phát feed cho từng locale.

### 5. `HighlightThemes` — bổ sung, không thay thế `highlight`

Đây là ví dụ **tái dùng tối đa**: vẫn giữ `highlight` built-in để tô màu code (parse
stage 250). Chỉ có phần CSS là không hợp: built-in chỉ bơm **một** stylesheet qua
`config.site.setdefault("highlight_css", ...)`, scope vào `.highlight`. Site đổi
giao diện bằng thuộc tính `data-theme` (light/dark/papyrus) nên cần **3** stylesheet,
mỗi cái scope dưới `[data-theme="..."]`. Việc sinh CSS nằm bên trong built-in, không
có tham số đa-theme ⇒ `HighlightThemes` ghi đè `config.site["highlight_css"]` bằng
CSS đa-theme.

### 6. `Redirects` — pyssg không có plugin tương đương

Không có built-in nào lo chuyển hướng. Cần phát trang HTML `meta refresh` cho URL cũ
(`/about/` → CV, `/posts/` → `/`, vài slug tiếng Việt đổi tên). Viết mới hoàn toàn:
tạo `Page` với `template=None` để render plugin emit thẳng HTML.

### 7. `StaticFiles` — vì `asset_copy` chỉ phục vụ `assets/` của layout

`asset_copy` chỉ copy `assets/` của layout sang `/assets/...` (`_OUTPUT_SUBDIR =
"assets"`, nguồn là `layout.assets_dir`, đều cứng). Site phục vụ `/style.css`,
`/robots.txt`, `/images/...` ở **gốc** (bài viết tham chiếu `/images/...` tuyệt
đối). Không có tham số trỏ tới `static/` → gốc ⇒ viết plugin copy riêng.

---

## Ràng buộc xuyên suốt: không còn "seam" cho Jinja global

`RenderPlugin` mới tự dựng `jinja2.Environment` bên trong và **không expose hook**
để plugin đăng ký global/filter (API cũ có `template_globals`); template chỉ được
tiêm thêm hàm dịch `t(...)`. Hệ quả: không thể cấp `format_date()` hay
`highlight_css()` cho template như thiết kế cũ. Đây là lý do gốc khiến nhiều thứ
phải **tiền tính** trong plugin thay vì để template tự gọi hàm:

- ngày địa phương hoá, link tag, mô tả render markdown → tính sẵn vào `meta`
  (trong `WwwMarkdown` và bộ dựng card `_util.post_card`);
- CSS highlight → đẩy qua `config.site` (`HighlightThemes`).

---

## Kết luận

Việc viết plugin mới ở đây **không phải workaround** mà là cách mở rộng đúng kiểu
của pyssg (tap hook trong plugin riêng). Built-in được tái dùng ở mọi chỗ có thể (8
plugin + helper `slugify`, và phần tô màu của `highlight`); chỉ viết mới ở những chỗ
built-in *về bản chất* không đáp ứng được: **đa ngôn ngữ** (collections/taxonomy/rss
mù locale), **đóng cứng cấu hình** (extension markdown, CSS highlight, đường dẫn
asset), **thiếu tính năng** (redirects), và **mất seam Jinja global** (buộc tiền
tính). Mỗi điểm này đều không thể giải quyết bằng kế thừa vì logic built-in nằm ở
hàm module chứ không phải method override được.
