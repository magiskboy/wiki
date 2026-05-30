# Game loop và FPS control — transcript khai quật

> Đã chưng cất lên wiki: [Game loop cơ bản](../../wiki/Game%20development/Game%20loop%20c%C6%A1%20b%E1%BA%A3n.md), [Time-based movement thay vì sleep trong game loop](../../wiki/Game%20development/Time-based%20movement%20thay%20v%C3%AC%20sleep%20trong%20game%20loop.md).
> Leaf gốc trong [`_source/track.md`](../../_source/track.md), section "Personal → Game programming với SDL2 (2016–2017)".
> Repo: [references/repos/sdl_game](../repos/sdl_game/) (`snake/`, `doge_snake/`, `doge_space/`).
> Tài liệu nguồn người dùng đọc thời điểm đó: [lazyfoo.net](https://lazyfoo.net/) tutorial SDL2.

## Trí nhớ — thứ tự gọi trong game loop

**[Trí nhớ]** Người dùng đảo `Handle()` xuống sau `Draw()` (xem `snake/Game.cpp:24-32`) vì nghĩ rằng *frame time trong game rất nhanh và có tính tương đương*, nên đổi thứ tự `event → update → render → handle` so với chuẩn lazyfoo `event → update → render` không gây sai logic.

**[Bổ sung — phân tích code]** Lý do sâu hơn (người dùng không nhắc tới, suy ra từ code): đảo `Handle()` xuống sau hoạt động được vì hai điều kiện kết hợp:
1. `Snake::Update()` không đọc input — chỉ Snake::Handle mới đọc. Nếu Update có đọc input thì việc đảo sẽ làm lag 1 frame.
2. Các edge event (`wasPressed`/`wasReleased`) sống đúng 1 frame và bị clear ở `beginNewFrame()` đầu frame kế (xem `Input.cpp:14-19`). Handle vẫn là consumer cuối cùng trong frame nên đọc kịp.

Nói cách khác: trật tự đúng phải là *consumer cuối phải nằm trước beginNewFrame của frame kế*. Đảo ngược không ảnh hưởng miễn vẫn còn trong frame đó.

## Trí nhớ — chọn tự quản FPS thay vì vsync

**[Trí nhớ]** Người dùng cố tình không dùng `SDL_RENDERER_PRESENTVSYNC` để *tự học cách quản lý FPS thay vì phụ thuộc thư viện*. (Lưu ý: trong `doge_snake/main.cpp:169` và `doge_space/doge.cpp:136` lại có dùng vsync — chứng tỏ snake/ là phiên bản học tay, hai game kia làm sau khi đã hiểu.)

**[Trí nhớ]** Có lần thấy frame chậm khiến `delayTime` âm (đoạn ép `= 1` trong `FPSController.cpp:28`) nhưng *chưa xử lý gì thêm*.

**[Trí nhớ — mối nối đồ thị]** Từ trải nghiệm quản lý FPS này, sau đó người dùng liên kết được tới `requestIdleCallback` trong Web API — cùng tư duy: trả quyền cho event loop, không chặn render frame.

**[Bổ sung — phân tích]** Tương đồng xa hơn nhưng cùng họ:
- `requestAnimationFrame` của browser ≈ vsync (browser tự lock 60fps theo refresh rate màn hình)
- `SDL_RENDERER_PRESENTVSYNC` ≈ rAF
- `SDL_Delay(1000/FPS - elapsed)` ≈ tự build rAF bằng `setTimeout` (cũ trước rAF ra đời)
- Asyncio event loop trong Python (xem [`wiki/event-loop-trong-python.md`](../../wiki/System%20level/Event%20loop%20trong%20Python.md)) cùng nguyên lý cooperative scheduling.

## Trí nhớ — vì sao chỉ đo quanh Update()

**[Trí nhớ]** *Chỉ làm theo lazyfoo*, không có lý do sâu xa.

**[Bổ sung — quan sát]** Thực tế bug ngầm: bỏ `Handle()` và `updateEvent()` ngoài vùng đo sẽ làm FPS thấp hơn dự kiến nếu input/event xử lý lâu. Trong game đơn giản này thì không thành vấn đề.

## Trí nhớ — tái dựng tư duy sửa SDL_Delay drop FPS

**[Trí nhớ]** Người dùng nhận ra `SDL_Delay(60)` làm drop FPS, đã sửa, nhưng không nhớ tư duy lúc đó. Nhờ trợ lý phân tích từ code để tái dựng.

**[Bổ sung — tái dựng tư duy từ code]**

Trước (`snake/Snake.cpp:25`):
```cpp
void Snake::Update() {
    SDL_Delay(60);   // block cả thread 60ms để snake chỉ "step" mỗi 60ms
    preVector = this->part.at(0);
    // ... move logic ...
}
```
Hệ quả ngầm: trong 60ms ấy không poll event, không render, FPS thực tế = ~16. `FPSController` mất tác dụng vì `delayTime` luôn ≥ 60ms.

Sau (`doge_snake/main.cpp:58-100`):
```cpp
void update(){
    if (!this->isDead && SDL_GetTicks() - this->last_update > SPEED){
        // ... move logic ...
        this->last_update = SDL_GetTicks();
    }
}
```
Tư duy ngầm — 3 bước chuyển:
1. **Đảo câu hỏi**: từ "sleep đủ 60ms rồi step" → "đã đủ 60ms từ lần step trước chưa?". Đây là bước chuyển bản chất: từ blocking sang polling.
2. **Per-object clock**: mỗi entity giữ `last_update` riêng. Game loop chạy 60fps nhưng snake step mỗi 120ms, doge rơi mỗi 20ms — không xung đột.
3. **Tách object speed khỏi render speed**: chính là khái niệm **delta-time / fixed timestep** trong game programming chuẩn. Game loop = vòng check; mỗi object tự biết khi nào tới lượt.

Trong `doge_space/doge.cpp:42-66` còn tổng quát thêm: mỗi `Doge` có `rate` riêng (param constructor), chứng minh người dùng đã tổng quát hoá pattern — không còn là fix-cứng 60ms mà là *scheduler per-entity*.

**[Bổ sung — nguồn]** Đây là pattern kinh điển trong cuốn ["Game Programming Patterns" của Robert Nystrom — chương Game Loop](https://gameprogrammingpatterns.com/game-loop.html): "Decouple the progression of game time from user input and processor speed". Người dùng tự khám phá lại pattern này khi sửa bug FPS — không qua sách, chỉ qua va vấp.

## Chưa chắc

- Không rõ snake/ hay doge_snake/ ra đời trước. Code style của snake/ (OOP đa file, State pattern) trông trưởng thành hơn → có thể là phiên bản refactor lại. Nhưng SDL_Delay(60) lại là kỹ thuật cũ → có thể snake/ làm trước thực sự, doge_snake/ là phiên bản học được bài học.

## Mối nối ra đồ thị wiki (cho bước tinh)

- Tư duy "không block loop, schedule công việc" — kết nối với:
  - [`wiki/event-loop-trong-python.md`](../../wiki/System%20level/Event%20loop%20trong%20Python.md) — cooperative scheduling trong asyncio
  - [`wiki/dieu-khien-thread-bang-cooperative-event.md`](../../wiki/System%20level/%C4%90i%E1%BB%81u%20khi%E1%BB%83n%20thread%20b%E1%BA%B1ng%20cooperative%20event.md) — cooperative event để pause thread (cùng nguyên lý: trả quyền điều khiển)
  - [`wiki/backpressure-tang-transport.md`](../../wiki/System%20level/Backpressure%20%E1%BB%9F%20t%E1%BA%A7ng%20transport%20trong%20asyncio.md) — không để producer chặn consumer
- Liên kết web ngược về game: `requestIdleCallback`, `requestAnimationFrame`, `setTimeout` cũ.
