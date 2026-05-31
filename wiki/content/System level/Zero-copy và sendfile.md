---
tags:
  - web
date: 2026-05-29
---
# Zero-copy và sendfile

Zero-copy là kỹ thuật truyền dữ liệu giảm tối đa số lần sao chép dữ liệu giữa các vùng nhớ. `sendfile` là system call của hệ điều hành cho phép di chuyển dữ liệu trực tiếp giữa hai file descriptor ngay dưới tầng kernel, không phải nạp dữ liệu lên tầng ứng dụng qua RAM. Nhờ đó giảm đáng kể thời gian, số lần copy và chi phí context switch giữa user space và kernel space.

## Vấn đề mà zero-copy giải quyết

Cách truyền file truyền thống (đọc file rồi ghi ra socket ở tầng ứng dụng) phải copy dữ liệu nhiều lần: từ disk vào page cache của kernel, từ kernel lên buffer của ứng dụng, từ buffer ứng dụng trở lại kernel buffer của socket, rồi mới ra network card. Mỗi lần copy tốn CPU và bộ nhớ. `sendfile` (có trên Unix hiện đại, Linux từ kernel 2.1) cho phép kernel gửi dữ liệu từ page cache thẳng tới socket, chỉ còn lần copy cuối tới buffer của network card.

## Ứng dụng trong Kafka

Zero-copy là một trong những kỹ thuật cốt lõi giúp Kafka đạt throughput cao. Kafka dùng `sendfile` (qua `FileChannel.transferTo` của Java NIO) để gửi dữ liệu log từ disk thẳng ra socket cho consumer mà không nạp qua bộ nhớ ứng dụng JVM. Một lưu ý quan trọng: bật TLS sẽ vô hiệu hóa zero-copy, vì dữ liệu phải được mã hóa ở tầng ứng dụng nên không thể đi thẳng từ page cache ra socket.

## Giới hạn trong ASGI

Core spec của ASGI gửi response body dưới dạng các message `http.response.body` chứa bytes ở tầng ứng dụng Python, nên không tận dụng được `sendfile` - dữ liệu file vẫn phải đi qua bộ nhớ Python. Đây là hạn chế khi phục vụ file tĩnh kích thước lớn.

ASGI bổ sung khả năng này qua hai extension tùy chọn: `http.response.pathsend` (ứng dụng gửi đường dẫn tuyệt đối của file, server tự `sendfile`, không trộn với `http.response.body`) và `http.response.zerocopysend` (ứng dụng truyền một file descriptor để server gọi `os.sendfile`, có thể trộn với body). Các extension này chỉ dùng được khi cả server (ví dụ Granian, Hypercorn) và ứng dụng cùng hỗ trợ.

## Nguồn tham khảo

- [Viết HTTP/2 server tương thích ASGI trong Python](https://www.nkthanh.dev/posts/implement-an-asgi-compatible-http2-server-in-python)
- [ASGI Extensions - pathsend, zerocopysend](https://asgi.readthedocs.io/en/latest/extensions.html)
- [What is Zero Copy in Kafka?](https://www.nootcode.com/knowledge/en/kafka-zero-copy)
- [Kafka Design - Efficiency (sendfile)](https://docs.confluent.io/platform/current/kafka/design.html)

## Liên kết tri thức

- [Bài toán C10K - giới hạn sendfile của ASGI nảy sinh khi tối ưu web server](../Web%20development/B%C3%A0i%20to%C3%A1n%20C10K.md)
- [WSGI và ASGI - sendfile là khả năng nằm ngoài core spec của ASGI](../Web%20development/WSGI%20v%C3%A0%20ASGI.md)
- [HTTP/2 và web server bất đồng bộ - phục vụ file tĩnh là ngữ cảnh cần zero-copy](../Web%20development/HTTP-2%20v%C3%A0%20web%20server%20b%E1%BA%A5t%20%C4%91%E1%BB%93ng%20b%E1%BB%99.md)
