# Knowledge

Kho này dùng để lưu tri thức cá nhân dưới dạng Markdown, ưu tiên các ghi chú ngắn, có nguồn tham khảo, có liên kết giữa các mảnh tri thức và có tag để phân loại.

## Cấu trúc

- `wiki/`: nơi lưu các trang tri thức chính.
- `wiki/_index.md`: mục lục các trang tri thức.
- `wiki/_tags.md`: danh sách tag đang dùng trong kho.
- `.agents/skills/`: quy tắc và phương pháp làm việc với kho tri thức (mỗi skill là một thư mục chứa `SKILL.md`).
- `references/`: nguồn tham khảo đáng tin cậy, gồm `references/interviews/` lưu transcript phỏng vấn khai quật làm primary source.
- `_source/`: vùng staging **tạm thời** cho việc migrate tri thức từ trí nhớ (xem [`_source/README.md`](./_source/README.md)); xoá được sau khi migrate xong.

## Cách dùng

Đọc tri thức từ [`wiki/_index.md`](./wiki/_index.md), sau đó đi theo các liên kết trong từng trang để mở rộng ngữ cảnh.

Khi thêm tri thức mới, hãy tạo một file Markdown trong `wiki/`, đặt tên ngắn gọn theo khái niệm chính, cập nhật lại `wiki/_index.md`, và dùng tag có sẵn trong `wiki/_tags.md` hoặc bổ sung tag mới nếu cần.

Mỗi trang tri thức nên có tiêu đề rõ ràng, nội dung ngắn gọn, nguồn tham khảo, liên kết tới các trang liên quan và danh sách tag. Quy tắc chi tiết nằm trong [`.agents/skills/add-knowledge/SKILL.md`](./.agents/skills/add-knowledge/SKILL.md).
