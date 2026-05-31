---
tags:
  - game
date: 2026-05-29
---
# CPU và GPU resource trong SDL2

SDL2 phân biệt resource theo hai trục quan trọng: *resource nằm ở CPU RAM hay GPU VRAM*, và với audio là *load full vào RAM hay stream on-demand*. Bốn loại resource phổ biến (`SDL_Surface`, `SDL_Texture`, `Mix_Chunk`, `Mix_Music`) là bốn vị trí trên hai trục đó. Chọn nhầm không gây crash nhưng gây leak RAM hoặc không thể overlap sound — bug "im lặng" khó phát hiện.

## Surface và Texture: nơi pixel sống

`SDL_Surface` giữ pixel data ở CPU RAM. Mọi thao tác (fill rect, blit, alpha blend tay) đều do CPU làm — chậm nhưng kiểm soát từng pixel. `SDL_Texture` giữ pixel data ở GPU VRAM, hardware-accelerated qua renderer. Render cùng một image bằng texture nhanh hơn surface nhiều lần vì GPU có pipeline song song và memory bandwidth cao.

Quy tắc thực dụng: *cái gì render lên screen thì phải là Texture; cái gì cần pixel manipulation thì phải là Surface; chuyển đổi qua `SDL_CreateTextureFromSurface`.*

`SDL_ttf` minh hoạ điển hình. `TTF_RenderText_Blended` chỉ tạo Surface vì font rasterization (vẽ glyph từ vector outline thành bitmap) là CPU-bound — phải pass qua CPU memory. Dev có trách nhiệm upload sang Texture rồi free Surface:

```cpp
SDL_Surface* surf = TTF_RenderText_Blended(font, "Hello", color);
SDL_Texture* tex = SDL_CreateTextureFromSurface(renderer, surf);
SDL_FreeSurface(surf);  // bắt buộc, nếu không sẽ leak CPU RAM
```

Bỏ `SDL_FreeSurface` là một trong những lỗi rò rỉ phổ biến nhất khi học SDL — code vẫn chạy đúng nhưng leak ~20KB mỗi lần render text mới.

## Mix_Chunk và Mix_Music: streaming hay preload

SDL2_mixer phân biệt hai loại audio:

| | `Mix_Chunk` (qua `Mix_LoadWAV`) | `Mix_Music` (qua `Mix_LoadMUS`) |
|---|---|---|
| Memory | Decode full vào RAM khi load | Stream on-demand, decode dần |
| Channel | Nhiều channel song song (default 8) | **Một music channel duy nhất** |
| API play | `Mix_PlayChannel(-1, chunk, 0)` | `Mix_PlayMusic(music, loops)` |
| Phù hợp cho | Sound effect ngắn, có thể overlap | Background music dài |

Hệ quả của "một music channel duy nhất": gọi `Mix_PlayMusic` lần hai sẽ cắt music đang chơi. Nếu lỡ dùng `Mix_LoadMUS` cho sound effect (như tiếng ăn của snake), mỗi lần ăn sẽ cắt music nền — bug rất rõ. Ngược lại, dùng `Mix_LoadWAV` cho background music dài sẽ load toàn bộ file vào RAM (file 13MB → tốn 13MB RAM cứng) thay vì streaming.

Quy tắc: *file ngắn, cần overlap → Chunk; file dài, chỉ chơi một bản tại một thời điểm → Music.*

## Mỗi loại cần API destroy riêng

Vì C không có destructor tự động, mỗi loại resource có hàm cleanup tương ứng:

```cpp
SDL_FreeSurface(surface);
SDL_DestroyTexture(texture);
Mix_FreeChunk(chunk);
Mix_FreeMusic(music);
TTF_CloseFont(font);
```

Gọi nhầm sẽ undefined behavior (ví dụ `SDL_FreeSurface` lên một Texture pointer). Quy tắc [Cấp resource ở đâu, giải phóng ở đó](../System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md) áp dụng nguyên xi: nơi nào `Create/Load` thì nơi đó phải `Free/Destroy`, với đúng cặp hàm.

## Trải nghiệm cá nhân

Phân biệt này được internalize qua 3 game SDL2 thời 2016–2017 ([repo sdl_game](../../references/repos/sdl_game/)). Việc chọn đúng `Mix_LoadMUS` cho `doge.wav` (13MB music nền) và `Mix_LoadWAV` cho `eat.wav` (66KB sound effect) trong [doge_snake/main.cpp:194-195](../../references/repos/sdl_game/doge_snake/main.cpp:194) là quyết định đúng — game audio hoạt động bình thường, không bị cắt nhạc khi ăn. Tuy nhiên `SDL_FreeSurface` bị quên ở [Snake.cpp:16](../../references/repos/sdl_game/snake/Snake.cpp:16) là một leak ngầm. Chi tiết trong [transcript phỏng vấn](../../references/interviews/resource-management-thu-cong-sdl.md).

## Nguồn tham khảo

- [SDL2 Wiki - SDL_Surface](https://wiki.libsdl.org/SDL2/SDL_Surface)
- [SDL2 Wiki - SDL_Texture](https://wiki.libsdl.org/SDL2/SDL_Texture)
- [SDL Discourse - Is the texture data of SDL_Texture placed in VRAM or RAM?](https://discourse.libsdl.org/t/is-the-texture-data-of-sdl-texture-placed-in-vram-or-ram/38862)
- [SDL2_mixer Wiki - Mix_LoadMUS](https://wiki.libsdl.org/SDL2_mixer/Mix_LoadMUS)
- [Lazy Foo' - Sound Effects and Music](https://lazyfoo.net/tutorials/SDL/21_sound_effects_and_music/index.php) — tutorial 21 phân biệt Music và Chunk
- [Source sdl_game - dẫn chứng dùng đúng cả 4 loại](../../references/repos/sdl_game/)

## Liên kết tri thức

- [Cấp resource ở đâu, giải phóng ở đó - quy tắc tổng quát áp dụng cho từng cặp Create/Free trong SDL](../System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md)
- [Texture leak làm game lag dần - hệ quả thực tế khi quên destroy texture trong game loop](./Texture%20leak%20l%C3%A0m%20game%20lag%20d%E1%BA%A7n.md)
- [Game loop cơ bản - vòng lặp render là nơi texture được dùng và là nơi leak biểu hiện rõ nhất](./Game%20loop%20c%C6%A1%20b%E1%BA%A3n.md)
