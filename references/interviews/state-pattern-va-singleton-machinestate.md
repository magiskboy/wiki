# State pattern + Singleton MachineState — transcript khai quật

> Đã chưng cất lên wiki: [State pattern trong game](../../wiki/Game%20development/State%20pattern%20trong%20game.md), [Cấp resource ở đâu, giải phóng ở đó](../../wiki/System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md).
> Leaf gốc trong [`_source/track.md`](../../_source/track.md), section "Personal → Game programming với SDL2 (2016–2017)".
> Repo: [references/repos/sdl_game/snake/](../repos/sdl_game/snake/).
> File liên quan: `State.h`, `MachineState.cpp`, `LogoState.cpp`, `PlayState.cpp`, `CreditState.cpp`, `Game.cpp`.

## Trí nhớ — vì sao 5 method (Init/Update/Draw/Handle/Exit)

**[Trí nhớ]** Người dùng tách 5 method để đảm bảo **Single Responsibility Principle**: mỗi method chịu một trách nhiệm duy nhất. `Update` chỉ update data của state.

**[Bổ sung — phân tích code]** Phân rã đầy đủ trách nhiệm 5 method (suy từ code):
- `Init()`: tạo SDL resource (texture, font surface...) sau khi `Core` đã sẵn sàng — xem [LogoState.cpp:13-26](../../references/repos/sdl_game/snake/LogoState.cpp:13).
- `Update()`: thuần logic — đổi data, không vẽ. Trong [LogoState.cpp:28-42](../../references/repos/sdl_game/snake/LogoState.cpp:28) là set color cho menu item theo `choiceState`.
- `Draw()`: chỉ render — gọi `SDL_RenderCopy`, không thay đổi state.
- `Handle()`: đọc input và quyết định transition.
- `Exit()`: cleanup khi rời state.

**[Bổ sung — phân tích]** Vì sao tách `Init` khỏi constructor và `Exit` khỏi destructor — câu hỏi này người dùng không trả lời trực tiếp, nhưng code cho thấy lý do thực dụng:
- Constructor chạy ở thời điểm `new LogoState(core)` trong `LogoState::Handle()` của state cũ — lúc đó render context đã có nhưng "thời điểm logic" chưa phải lúc nên init resource. Lazy transition (xem mục dưới) chỉ gọi `Init()` khi state thực sự active.
- Destructor không được gọi (xem `MachineState::Update()` chỉ gọi `currentState->Exit()`, không `delete currentState`). Tách `Exit` ra cho phép cleanup logic độc lập với memory lifecycle.

## Trí nhớ — vì sao lazy transition

**[Trí nhớ]** Toàn bộ việc change state chỉ apply ở iteration tiếp theo của game loop. Nếu apply ngay thì state hiện tại sẽ bị phá vỡ và gây bug conflict data.

**[Bổ sung — minh hoạ cụ thể]** Concrete scenario nếu apply ngay (xem [LogoState.cpp:82-92](../../references/repos/sdl_game/snake/LogoState.cpp:82)):
```cpp
else if (core->getInput()->wasKeyPressed(SDL_SCANCODE_RETURN)) {
    switch (this->choiceState)
    {
    case PLAY: MachineState::getInstance()->changeState(new PlayState(core));
        break;  // <-- nếu state đã swap ngay, this (LogoState) có thể đã được Exit() trong khi
                //     code sau vẫn đọc this->choiceState ở các nhánh switch khác
    ...
    }
}
```
Pattern này có tên kỹ thuật: **deferred state transition** — giống double-buffering rendering nhưng cho state machine.

## Trí nhớ — singleton vs instance member

**[Trí nhớ]** Lúc đó người dùng nghĩ `MachineState` là *toàn bộ data của game* nên dùng singleton. Nhìn lại bây giờ, `MachineState` chỉ là class general-purpose, các class cụ thể như `Game` mới nên giữ nó như instance member.

**[Trí nhớ]** Lý do `Core` là instance member của `Game`: vì nó giữ resource (graphic, audio, input event handler).

**[Trí nhớ — heuristic]** Tiêu chí chọn singleton (ở thời điểm đó): *object không đổi trong cả vòng đời game*.

**[Trí nhớ — reflection]** Nếu thiết kế lại bây giờ sẽ làm đơn giản hơn — không lạm dụng singleton.

