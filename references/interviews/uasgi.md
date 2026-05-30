# Phỏng vấn khai quật: uasgi

- **Leaf**: Implement ASGI server bằng pure Python (`_source/track.md` > Personal > Tự cài lại bằng tay)
- **Repo**: https://github.com/magiskboy/uasgi — mirror local: `references/repos/uasgi/`, version 0.4.0
- **Thời điểm repo**: 2025-07-11 → 2025-08-24 (23 commit, ~6 tuần liên tục), sau đó ngắt quãng tới gần đây
- **Wiki node hiện có (từ source)**:
  - [arbiter-va-worker-trong-asgi-server](../../wiki/Web%20development/Arbiter%20v%C3%A0%20worker%20trong%20ASGI%20server.md)
  - [lifespan-protocol-trong-asgi](../../wiki/Web%20development/Lifespan%20protocol%20trong%20ASGI.md)
  - [pipelining-trong-http](../../wiki/Web%20development/Pipelining%20trong%20HTTP-1.1.md)
  - [backpressure-tang-transport](../../wiki/System%20level/Backpressure%20%E1%BB%9F%20t%E1%BA%A7ng%20transport%20trong%20asyncio.md)
  - [hot-reload-bang-watchdog-va-signal](../../wiki/Web%20development/Hot%20reload%20server%20b%E1%BA%B1ng%20watchdog%20v%C3%A0%20signal.md)
