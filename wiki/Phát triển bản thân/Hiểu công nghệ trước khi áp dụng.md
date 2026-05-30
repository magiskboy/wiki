---
tags:
  - mindset
date: 2026-05-29
---
# Hiểu công nghệ trước khi áp dụng

Công nghệ mới có sức hút mạnh với lập trình viên, đặc biệt với thực tập sinh và người mới ra trường. Tuy nhiên việc đưa một công nghệ vào sử dụng khi chưa hiểu cách nó vận hành dẫn tới dùng sai cách, không kiểm soát được hệ thống và luôn bị động khi xử lý lỗi hoặc khi cần mở rộng. Hiểu công nghệ trước khi áp dụng là nguyên tắc đặt sự thông hiểu lên trước sự tiện lợi của việc dùng ngay một giải pháp có sẵn.

Phương pháp học tập hiệu quả để hiểu một công nghệ là tự cài đặt lại phần lõi của nó trước khi dùng bản đóng gói. Khi học AI, thay vì dùng ngay tensorflow hay keras, người học viết các hàm Python cho từng công thức toán học, sau đó mới dùng scikit-learn cho tính toán thống kê, và cuối cùng mới dùng tensorflow. Khi học backend, thay vì dùng async task queue có sẵn, người học bắt đầu xây task queue từ thread, TCP và Redis. Trình tự này giúp người học nắm được cơ chế bên dưới trước khi tin tưởng vào lớp trừu tượng do thư viện cung cấp.

Một con đường khác để hiểu công nghệ mà không cần viết lại từ đầu là đọc source code của các repository nổi tiếng trên các nền tảng như GitHub, quan sát cách người khác sử dụng công nghệ đó và trong hoàn cảnh nào. Không có tài liệu nào mô tả công nghệ chính xác hơn source code của chính nó, và không ai hiểu công nghệ rõ hơn tác giả của nó.

# Nguồn tham khảo

- [Mình rút ra được những bài học gì sau 4 năm làm lập trình viên - Phần 1](https://www.nkthanh.dev/posts/minh-rut-ra-duoc-nhung-bai-hoc-gi-sau-4-nam-lam-lap-trinh-vien-phan-1)
- [Mình rút ra được những bài học gì sau 4 năm làm lập trình viên - Phần 2](https://www.nkthanh.dev/posts/minh-rut-ra-duoc-nhung-bai-hoc-gi-sau-4-nam-lam-lap-trinh-vien-phan-2)

# Liên kết tri thức

- [Tư duy theo bản chất vấn đề](./T%C6%B0%20duy%20theo%20b%E1%BA%A3n%20ch%E1%BA%A5t%20v%E1%BA%A5n%20%C4%91%E1%BB%81.md) - Hiểu cơ chế bên dưới một công nghệ chính là nắm được bản chất của nó
- [Rèn luyện tư duy giải quyết vấn đề](./R%C3%A8n%20luy%E1%BB%87n%20t%C6%B0%20duy%20gi%E1%BA%A3i%20quy%E1%BA%BFt%20v%E1%BA%A5n%20%C4%91%E1%BB%81.md) - Đọc source code và cài đặt lại công nghệ là phương pháp rèn luyện chung
- [Giá trị của kiến thức nền tảng](./Gi%C3%A1%20tr%E1%BB%8B%20c%E1%BB%A7a%20ki%E1%BA%BFn%20th%E1%BB%A9c%20n%E1%BB%81n%20t%E1%BA%A3ng.md) - Hiểu công thức toán học bên dưới một thư viện AI dựa trên nền tảng đã học
- [Dựng lại để hiểu sâu](./D%E1%BB%B1ng%20l%E1%BA%A1i%20%C4%91%E1%BB%83%20hi%E1%BB%83u%20s%C3%A2u.md) - Dựng lại là phương pháp triệt để nhất cụ thể hoá nguyên tắc hiểu công nghệ trước khi áp dụng
