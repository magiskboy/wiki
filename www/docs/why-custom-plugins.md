# Vì sao (vẫn) còn plugin tự viết — sau khi lên pyssg 0.2.0

Tài liệu này từng giải thích vì sao **không** dùng lại được plugin built-in của
pyssg **0.1.0**. pyssg **0.2.0** đã cấu hình-hoá gần hết những điểm đó, nên site
đã gỡ bỏ phần lớn plugin riêng. Bản này ghi lại: cái gì đã thay được bằng
built-in, và cái gì *bản chất* vẫn phải tự viết.

Tham chiếu mã built-in: `.venv/lib/python3.13/site-packages/pyssg/plugins/`.
Tài liệu: <https://pyssg.nkthanh.dev>.

---

## TL;DR

- 0.2.0 làm `collections` / `taxonomy` / `rss` **i18n-aware** (sinh trang & feed
  theo từng locale, gom term theo slug), thêm `redirects` built-in và
  `asset_copy(mounts=...)`, và cho `markdown(extensions=...)`. ⇒ Sáu plugin tự
  viết cũ của www **bị xoá hẳn**.
- Chỉ còn **hai** mảnh không cấu hình-hoá được, vì lý do kiến trúc cốt lõi:
  1. `render` vẫn **không expose seam đăng ký Jinja filter/global** ⇒ vẫn phải
     *tiền tính* dữ liệu đã định dạng theo locale (ngày kiểu Việt, link tag, mô
     tả render markdown). Gói trong `WwwEnrich` + subclass `WwwCollections`.
  2. `highlight` chỉ nhận **một** `style` ⇒ CSS code đa `data-theme`
     (light/dark/papyrus) vẫn do `HighlightThemes` sinh.

---

## Những gì 0.2.0 đã thay được (đã xoá plugin tự viết)

| Nhu cầu | Plugin cũ (đã xoá) | Thay bằng (0.2.0) |
|---|---|---|
| Thêm `arithmatex` cho công thức | `WwwMarkdown` | `markdown(extensions=[ArithmatexExtension(...)])` |
| Danh sách bài phân trang theo locale | `WwwCollections`¹ | `collections(CollectionSpec(...))` (i18n-aware) |
| Tag/category theo locale, gom theo slug | `WwwTaxonomy` | `taxonomy()` (i18n-aware, gom slug sẵn) |
| Feed RSS theo locale, có guid/pubDate | `WwwRss` | `rss()` (tách `/feed.xml` + `/en/feed.xml`) |
| Chuyển hướng URL cũ | `Redirects` | `redirects(rules=...)` |
| Copy `static/` ra gốc | `StaticFiles` | `asset_copy(mounts=[("static", "/")])` |

¹ `WwwCollections` **không bị xoá hẳn** mà rút thành subclass mỏng của
`CollectionsPlugin` (chỉ override `make_item`/`item_to_dict`) — xem dưới.

Đáng chú ý: bug "`Python` và `python` cùng slug đè trang nhau" mà bản tự viết
phải xử lý nay đã được built-in `taxonomy` gom-theo-slug lo sẵn.

---

## Những gì *vẫn* phải tự viết

### 1. `WwwEnrich` + `WwwCollections` — vì `render` chưa có seam Jinja

`RenderPlugin` dựng `jinja2.Environment` bên trong và chỉ tiêm hàm `t(...)`;
không có cách đăng ký global/filter như `format_date()`. Hệ quả: ngày địa phương
hoá ("Thứ X, ngày D tháng M năm Y" / "March 19, 2021"), `tag_links`, và mô tả
render-markdown phải **tính sẵn** chứ template không tự gọi được.

- `WwwEnrich`: tap `parse`, bơm `date_display` / `tag_links` /
  `description_html` (+ cờ `math`) vào `doc.meta` cho **trang bài đơn**.
- `WwwCollections(CollectionsPlugin)`: override `make_item` (giữ mô tả curated)
  và `item_to_dict` (thêm `date_display` / `description` / `tag_links`) cho **thẻ
  bài** ở trang danh sách. Toàn bộ phân trang + i18n vẫn của built-in.

### 2. `HighlightThemes` — vì `highlight` chỉ một style

Built-in `highlight` chỉ bơm **một** stylesheet vào `config.site["highlight_css"]`,
scope `.highlight`. Site đổi giao diện bằng `data-theme` nên cần **3** stylesheet,
mỗi cái scope dưới `[data-theme="..."]`. `HighlightThemes` ghi đè
`config.site["highlight_css"]` bằng CSS đa-theme.

---

## Đánh đổi khi chuyển template sang built-in

Vì dùng context của built-in (đã rewrite `list/term/terms.html.j2`):

- **Trang term `/tags/<x>/`**: built-in chỉ mang `{title, url}` cho mỗi member ⇒
  hiển thị **danh sách link tiêu đề** thay vì thẻ bài đầy đủ như trước. Cùng tập
  bài. Muốn lấy lại thẻ đầy đủ thì cần thêm subclass `taxonomy` để enrich member.
- **Thứ tự trang index** `/tags/`, `/categories/`: built-in sort phân biệt
  hoa/thường; chỉ khác thứ tự hiển thị.
- **RSS**: feed có thêm `guid isPermaLink`; bỏ `<description>` cấp channel.

---

## Ghi chú cho wiki

Wiki (`../wiki/`) lên 0.2.0 nhưng **giữ nguyên** plugin riêng: codehilite (giữ
class CSS sẵn có; built-in `mermaid()` không dùng được vì codehilite nuốt fence
mermaid trước), đồ thị tri thức từ prose, category theo thư mục cha, dashboard.
Đây là **tính năng bespoke**, không phải workaround cấu hình thiếu, nên 0.2.0
không thay được — chỉ hưởng lợi gián tiếp (RSS có guid/pubDate).
