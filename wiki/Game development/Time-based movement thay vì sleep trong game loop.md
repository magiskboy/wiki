---
tags:
  - game
date: 2026-05-29
---
# Time-based movement thay vì sleep trong game loop

Khi một entity cần chuyển động chậm hơn frame rate của game (ví dụ snake step mỗi 120ms trong khi loop chạy 60fps), có hai cách viết — và sự khác biệt giữa chúng là một trong những bài học bản lề khi học game programming.

## Hai cách viết, một câu hỏi đảo ngược

Cách *blocking* — sleep trong update của entity:

```cpp
void Snake::Update() {
    SDL_Delay(60);   // block cả thread 60ms
    move();
}
```

Cách *time-based* — entity giữ timestamp riêng và poll:

```cpp
void Snake::update() {
    if (SDL_GetTicks() - this->last_update > SPEED) {
        move();
        this->last_update = SDL_GetTicks();
    }
}
```

Khác biệt cốt lõi là *câu hỏi*: cách đầu hỏi *"đã sleep đủ chưa?"* (block tới khi đủ), cách sau hỏi *"đã đủ thời gian từ lần trước chưa?"* (return ngay nếu chưa, không làm gì). Một là blocking, một là polling. Cùng giải quyết "snake step mỗi 60ms" nhưng hệ quả khác nhau hoàn toàn.

## Vì sao sleep trong update phá game loop

Trong 60ms `SDL_Delay` đó, toàn bộ game loop bị block:

- `poll_event` không chạy — input bị nuốt, user nhấn key không được ghi
- `render` không chạy — màn hình đứng hình, FPS thực tế tụt còn ~16
- FPS controller cũng không có cơ hội đo và điều tiết — nó đo `delayTime` của một iteration, và iteration này luôn ≥ 60ms nên `1000/60 - delayTime` luôn âm

Sleep trong update vi phạm hợp đồng ngầm của game loop: *update phải hoàn thành trong một burst ngắn để loop có cơ hội quay tiếp.* Đây là cùng nguyên lý cooperative scheduling đã thấy ở [Điều khiển thread bằng cooperative event](../System%20level/%C4%90i%E1%BB%81u%20khi%E1%BB%83n%20thread%20b%E1%BA%B1ng%20cooperative%20event.md).

## Per-entity clock và pattern decoupling

Cách time-based mở ra ba khả năng:

- **Per-entity clock**: mỗi entity giữ `last_update` riêng. Snake step mỗi 120ms, doge rơi mỗi 20ms, particle update mỗi frame — cùng tồn tại không xung đột.
- **Per-entity rate**: rate có thể là tham số constructor, không hard-code. Ví dụ trong [doge_space/doge.cpp:44](../../references/repos/sdl_game/doge_space/doge.cpp:44) constructor `Doge` nhận `rate` riêng.
- **Tách object speed khỏi render speed**: game loop quay 60fps cho input mượt, entity tự biết khi nào tới lượt update. Đây chính là tinh thần của *fixed timestep* mà Nystrom gọi là "decouple the progression of game time from processor speed".

## Liên hệ ngoài game programming

Cùng tư duy "không block, schedule công việc" xuất hiện ở nhiều nơi:

- `requestAnimationFrame` của browser ≈ vsync — trả quyền cho compositor
- `requestIdleCallback` ≈ "chạy khi loop rảnh" — đúng tư duy time-based
- Asyncio event loop ([Event loop trong Python](../System%20level/Event%20loop%20trong%20Python.md)) — coroutine không block loop, await để nhường quyền
- Kubernetes controller reconciliation — không event-driven push, mà poll periodically và so sánh desired vs actual

Sleep trong vòng lặp chính là anti-pattern xuyên ngành. Khi gặp tình huống "tôi muốn chậm lại", câu hỏi đúng là *"ai có quyền chậm lại — tôi hay loop?"* — câu trả lời gần như luôn là loop.

## Trải nghiệm cá nhân

Phát hiện này đến từ bug FPS drop khi viết `snake/Snake.cpp:25` (sleep trong update) thời 2016–2017. Phiên bản sau ([doge_snake/main.cpp:58](../../references/repos/sdl_game/doge_snake/main.cpp:58)) đã chuyển sang time-based và tổng quát hoá thành per-entity rate trong [doge_space/doge.cpp](../../references/repos/sdl_game/doge_space/doge.cpp). Cá nhân không nhớ tư duy lúc sửa, nhưng đối chiếu hai phiên bản code cho thấy đã đi qua ba bước chuyển: đảo câu hỏi (blocking → polling), per-object clock, tổng quát thành per-entity rate. Chi tiết trong [transcript phỏng vấn](../../references/interviews/game-loop-va-fps-control.md).

## Nguồn tham khảo

- [Game Programming Patterns - Game Loop: Fixed Time Step](https://gameprogrammingpatterns.com/game-loop.html) — chương kinh điển về tách game time khỏi render time
- [lazyfoo SDL2 Tutorial - Frame Independent Movement](https://lazyfoo.net/tutorials/SDL/index.php) — tutorial 44 về cùng pattern
- [Source sdl_game/snake/Snake.cpp - phiên bản blocking (anti-pattern)](../../references/repos/sdl_game/snake/Snake.cpp)
- [Source sdl_game/doge_snake/main.cpp - phiên bản time-based đúng](../../references/repos/sdl_game/doge_snake/main.cpp)
- [Source sdl_game/doge_space/doge.cpp - per-entity rate](../../references/repos/sdl_game/doge_space/doge.cpp)

## Liên kết tri thức

- [Game loop cơ bản - cấu trúc khung trong đó pattern này áp dụng](./Game%20loop%20c%C6%A1%20b%E1%BA%A3n.md)
- [Điều khiển thread bằng cooperative event - cùng nguyên lý "không block, return định kỳ" áp dụng cho thread](../System%20level/%C4%90i%E1%BB%81u%20khi%E1%BB%83n%20thread%20b%E1%BA%B1ng%20cooperative%20event.md)
- [Event loop trong Python - cooperative scheduling cấp cao hơn cho I/O](../System%20level/Event%20loop%20trong%20Python.md)
- [Backpressure ở tầng transport trong asyncio - cùng họ "không block producer, schedule lại"](../System%20level/Backpressure%20%E1%BB%9F%20t%E1%BA%A7ng%20transport%20trong%20asyncio.md)