- **Blog liên quan (cùng người viết)**: [Viết HTTP/2 server tương thích ASGI trong Python](../www/implement-an-asgi-compatible-http2-server-in-python.mdx), date 2025-07-13
- **Repo tutorial tiền-uasgi**: [magiskboy/python-webserver-tutorial](https://github.com/magiskboy/python-webserver-tutorial)
- **Phiên phỏng vấn**: 2026-05-24

## Bối cảnh

- [Trí nhớ] Thời điểm viết: 7-8/2025, đang ở Zen8labs. Code và commit liên tục là *thời gian rảnh* ở Zen8labs.
- [Trí nhớ] Động cơ chính: muốn hiểu cặn kẽ ASGI và cơ chế high-performance của các web server như Gunicorn, uvicorn; muốn hiểu cách Starlette, FastAPI tích hợp lên ASGI server.
- [Trí nhớ] uasgi là project *để hiểu*, không phải để dùng. Không có production use case cụ thể.
- [Trí nhớ] Tên "uasgi" — chữ `u` lấy cảm hứng từ uWSGI.
- [Trí nhớ] Chuỗi: prototype trong `magiskboy/python-webserver-tutorial` → blog [Viết HTTP/2 server tương thích ASGI trong Python](../www/implement-an-asgi-compatible-http2-server-in-python.mdx) (7/13/2025) → uasgi (productionized library).
- [Trí nhớ] Sẽ bổ sung WebSocket trong giai đoạn tiếp theo (chưa làm).

## Nguồn học và thiết kế

### Multi-process từ Gunicorn

- [Trí nhớ] Kiến trúc quản lý multi-process học từ Gunicorn (đọc source rất lâu trước khi viết uasgi).
- [Trí nhớ] Thích interface Gunicorn vì *dễ mở rộng* — đây là lý do thiết kế UASGIWorker để uasgi có thể chạy *bên trong* Gunicorn (drop-in worker compatibility).
- [Trí nhớ] Cách tích hợp với Gunicorn: pass-through socket từ Gunicorn xuống worker; toàn bộ parse information làm trong worker.
- [Trí nhớ] Tích hợp với Gunicorn dễ dàng, không có vùng vấp đáng nhớ.

### Async task từ uvicorn

- [Trí nhớ] Kiến trúc quản lý async task học từ uvicorn (cũng đọc source rất lâu trước).
- [Trí nhớ] HTTP pipelining (`deque` + `current_runner` trong `H11Protocol`) cài đặt bằng cách đọc hiểu flow của uvicorn rồi tự reimplement theo cách hiểu cá nhân, không sao chép trực tiếp.
- [Trí nhớ + đã mờ] "Bây giờ chỉ nhớ phần nào cơ chế đó" — chi tiết pipelining đã mờ.

### Protocol/Transport pattern từ Python docs

- [Trí nhớ] Pattern asyncio Protocol/Transport học từ trang chủ Python (docs.python.org). Đây là pattern làm việc với networking mà bạn nhận thấy là "đúng cách".
- [Trí nhớ] Tư duy về pattern này thể hiện trong blog [implement-an-asgi-compatible-http2-server-in-python.mdx](../www/implement-an-asgi-compatible-http2-server-in-python.mdx) — blog là design doc song hành với code.

### HTTP/2 từ AI + thư viện h2

- [Trí nhớ] Học HTTP/2 từ hai nguồn: trò chuyện với AI để hiểu spec, và đọc thư viện `h2` của python-hyper.
- [Trí nhớ] Tự cài đặt H2 trong uasgi không tham khảo source nào khác — vì đã nắm chắc pattern Protocol/Transport.

## Vai trò của AI

- [Trí nhớ] AI chỉ implement *WebSocket interface* (giai đoạn sau, có thể chưa trong repo public).
- [Trí nhớ] Toàn bộ HTTP/1.1, HTTP/2, arbiter, worker, lifespan, hot-reload do bạn tự viết, không có hỗ trợ AI.
- [Chưa chắc] Trong chùm 2 từng nói `set_dangerous_leniencies(lenient_data_after_close=True)` "có thể do AI"; trong chùm 3 đính chính AI chỉ làm WebSocket. Nguồn của dòng flag này chưa rõ — cần đọc lại git blame để xác minh.

## Tự đánh giá

### Phần tự hào

- [Trí nhớ] Quản lý coroutine (pipelining, lifecycle request,...) để đảm bảo hiệu năng cao.
- [Trí nhớ] Vận dụng pattern Protocol/Transport của Python cho networking — kiến thức này giúp việc thiết kế uasgi trở nên dễ.
- [Trí nhớ] Hiểu ASGI interface để tích hợp được Starlette, FastAPI một cách dễ dàng.

### Phần tự thấy yếu

- [Trí nhớ] Quản lý multiprocess / arbiter — chỉ dựa vào Gunicorn mà chưa hiểu thật chắc.
- [Trí nhớ] Implement HTTP/2 — học theo flow nhưng chưa thực sự vững.

### Quan sát nghịch lý

- [Bổ sung — quan sát của assistant] Wiki node [arbiter-va-worker-trong-asgi-server](../../wiki/Web%20development/Arbiter%20v%C3%A0%20worker%20trong%20ASGI%20server.md) được extract từ source code và phản ánh kiến trúc chính xác (fork+inherit fd, SIGINT broadcast, sendfile cho stdout pipe). User tự thấy yếu ở vùng này có thể vì *đã copy pattern Gunicorn mà chưa internalize cái "vì sao"*, chứ không phải vì code sai. Đây là gợi ý cho phiên khai quật thêm sau này — đào sâu vào "vì sao" để vá chỗ thấy yếu.

## Lifecycle

- [Trí nhớ] Dừng commit liên tục từ ~8/2025 vì hết thời gian rảnh ở Zen8labs.
- [Trí nhớ] Có commit ngắt quãng tới gần đây nhưng không liên tục.
- [Trí nhớ] Tương lai: hoàn thiện WebSocket subprotocol.

## Mở rộng đồ thị tri thức từ phiên này

- **uasgi là productionized version của python-webserver-tutorial**: nên thêm reference tới tutorial repo trong các wiki node liên quan (đặc biệt arbiter-va-worker, pipelining, lifespan).
- **Pattern Protocol/Transport đáng có node riêng**: bạn xác định đây là vùng *nắm chắc* và *tự hào*. Hiện tại chưa có wiki node tách riêng cho "asyncio Protocol và Transport pattern" — có thể là một leaf khai quật tiếp.
- **"Drop-in Gunicorn worker compatibility"**: design pattern thú vị (extend interface có sẵn để có thể plug vào ecosystem trưởng thành), đáng tách thành ghi chú design tự do.
- **Phần "yếu nhất tự nhận"** (multiprocess, HTTP/2): vùng còn nợ tri thức — không bít vào wiki node hiện có cho tới khi user thật sự internalize.
