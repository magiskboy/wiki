---
tags:
  - web
date: 2026-05-29
---
# Giới hạn kích thước header để khống chế bộ nhớ server

HTTP parser phải đệm toàn bộ một header trước khi emit ra application — vì name và value chỉ có nghĩa khi đủ một dòng kết thúc bằng `\r\n`. Nếu server cho phép header tuỳ ý lớn, một attacker (hoặc client hỏng) gửi header dài 1MB sẽ buộc parser cấp phát 1MB buffer cho mỗi connection. Ở quy mô cao, bộ nhớ phình theo số connection × kích thước header tối đa — đến mức không tồn tại máy nào chịu nổi. Đây là lý do mọi production HTTP server đều giới hạn header size, và lý do nên hiểu phép tính này khi thiết kế server hiệu năng cao.

## Phép tính minh hoạ

Một back-of-envelope estimation từ tác giả [http-parser](https://github.com/magiskboy/http-parser):

> Server xử lý 1.000.000 request/s, header tối đa cho phép 1MB → bộ nhớ in-flight có thể tới (1.000.000 × 1MB) ≈ 1TB.

Phép tính này dùng "kịch bản tệ nhất đồng thời" để cho thấy: cho phép header lớn ngầm chấp nhận bộ nhớ vô hạn. Production server không chấp nhận. Cách khống chế chuẩn là giới hạn buffer ở tầng parser — buffer size không vượt một ngưỡng cố định, vượt thì reject với 413/431.

## Default của các production server

Default của các server phổ biến nằm trong khoảng 4-32KB, không gần 1MB:

- **Nginx**: `client_header_buffer_size 1k` cho header nhỏ, `large_client_header_buffers 4 8k` cho header lớn — tổng tối đa 32KB cho một request line + tất cả header
- **Apache httpd**: `LimitRequestFieldSize 8190` mặc định (8KB cho một field), `LimitRequestFields 100` (số field tối đa)
- **Go net/http**: `Server.MaxHeaderBytes` mặc định `1 << 20` = 1MB (cao bất thường, nên override trong production)
- **Node.js http**: `--max-http-header-size=16384` mặc định 16KB (giảm từ 80KB từ 2018 sau CVE-2018-12121)

Sự khác biệt giữa Nginx/Apache (KB) và Go/Node mặc định (MB) phản ánh phong cách thiết kế: Nginx/Apache xuất thân từ web hosting đa khách hàng nên paranoid về bảo mật và bộ nhớ; Go/Node mặc định cho hyper-developer setup nên thư thái hơn.

## Heuristic chọn ngưỡng

Công thức ngược: cho memory budget mỗi worker `M` và số kết nối đồng thời cần phục vụ `C`, ngưỡng header tối đa là:

```
max_header_size ≤ M / (C × safety_factor)
```

Ví dụ một worker có 512MB ngân sách, phục vụ 10.000 connection đồng thời, safety_factor 4 (để chừa cho body, scope, task) → max_header_size ≤ 12.8KB. Khớp với default của Nginx/Apache.

Phép tính này gắn chặt với [backpressure ở tầng C10K](./B%C3%A0i%20to%C3%A1n%20C10K.md): khi parser đệm header vượt ngưỡng, server reject ngay thay vì cố hoàn thành — đây cũng là một dạng backpressure đẩy ngược về client.

## Trải nghiệm cá nhân

Đây là một trong những bài học rút ra khi viết [http-parser](https://github.com/magiskboy/http-parser) bằng C (Teko era) — parser dùng buffer cố định `char token[4096]` thay vì dynamic allocation, khớp với triết lý "biết trước max size để budget chính xác". README repo cũng ghi phép tính 1TB như cảnh báo rõ ràng cho người đọc.

## Nguồn tham khảo

- [README magiskboy/http-parser - mục What do we learn from it](https://github.com/magiskboy/http-parser/blob/main/README.md)
- [Nginx - client_header_buffer_size và large_client_header_buffers](https://nginx.org/en/docs/http/ngx_http_core_module.html#client_header_buffer_size)
- [Apache - LimitRequestFieldSize](https://httpd.apache.org/docs/current/mod/core.html#limitrequestfieldsize)
- [Go - net/http Server.MaxHeaderBytes](https://pkg.go.dev/net/http#Server)
- [Node.js CVE-2018-12121 - DoS via large HTTP headers](https://nvd.nist.gov/vuln/detail/CVE-2018-12121)

## Liên kết tri thức

- [HTTP parser dạng máy trạng thái - parser phải đệm header tới khi đủ một dòng, là lý do giới hạn buffer là cần thiết](./HTTP%20parser%20d%E1%BA%A1ng%20m%C3%A1y%20tr%E1%BA%A1ng%20th%C3%A1i.md)
- [Bài toán C10K - giới hạn header là một mảnh trong khung backpressure tổng thể của server cao tải](./B%C3%A0i%20to%C3%A1n%20C10K.md)
- [Backpressure ở tầng transport trong asyncio - cùng triết lý đẩy áp lực ngược về client, nhưng ở tầng truyền byte thay vì parser](../System%20level/Backpressure%20%E1%BB%9F%20t%E1%BA%A7ng%20transport%20trong%20asyncio.md)
- [Arbiter và worker trong ASGI server - mỗi worker có ngân sách bộ nhớ riêng, là biến số chính trong phép tính chọn ngưỡng header](./Arbiter%20v%C3%A0%20worker%20trong%20ASGI%20server.md)
