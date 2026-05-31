---
tags:
  - game
date: 2026-05-29
---
# Game loop cơ bản

Game loop là vòng lặp trung tâm của một trò chơi, chịu trách nhiệm chạy liên tục từ lúc game start tới lúc exit. Khác với event loop của ứng dụng GUI (block đợi event), game loop luôn quay — kể cả khi không có input — vì game vẫn phải tiến triển: animation chạy, physics tính, AI suy nghĩ. Game Programming Patterns định nghĩa intent của pattern này là *"decouple the progression of game time from user input and processor speed"* để game cảm thấy giống nhau trên mọi cấu hình máy.

## Bốn pha trong một iteration

Một iteration tiêu chuẩn gồm bốn pha tách rời, mỗi pha một trách nhiệm theo Single Responsibility Principle:

- `poll event` — đọc input từ OS (keyboard, mouse, window event)
- `update` — chạy logic game (di chuyển entity, check collision, tính score)
- `render` — vẽ lên screen, không thay đổi state
- `handle` — phản ứng với input đã thu (đổi state, transition menu)

Tách `update` khỏi `render` cho phép sau này chạy update nhiều lần một frame (fixed timestep cho physics) hoặc skip render khi tải nặng. Tách `handle` khỏi `update` cho phép quyết định transition state (ví dụ vào menu mới) chạy *sau* khi state hiện tại đã update xong frame của nó.

```cpp
while (isRunning) {
    poll_event();
    update();
    render();
    handle();
}
```

## Hai chiến lược control FPS

Có hai cách giữ frame rate ổn định:

- **vsync** — đồng bộ render với refresh rate của màn hình (60Hz, 120Hz...) qua flag của driver. Trong SDL2 là `SDL_RENDERER_PRESENTVSYNC`. Đơn giản nhưng phụ thuộc driver và hardware.
- **manual cap** — đo thời gian một iteration, gọi `SDL_Delay(target - elapsed)` để chờ phần còn lại của frame budget. Code mẫu:

```cpp
void FPSController::endCounter() {
    endTime = SDL_GetTicks();
    delayTime = endTime - beginTime;
    int elapsedTime = 1000 / FPS - delayTime;
    if (elapsedTime <= 0) elapsedTime = 1;
    SDL_Delay(elapsedTime);
}
```

Manual cap kém mượt hơn vsync nhưng cho quyền chủ động — phù hợp khi muốn hiểu nguyên lý hoặc cần FPS khác refresh rate của màn hình (ví dụ 30fps mobile để tiết kiệm pin, đúng gợi ý của Nystrom).

## Bẫy phổ biến: sleep trong update

Khi muốn một entity chuyển động chậm (ví dụ snake step mỗi 60ms), cám dỗ đầu tiên là `SDL_Delay(60)` ngay trong hàm update của entity. Việc này block toàn bộ game loop 60ms — không poll event, không render, FPS thực tế tụt còn 16. Cách đúng là time-based movement: mỗi entity giữ `last_update`, mỗi frame kiểm tra `SDL_GetTicks() - last_update > interval`. Xem chi tiết ở node [Time-based movement thay vì sleep trong game loop](./Time-based%20movement%20thay%20v%C3%AC%20sleep%20trong%20game%20loop.md).

## Trải nghiệm cá nhân

Game loop được internalize qua ba game nhỏ viết bằng SDL2 thời 2016–2017 ([repo sdl_game](../../references/repos/sdl_game/)) khi học theo [lazyfoo](https://lazyfoo.net/tutorials/SDL/index.php). Lý do tự build FPS controller thay vì dùng vsync là *muốn học cách quản lý FPS thay vì phụ thuộc thư viện*. Từ trải nghiệm này về sau liên kết được sang `requestIdleCallback` của Web API — cùng tư duy *trả quyền điều khiển cho event loop, không block render frame*. Chi tiết trong [transcript phỏng vấn](../../references/interviews/game-loop-va-fps-control.md).

## Nguồn tham khảo

- [Game Programming Patterns - Game Loop](https://gameprogrammingpatterns.com/game-loop.html) — Robert Nystrom, chương kinh điển về pattern này
- [lazyfoo SDL2 Tutorials - Calculating Frame Rate, Capping Frame Rate](https://lazyfoo.net/tutorials/SDL/index.php) — tutorial 23–25 về FPS
- [Source sdl_game/snake/Game.cpp - cài đặt game loop](../../references/repos/sdl_game/snake/Game.cpp)
- [Source sdl_game/snake/FPSController.cpp - manual FPS cap](../../references/repos/sdl_game/snake/FPSController.cpp)

## Liên kết tri thức

- [Time-based movement thay vì sleep trong game loop - quy tắc bên trong pha update để không block game loop](./Time-based%20movement%20thay%20v%C3%AC%20sleep%20trong%20game%20loop.md)
- [Event loop trong Python - cùng triết lý cooperative scheduling nhưng cho I/O thay vì frame](../System%20level/Event%20loop%20trong%20Python.md)
- [Điều khiển thread bằng cooperative event - cùng nguyên lý "không block, hỏi định kỳ" áp dụng cho thread](../System%20level/%C4%90i%E1%BB%81u%20khi%E1%BB%83n%20thread%20b%E1%BA%B1ng%20cooperative%20event.md)
- [State pattern trong game - pha update và render thường delegate cho state hiện tại](./State%20pattern%20trong%20game.md)
- [Texture leak làm game lag dần - leak trong game loop tăng tuyến tính theo thời gian, biểu hiện thành lag](./Texture%20leak%20l%C3%A0m%20game%20lag%20d%E1%BA%A7n.md)
