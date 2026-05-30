---
tags:
  - python
date: 2026-05-29
---
# Điều khiển thread bằng cooperative event

Python không cung cấp API chính thống để dừng một thread đang chạy giữa chừng — không có cái tương đương `pthread_cancel` của POSIX hay `Thread.stop()` được khuyến cáo. Lý do là an toàn dữ liệu: nếu raise exception bất kỳ chỗ nào trong thread, lock có thể bị giữ vĩnh viễn, file descriptor mở dở, hoặc invariant của object bị phá. Cách "chính thống" duy nhất để báo hiệu dừng là dùng pattern cooperative: thread đích chủ động kiểm tra một flag dùng chung và tự thoát khi flag được set.

## Mẫu hình của xthread

xthread là thư viện cài đặt pattern này thành một wrapper quanh `threading.Thread`. Hai khả năng pause/unpause và stop non-preemptive đều dựa trên `threading.Event`:

- `__is_running` là event điều khiển vòng đời tổng. `stop()` clear event, vòng lặp wrapper thoát.
- `__resume` là event điều khiển pause. `pause()` clear event, `unpause()` set lại. Wrapper gọi `__resume.wait(pause_timeout)` sau mỗi lần chạy target, nên khi pause, thread block ở wait cho tới khi unpause hoặc timeout.

Target callable được gọi định kỳ trong vòng `while __is_running.is_set():` thay vì chạy một lần duy nhất. Đây là điểm cốt lõi của pattern: hợp đồng giữa thư viện và người dùng là target phải hoàn thành trong một burst ngắn, để wrapper có cơ hội kiểm tra event giữa các lần gọi.

```python
def wrapper():
    while self.__is_running.is_set():
        try:
            result = target(self, *args, **kwargs)
            self.__resume.wait(self.__pause_timeout)
        except Exception as e:
            self.__on_error(e)
```

Hệ quả: pattern này không thể dừng một target đang sleep dài hoặc đang chờ một syscall blocking — chừng nào target chưa return, wrapper không thể kiểm tra event.

## So với các cách "thật sự" preemptive

CPython có hàm `PyThreadState_SetAsyncExc` ở tầng C-API, cho phép raise một exception trong một thread khác tại điểm boundary giữa các opcode. Wrapper Python của nó là internal, không được expose chính thức, và Python doc cảnh báo rõ là "không an toàn nếu thread đích đang giữ lock". POSIX có `pthread_cancel` kèm cancellation point, an toàn hơn nhưng yêu cầu code phải có cleanup handler đúng cách.

So với hai cách trên, cooperative event đổi quyền điều khiển lấy an toàn: thread đích quyết định khi nào nó "an toàn để dừng" thay vì bị ép. Triết lý này gần với coroutine và event loop: tất cả đều dựa trên cộng tác thay vì preemption.

## Khi nào pattern này phù hợp

Pattern xthread phù hợp với các thread "polling" hoặc "periodic worker": kiểm tra hàng đợi, đọc sensor, tick game loop — nơi target tự nhiên chạy thành burst ngắn lặp đi lặp lại. Nó không thay thế được async cho I/O-bound (asyncio cho hiệu năng tốt hơn) và không phù hợp khi target là một tác vụ tuyến tính dài.

## Trải nghiệm cá nhân

Pattern này được kết tinh khi viết [xthread](https://github.com/magiskboy/xthread) tại Teko (7/2023) — dự án practice để giải bài toán nhiều dev dùng `threading.Thread` sai cách trong team SRE. Bài học sau cùng đọng lại: API gọn quan trọng hơn flexibility. Chi tiết bối cảnh và bài học trong [transcript phỏng vấn](../../references/interviews/xthread.md).

## Nguồn tham khảo

- [Source xthread - implementation](../../references/repos/xthread/xthread/__init__.py)
- [threading - Thread-based parallelism | Python documentation](https://docs.python.org/3/library/threading.html)
- [Python C API - PyThreadState_SetAsyncExc](https://docs.python.org/3/c-api/init.html#c.PyThreadState_SetAsyncExc)
- [Why Python's Thread.stop was deprecated](https://web.archive.org/web/20120206020829/http://docs.python.org/library/thread.html)

## Liên kết tri thức

- [Global Interpreter Lock trong Python - nền tảng giải thích vì sao raise exception giữa thread không an toàn](./Global%20Interpreter%20Lock%20trong%20Python.md)
- [Coroutine trong Python - cùng triết lý cộng tác, đơn vị tự nhường quyền điều khiển thay vì bị ép](./Coroutine%20trong%20Python.md)
- [Event loop trong Python - event loop là cooperative scheduler cấp cao hơn của cùng triết lý này](./Event%20loop%20trong%20Python.md)
- [Đơn giản hơn linh hoạt trong thiết kế API - xthread thừa tuỳ chọn so với nhu cầu thực, là nguồn rút ra bài học này](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/%C4%90%C6%A1n%20gi%E1%BA%A3n%20h%C6%A1n%20linh%20ho%E1%BA%A1t%20trong%20thi%E1%BA%BFt%20k%E1%BA%BF%20API.md)
- [Dựng lại để hiểu sâu - xthread là một ví dụ của dựng lại API threading để internalize cooperative concurrency](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/D%E1%BB%B1ng%20l%E1%BA%A1i%20%C4%91%E1%BB%83%20hi%E1%BB%83u%20s%C3%A2u.md)
- [Game loop cơ bản - game loop là cooperative scheduler cho frame, cùng triết lý "không block, hỏi định kỳ"](../Game%20development/Game%20loop%20c%C6%A1%20b%E1%BA%A3n.md)
- [Time-based movement thay vì sleep trong game loop - cùng nguyên lý cooperative áp dụng cho entity trong game](../Game%20development/Time-based%20movement%20thay%20v%C3%AC%20sleep%20trong%20game%20loop.md)
- [Cấp resource ở đâu, giải phóng ở đó - cùng triết lý "owner chủ động quyết định, không bị ép từ ngoài"](./C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md)