**[Bổ sung — phân tích]** Heuristic "không đổi trong vòng đời" đúng nhưng không đủ. Vấn đề thực sự của singleton:
- Phá Dependency Injection — code đâu cũng `MachineState::getInstance()` được, không thấy phụ thuộc từ signature.
- Khó test — không inject mock được.
- Implicit coupling — `Core::updateEvent()` ([Core.cpp:54](../../references/repos/sdl_game/snake/Core.cpp:54)) gọi `MachineState::getInstance()->isRunning = false` — Core lẽ ra không cần biết về MachineState.

Đây cũng là lý do `isRunning` lẽ ra nên ở `Game` (chủ vòng lặp game loop), không phải `MachineState`. Pattern đúng: `Game` truyền callback "request exit" xuống state.

## Trí nhớ — memory cleanup quy tắc vàng

**[Trí nhớ — INSIGHT QUAN TRỌNG]** Bug comment-out `delete` trong [LogoState::Exit](../../references/repos/sdl_game/snake/LogoState.cpp:95-100) đã giúp người dùng nhận ra một quy tắc làm việc với low-level memory API trong C: **memory được khởi tạo ở đâu thì ở đó giải phóng**.

**[Trí nhớ]** Bug cụ thể: cấp memory ở một class, giải phóng ở class khác → các nơi khác sử dụng resource đó bị segfault.

**[Trí nhớ — quy tắc]** Đây là lưu ý vô cùng quan trọng khi làm các dự án game với C++.

**[Bổ sung — nguồn]** Quy tắc người dùng tự rút ra trùng khớp với hai concept lớn của C++:
1. **RAII** (Resource Acquisition Is Initialization) — Stroustrup đặt tên: resource gắn với lifecycle của object, owner duy nhất chịu trách nhiệm cleanup ([cppreference: RAII](https://en.cppreference.com/w/cpp/language/raii)).
2. **Ownership** — concept trở thành first-class trong Rust (move semantics, borrow checker), nhưng nguồn gốc trong C++ qua `unique_ptr` (single owner) và `shared_ptr` (reference counted).

Trong code snake/, các texture được `SDL_CreateTextureFromSurface` trong `LogoState::Init()` — owner là LogoState, nên LogoState::Exit phải `SDL_DestroyTexture`. Nhưng nếu nhỡ truyền pointer ra ngoài và nơi khác cũng `DestroyTexture`, sẽ double-free → segfault. Comment-out là phản ứng "tránh xa" sau khi gặp bug — đúng hướng nhưng đánh đổi là memory leak.

Fix đúng: giữ ownership rõ ràng, hoặc dùng `std::unique_ptr` với custom deleter (`SDL_DestroyTexture`).

## Chưa chắc

- Không rõ snake/ hay doge_snake/ làm trước (carry-over từ leaf 1).
- Không rõ pattern "Init tách khỏi constructor" người dùng học từ lazyfoo hay tự nghĩ ra.
- Bug segfault: **[Trí nhớ một phần]** chỉ nhớ xảy ra trong quá trình user chạy trò chơi (runtime, không phải lúc startup/shutdown). Không nhớ file nào hay scenario cụ thể (vào Play rồi Esc về menu lần 2? Mix_FreeChunk trong destructor?...). Giả thuyết từ code: comment-out `delete` ở `LogoState::Exit` chính là phản ứng sau bug — có thể bug xảy ra khi từ Play bấm Esc về Menu, MachineState gọi `PlayState::Exit()`, nếu Exit `delete` texture mà texture đó vẫn được tham chiếu ở Logo (hoặc state mới Init tạo lại texture với cùng pointer được OS recycle) → segfault.

## Mối nối ra đồ thị wiki (cho bước tinh)

- Quy tắc "cấp ở đâu giải phóng ở đó" → **RAII / Ownership** — node wiki có giá trị riêng, nên tách thành node độc lập (không gắn cứng vào snake game).
- State pattern + State Machine → có thể tham chiếu chéo với [`wiki/http-parser-dang-may-trang-thai.md`](../../wiki/Web%20development/HTTP%20parser%20d%E1%BA%A1ng%20m%C3%A1y%20tr%E1%BA%A1ng%20th%C3%A1i.md) (cùng pattern state machine nhưng cho parser).
- Lazy transition / deferred apply → cùng tư duy với double-buffering, transaction commit, copy-on-write — pattern *"thay đổi không hiệu lực ngay, đợi điểm an toàn"*.
- Singleton lạm dụng — reflection meta về design, có thể tinh thành node mindset *"khi nào nên dùng singleton"*.
