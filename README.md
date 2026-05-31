# Knowledge

Kho này dùng để lưu tri thức cá nhân dưới dạng Markdown, ưu tiên các ghi chú ngắn, có nguồn tham khảo, có liên kết giữa các mảnh tri thức và có tag để phân loại.

## Cấu trúc

- `wiki/`: dự án [pyssg](https://github.com/magiskboy/pyssg) build kho tri thức thành site tĩnh.
  - `wiki/content/`: nơi lưu các trang tri thức chính (một thư mục mỗi category).
  - `wiki/content/_index.md`: mục lục các trang tri thức.
  - `wiki/content/_tags.md`: danh sách tag đang dùng trong kho.
  - `wiki/pyssg.config.py`, `wiki/plugins/`, `wiki/layouts/`, `wiki/static/`: cấu hình, plugin và giao diện của site.
- `.agents/skills/`: quy tắc và phương pháp làm việc với kho tri thức (mỗi skill là một thư mục chứa `SKILL.md`).
- `references/`: nguồn tham khảo đáng tin cậy, gồm `references/interviews/` lưu transcript phỏng vấn khai quật làm primary source.
- `_source/`: vùng staging **tạm thời** cho việc migrate tri thức từ trí nhớ (xem [`_source/README.md`](./_source/README.md)); xoá được sau khi migrate xong.

## Cách dùng

Đọc tri thức từ [`wiki/content/_index.md`](./wiki/content/_index.md), sau đó đi theo các liên kết trong từng trang để mở rộng ngữ cảnh.

Khi thêm tri thức mới, hãy tạo một file Markdown trong `wiki/content/`, đặt tên ngắn gọn theo khái niệm chính, cập nhật lại `wiki/content/_index.md`, và dùng tag có sẵn trong `wiki/content/_tags.md` hoặc bổ sung tag mới nếu cần.

Mỗi trang tri thức nên có tiêu đề rõ ràng, nội dung ngắn gọn, nguồn tham khảo, liên kết tới các trang liên quan và danh sách tag. Quy tắc chi tiết nằm trong [`.agents/skills/add-knowledge/SKILL.md`](./.agents/skills/add-knowledge/SKILL.md).

## Build site

Site tĩnh được build bằng pyssg (cần Python ≥ 3.13). Chạy trong thư mục `wiki/`:

```bash
cd wiki
uv venv && uv pip install "pyssg[plugins] @ git+https://github.com/magiskboy/pyssg" pymdown-extensions
.venv/bin/pyssg build      # build ra wiki/public/
.venv/bin/pyssg serve      # dev server kèm live-reload
```
