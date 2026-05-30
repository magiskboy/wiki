# Phỏng vấn khai quật: gist (4 subdir về threading Python)

- **Leaf**: Collection snippets cá nhân — Personal > Tooling cá nhân
- **Repo**: https://github.com/magiskboy/gist — mirror local: `references/repos/gist/`
- **Scope phỏng vấn**: 4 subdir cùng được dump trong commit đầu (2023-07-12)
  - `socket-programming-in-python/`
  - `simple-http-server-with-socket-and-asyncio/`
  - `simple-http-parser/`
  - `threading-processing-in-python/`
- **Wiki node hiện có (từ source)**: [http-parser-dang-may-trang-thai](../../wiki/Web%20development/HTTP%20parser%20d%E1%BA%A1ng%20m%C3%A1y%20tr%E1%BA%A1ng%20th%C3%A1i.md) — extract từ `simple-http-parser/`
- **Phiên phỏng vấn**: 2026-05-24

## Bối cảnh

- [Trí nhớ] Các snippet thu thập rải rác trên *Gist GitHub* từ rất lâu trước, ngày 2023-07-12 chỉ là ngày gom vào một repo duy nhất.
- [Trí nhớ + Chưa chắc] Mối liên hệ thời gian với xthread (commit 2023-07-13) "mỏng manh" — đơn thuần là *rảnh + đang quan tâm threading Python*, không có drive cụ thể như chuẩn bị talk hay job-hunt.
- [Trí nhớ] 4 subdir là chuỗi học có chủ đích về *threading Python* (xác định trục là threading, không phải networking nói chung).

## Mệnh đề khởi sinh của chuỗi

- [Trí nhớ] Câu hỏi gốc: *"Nếu GIL cản hiệu năng threading, threading có giá trị gì trong Python?"*
- [Trí nhớ] Hypothesis tự dựng: threading có lợi thế khi xử lý I/O-bound — vì thời gian thread bị suspend do thread khác giữ GIL trùng với thời gian thread đang chờ I/O, nên *suspend overlap với wait* và tổng thể quá trình vẫn tiếp diễn.
- [Trí nhớ] Quyết định: làm chuỗi *threading + socket* để **thử nghiệm lý thuyết của chính mình**.

## Vai trò của từng subdir

User xác nhận hoàn toàn cách phân vai sau:

- [Trí nhớ] `threading-processing-in-python` — **chứng cứ thực nghiệm về GIL**: benchmark single-thread vs multi-thread vs multi-process cho CPU-bound (fib(40)) và I/O-bound (HTTP request).
- [Trí nhớ] `socket-programming-in-python` — **3 paradigm I/O thay cho threading**: blocking với selector+generator (echo-server), callback-base client, coroutine-base client với Future+Task.
- [Trí nhớ] `simple-http-parser` — **viên gạch nền** cho async server: parser dạng máy trạng thái cho phép parse HTTP qua nhiều chunk TCP.
- [Trí nhớ] `simple-http-server-with-socket-and-asyncio` — **kết tinh**: ráp paradigm coroutine + parser + URL routing tự cài thành một HTTP server đầy đủ.

## Thứ tự thực hiện

- [Trí nhớ] Không có thứ tự cụ thể — 4 subdir làm *rải rác trong thời gian rảnh*, song song chứ không tuần tự.
- [Bổ sung — quan sát của assistant] Nuance đáng chú ý: chuỗi có chủ đích về *chủ đề* (deep-dive threading) nhưng không có chủ đích về *thứ tự thực hiện*. Đây là pattern học khác với phong cách tuyến tính của giáo trình — gần với research-style exploration.

## Surprise và khác biệt với cliché

- [Trí nhớ] Không surprise lớn. Chút surprise nhẹ: kết quả threading vs single-thread vs multiprocess theo I/O-bound vs CPU-bound *không khớp với 2 cliché phổ biến*:
  - "Threading trong Python luôn tăng hiệu năng" — sai
  - "Threading trong Python luôn giảm hiệu năng (do GIL)" — cũng sai
  - Thực tế: kết quả phụ thuộc workload type, không có generalization đơn giản. Đây trở thành kiến thức nền cốt lõi sau này dùng cho FastAPI thiết kế async/sync endpoint, uvicorn worker model, v.v.

## Kết tinh và cầu nối tới uASGI

- [Trí nhớ] Kết tinh sau cùng của chuỗi gist + xthread là **uASGI** — chứng minh "Python có thể tạo webserver tận dụng hiệu năng tối đa".
- [Trí nhớ] Kiến thức từ chuỗi gist có *trước* khi viết uASGI, nhưng:
- [Chưa chắc] Không khẳng định bạn có *ý định viết uASGI sẵn từ 2023*. Có vẻ uASGI là **kết tinh hồi cứu** (retrospective crystallization) của kiến thức tích lũy, hơn là kế hoạch dài hạn đặt sẵn.

## Vòng cung 2 năm — phát hiện meta của phiên này

```
2023-07-12: gist (4 subdir threading)
  → thử nghiệm lý thuyết "threading có giá trị cho I/O"

2023-07-13 → 07-14: xthread
  → abstraction threading có chủ kiến, kết quả 1 chuỗi reflection

2025-07-11 → 08-24: uASGI (commit liên tục 6 tuần) + blog HTTP/2 (07-13)
  → kết tinh: webserver Python hiệu năng cao
  → chia sẻ public qua blog

Mỗi giai đoạn cách nhau ~2 năm. Toàn bộ là một dự án học dài hạn về
"Python low-level networking + threading + async", không phải 3 mảnh rời.
```

## Mở rộng đồ thị từ phiên này

Hai ứng viên node mới:

1. **"Dựng lại để hiểu sâu"** (mindset) — pattern học sâu chung của bạn xuyên suốt nhiều dự án (gist HTTP parser, gist HTTP server, xthread, uasgi, http-parser C, oauth2-impl, voting-blockchain). Reimplementation as learning method. Phổ biến hơn 1 phiên này nên đáng tách riêng.
2. **"Thử nghiệm hypothesis tự dựng"** (mindset) — methodology: tự đặt mệnh đề rồi tự thực nghiệm. Hẹp hơn nhưng rõ nét. Có thể fold vào node 1 hoặc tách riêng.

Hai node trên có thể là một, cùng cụm với [hieu-cong-nghe-truoc-khi-ap-dung](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Hi%E1%BB%83u%20c%C3%B4ng%20ngh%E1%BB%87%20tr%C6%B0%E1%BB%9Bc%20khi%20%C3%A1p%20d%E1%BB%A5ng.md), [gia-tri-cua-kien-thuc-nen-tang](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Gi%C3%A1%20tr%E1%BB%8B%20c%E1%BB%A7a%20ki%E1%BA%BFn%20th%E1%BB%A9c%20n%E1%BB%81n%20t%E1%BA%A3ng.md), [toi-uu-hoa-dua-tren-bang-chung](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/T%E1%BB%91i%20%C6%B0u%20h%C3%B3a%20d%E1%BB%B1a%20tr%C3%AAn%20b%E1%BA%B1ng%20ch%E1%BB%A9ng.md).
