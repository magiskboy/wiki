---
tags:
  - mindset
date: 2026-05-29
---
# Cấp resource ở đâu, giải phóng ở đó

Khi làm việc với low-level resource (memory, file descriptor, mutex, network socket, GPU texture) trong ngôn ngữ không có garbage collector tự quản — C, C++, Rust ở mức unsafe — một quy tắc đơn giản nhưng cứu nhiều giờ debug: *resource được cấp ở đâu thì ở đó chịu trách nhiệm giải phóng.* Quy tắc này là phát biểu dân dụng của hai khái niệm lớn trong C++: RAII và ownership.

## Vì sao chia resource ownership ra nhiều nơi dẫn tới bug

Khi resource được cấp ở class A và giải phóng ở class B, có ba loại bug khó tránh:

- **Double-free** — A tự `free` rồi B `free` lại pointer cũ. Trên Linux, allocator có thể đã reuse vùng nhớ đó cho object khác, double-free phá luôn object đó. Thường lộ ra dưới dạng segfault hoặc heap corruption ở chỗ hoàn toàn khác.
- **Use-after-free** — A đã `free`, B vẫn dùng pointer cũ. Đọc rác hoặc segfault.
- **Memory leak** — cả A và B đều nghĩ bên kia sẽ free, không ai free.

Triệu chứng phổ biến nhất là *segfault xảy ra ở chỗ tưởng chừng không liên quan* — vì tại điểm crash, code chỉ là nạn nhân, thủ phạm là một `free` sai chỗ ở xa.

## RAII — ràng buộc resource vào object lifecycle

C++ giải bài toán này bằng RAII (Resource Acquisition Is Initialization), thuật ngữ do Bjarne Stroustrup đặt khi cùng Andrew Koenig phát triển kỹ thuật trong giai đoạn 1984–1989 cho exception-safe resource management. Ý tưởng: *acquire resource trong constructor, release trong destructor.* Object còn sống thì resource còn được giữ; object bị huỷ là resource tự động được trả lại.

Hệ quả: class invariant ràng buộc "object exists" với "resource is held". Nếu không có object leak thì không có resource leak — Wikipedia diễn đạt là *"if there are no object leaks, there are no resource leaks"*. Stroustrup cũng nói: *"In realistic systems, there are far more resource acquisitions than kinds of resources, so the 'resource acquisition is initialization' technique leads to less code than use of a 'finally' construct."*

`std::unique_ptr<T, Deleter>` là hiện thân chuẩn của RAII cho memory. Có thể truyền custom deleter cho resource ngoài memory:

```cpp
std::unique_ptr<SDL_Texture, decltype(&SDL_DestroyTexture)>
    texture(SDL_CreateTexture(...), SDL_DestroyTexture);
```

Texture bị `SDL_DestroyTexture` tự động khi `texture` ra khỏi scope — không cần viết `Exit()` thủ công và không thể quên.

## Single ownership và transfer

RAII chỉ làm việc khi mỗi resource có *một owner duy nhất*. Nhiều owner cùng nghĩ mình phải free là gốc rễ của double-free. Hai cách để giữ single ownership:

- **Move semantics** — `std::unique_ptr` không copy được, chỉ move. Move chuyển ownership từ A sang B, A mất quyền, B chịu trách nhiệm.
- **Shared ownership có reference count** — `std::shared_ptr` cho phép nhiều owner, free khi count về 0. Đánh đổi: overhead của atomic counter và nguy cơ cycle leak.

Rust nâng single ownership lên thành first-class với borrow checker — bắt compiler kiểm tra ownership tại compile time thay vì để bug rò rỉ ra runtime. Đây là cùng tư duy của Stroustrup, nhưng được ép thi hành thay vì khuyến cáo.

## Khi không có ngôn ngữ giúp

Trong C thuần và trong wrapper C của SDL/OpenGL/Vulkan, không có destructor — phải tự kỷ luật. Quy tắc thực dụng để giữ ownership rõ:

- Hàm cấp resource và hàm giải phóng đi thành cặp, đặt cùng module: `T* T_create()` ↔ `void T_destroy(T*)`. Người gọi `_create` chịu trách nhiệm gọi `_destroy`.
- Không trả raw pointer ra khỏi class trừ khi đó là *borrow* (người nhận không được free). Ngôn ngữ không cảnh báo, phải viết comment rõ trong API.
- Khi pass pointer giữa các module, document rõ ai là owner — *"caller owns the returned pointer"* hay *"returned pointer is borrowed, do not free"*.

## Trải nghiệm cá nhân

Quy tắc này được rút ra từ một bug segfault khi viết snake game bằng SDL2 thời 2016–2017 ([repo sdl_game/snake](../../references/repos/sdl_game/snake/)). Texture được cấp ở một state, một state khác cố giải phóng → segfault ở runtime khi user chuyển màn hình. Phản ứng đầu tiên là comment-out toàn bộ `delete` trong `LogoState::Exit` ([snake/LogoState.cpp:95-100](../../references/repos/sdl_game/snake/LogoState.cpp:95)) — tránh bug nhưng đổi lấy memory leak. Bài học sau cùng đọng lại: *resource được cấp ở đâu thì ở đó chịu trách nhiệm giải phóng — đây là lưu ý vô cùng quan trọng khi làm các dự án với low-level memory API như C.* Chi tiết trong [transcript phỏng vấn](../../references/interviews/state-pattern-va-singleton-machinestate.md).

## Nguồn tham khảo

- [Resource Acquisition Is Initialization - Wikipedia](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization) — định nghĩa RAII, lịch sử Stroustrup và Koenig, mối quan hệ với single ownership
- [RAII - cppreference](https://en.cppreference.com/w/cpp/language/raii) — tài liệu chính thức C++
- [Object lifetime and resource management (RAII) - Microsoft Learn](https://learn.microsoft.com/en-us/cpp/cpp/object-lifetime-and-resource-management-modern-cpp) — góc nhìn modern C++ với smart pointer
- [Source sdl_game/snake/LogoState.cpp - bug comment-out delete là phản ứng sau segfault](../../references/repos/sdl_game/snake/LogoState.cpp)

## Liên kết tri thức

- [State pattern trong game - bug rò resource khi viết Exit của state là nơi quy tắc này phát sinh](../Game%20development/State%20pattern%20trong%20game.md)
- [Điều khiển thread bằng cooperative event - cùng triết lý "owner chủ động quyết định, không bị ép từ ngoài"](./%C4%90i%E1%BB%81u%20khi%E1%BB%83n%20thread%20b%E1%BA%B1ng%20cooperative%20event.md)
- [Đơn giản hơn linh hoạt trong thiết kế API - quy tắc đơn giản dễ tuân thủ hơn API phức tạp cho phép sai](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/%C4%90%C6%A1n%20gi%E1%BA%A3n%20h%C6%A1n%20linh%20ho%E1%BA%A1t%20trong%20thi%E1%BA%BFt%20k%E1%BA%BF%20API.md)
- [Texture leak làm game lag dần - dẫn chứng concrete cho hệ quả khi vi phạm quy tắc trong vòng lặp game](../Game%20development/Texture%20leak%20l%C3%A0m%20game%20lag%20d%E1%BA%A7n.md)
- [CPU và GPU resource trong SDL2 - áp dụng quy tắc cho 4 loại resource cụ thể của SDL](../Game%20development/CPU%20v%C3%A0%20GPU%20resource%20trong%20SDL2.md)
