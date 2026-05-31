---
tags:
  - web
date: 2026-05-29
---
# Callback qua function pointer trong C

C không có class hay virtual method để dispatch callback theo kiểu OOP, nhưng có function pointer — cùng cơ chế ở tầng thấp hơn. Một callback trong C là một con trỏ tới hàm được lưu trong struct hoặc truyền làm tham số; caller invoke qua con trỏ đó như gọi hàm thường. Pattern này là cách C đạt được polymorphism động: cùng một parser/event loop/sort routine có thể chạy với behavior khác nhau tuỳ con trỏ được đăng ký.

## Cấu trúc cơ bản

Khai báo trong header: kiểu con trỏ hàm là một phần của struct. Mỗi field con trỏ định nghĩa một "slot" mà người dùng có thể plug vào hành vi tuỳ chỉnh.

```c
struct parser_t {
    char token[4096];
    enum STATE state;

    void (*on_method)(char*);
    void (*on_url)(char*);
    void (*on_header)(char*, char*);
    void (*on_headers_completed)(void);
    void (*on_body)(char*);
};
```

Người dùng đăng ký callback bằng cách gán con trỏ:

```c
void my_on_method(char *m) { printf("Method: %s\n", m); }

struct parser_t parser;
parser.on_method = &my_on_method;
```

Parser invoke callback như gọi hàm bình thường, không cần `(*parser.on_method)(token)` vì C tự dereference con trỏ hàm khi đứng trước `()`:

```c
parser->on_method(parser->token);
```

## Ngữ nghĩa: late binding ở tầng C

Tại compile time parser không biết hàm cụ thể nào sẽ chạy — nó chỉ biết signature. Lúc runtime con trỏ được lookup từ struct và invoke. Đây là tương đương low-level của virtual table trong C++: cả hai đều là indirect call qua một con trỏ được set ở runtime, nhưng C++ tự sinh table, còn C bắt người dùng tự khai báo từng slot.

Một lợi điểm của pattern này so với hardcode: parser được tách rời khỏi consumer. Cùng một `pparser_parse` có thể được dùng để in ra stdout (như `main.c`), để build scope cho ASGI server, hay để build object cho ORM — chỉ cần đổi callback đăng ký.

## Ứng dụng tiêu biểu

Function pointer callback là một trong những pattern phổ biến nhất trong C library:

- `qsort` của libc — comparator là function pointer
- `signal()` của POSIX — handler là function pointer
- libuv — mọi event handler (read, write, timer, idle) đều là function pointer
- GLib/GTK signal — callback đăng ký vào signal slot bằng function pointer
- HTTP parser của Node.js (llhttp), libcurl, OpenSSL — đều theo pattern này

## Đánh đổi cần biết

Pattern này gọn nhưng có vài điểm phải tự quản:

- **Lỗi NULL** — quên gán callback thì invoke con trỏ NULL → segfault. Parser nên check `if (parser->on_method != NULL)` trước khi gọi, hoặc set default no-op handler.
- **Không có closure** — C không capture được biến ngoài như JavaScript hay Python. Để truyền context, pattern thường thấy là kèm `void* user_data` vào callback signature: `void (*on_method)(char*, void* user_data)`.
- **Lifetime của hàm callback** — phải đảm bảo hàm còn tồn tại khi callback được gọi; không phải vấn đề với hàm tĩnh nhưng cần cẩn thận với function pointer trỏ tới hàm trong shared library bị unload.

## Trải nghiệm cá nhân

Pattern này được dùng cụ thể trong [http-parser](https://github.com/magiskboy/http-parser) — bản C song hành với HTTP parser Python trong gist; cả hai cùng một state machine, khác nhau ở chỗ Python dùng object có method còn C dùng struct chứa function pointer. Mục đích: thực hành cùng pattern trên hai ngôn ngữ để thấy rõ "kiểu OOP" thực ra là một dạng dressed-up của function pointer indirect call.

## Nguồn tham khảo

- [Source magiskboy/http-parser - pparser.h declare callback struct](https://github.com/magiskboy/http-parser/blob/main/pparser.h)
- [Source magiskboy/http-parser - main.c đăng ký callback](https://github.com/magiskboy/http-parser/blob/main/main.c)
- [Function Pointers in C - K&R The C Programming Language, chapter 5.11](https://en.wikipedia.org/wiki/The_C_Programming_Language)
- [qsort - libc reference](https://man7.org/linux/man-pages/man3/qsort.3.html)
- [libuv design overview - callback model](https://docs.libuv.org/en/v1.x/design.html)

## Liên kết tri thức

- [HTTP parser dạng máy trạng thái - cùng một state machine được cài bằng cả Python (object có method) và C (struct + function pointer)](../Web%20development/HTTP%20parser%20d%E1%BA%A1ng%20m%C3%A1y%20tr%E1%BA%A1ng%20th%C3%A1i.md)
- [Observer pattern - function pointer callback là phiên bản tầng thấp của observer; observer trong OOP che cùng cơ chế qua virtual method](./Observer%20pattern.md)
- [Dựng lại để hiểu sâu - cài lại cùng parser bằng cả Python và C là một ví dụ điển hình của reimplement để hiểu nguyên lý chung dưới mỗi ngôn ngữ](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/D%E1%BB%B1ng%20l%E1%BA%A1i%20%C4%91%E1%BB%83%20hi%E1%BB%83u%20s%C3%A2u.md)
