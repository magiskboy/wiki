---
tags:
  - game
date: 2026-05-29
---
# Texture leak làm game lag dần

Một triệu chứng quen thuộc khi học game programming: game chạy mượt lúc mới start, càng chơi lâu càng lag, đến mức phải restart mới mượt lại. Thường thủ phạm là *resource leak trong game loop* — đặc biệt là texture không được destroy khi tạo mới. Cùng pattern xuất hiện ở web (DOM leak), mobile (image cache leak) — bất cứ context nào có resource pool giới hạn và code tạo mới trong vòng lặp mà quên giải phóng.

## Chuỗi nhân quả từ leak đến lag

Mỗi lần `SDL_CreateTextureFromSurface` không kèm `SDL_DestroyTexture` cho texture cũ:

1. Texture mới được cấp ở VRAM, pointer mới ghi đè biến giữ texture cũ
2. Texture cũ vẫn nằm ở VRAM nhưng mất handle — không bao giờ free được
3. Game chơi liên tục → VRAM lấp dần (vài KB mỗi lần × hàng nghìn frame = hàng MB sau vài phút)
4. Khi VRAM gần đầy, GPU driver phải **evict** texture đang dùng ra system RAM, swap lại khi cần render
5. Mỗi swap qua PCIe bus chậm hơn GPU access trực tiếp hàng chục lần
6. Render time mỗi frame tăng → frame rate tụt → game lag rõ

Trên integrated GPU (Intel HD, Apple Silicon unified memory), không có PCIe swap nhưng tổng memory pressure tăng — OS phải swap virtual memory ra disk, lag thậm chí chậm hơn nữa. Thêm vào đó là **GPU memory fragmentation**: sau nhiều cycle create không destroy, allocator phải tìm chỗ trống đủ to → tốc độ allocate cũng chậm dần.

## Vì sao leak ở game loop nguy hiểm hơn leak ở chỗ khác

Leak trong code chạy một lần (ví dụ init) chỉ tốn cố định một lần — annoying nhưng không tăng theo thời gian. Leak trong **game loop** (hoặc bất kỳ vòng lặp chính nào) thì tăng tuyến tính theo thời gian chạy, biến từ "rò rỉ nhỏ" thành "cạn resource sau N phút".

Hai chỗ điển hình leak trong game loop:
- Re-render text mỗi frame khi score đổi (như [Snake.cpp:89](../../references/repos/sdl_game/snake/Snake.cpp:89)) — quên `SDL_DestroyTexture`
- Re-load asset khi reset state (như reset color text trong menu) — quên giải phóng texture cũ
- Spawn entity rồi mất reference — entity giữ texture/buffer riêng cũng leak theo

## Hai cách fix

Cách trực tiếp — destroy trước khi tạo mới:

```cpp
if (this->scoreTex != nullptr) {
    SDL_DestroyTexture(this->scoreTex);
}
this->scoreTex = SDL_CreateTextureFromSurface(...);
```

Cách phòng ngừa — *tránh tạo texture nếu data không đổi*:

```cpp
if (this->lastScore != newScore) {
    if (this->scoreTex != nullptr) SDL_DestroyTexture(this->scoreTex);
    this->scoreTex = SDL_CreateTextureFromSurface(...);
    this->lastScore = newScore;
}
```

Cách thứ hai tốt hơn vì giải quyết cả CPU cost của `TTF_RenderText` và surface leak — *render lười* (lazy render): chỉ render khi data đổi, cache lại lần sau. Đây là cùng tư duy với `React.memo`, `useMemo`, `requestAnimationFrame` skipping.

## Cùng pattern ở các context khác

Triệu chứng "chạy lâu càng chậm" do leak trong vòng lặp chính xuất hiện khắp nơi:

- **Web**: tạo DOM node trong event handler mà không remove khi component unmount — DOM tree phình dần, query selector chậm dần.
- **Mobile**: cache image mỗi lần scroll mà không evict — RAM đầy, OS kill app.
- **Backend**: tạo connection trong request handler mà không close — connection pool cạn, request mới block.
- **Node.js**: closure giữ reference trong setInterval — heap phình dần, GC pause lâu hơn.

Pattern chung: *resource pool giới hạn × tạo mới trong vòng lặp × quên cleanup = degradation tuyến tính theo thời gian.* Khi gặp ứng dụng "lag dần sau N phút chạy", câu hỏi đầu tiên nên hỏi là *cái gì đang được tạo trong vòng lặp chính mà có thể đang leak.*

## Trải nghiệm cá nhân

Quan sát "game càng chơi càng lag" đến từ snake game thời 2016–2017 ([repo sdl_game/snake](../../references/repos/sdl_game/snake/)) khi mỗi lần ăn food tạo texture mới mà không destroy texture cũ trong [Snake.cpp:89](../../references/repos/sdl_game/snake/Snake.cpp:89). Lúc đó chỉ thấy hiện tượng, không kết nối được nguyên nhân — chỉ sau này khi nhìn lại code mới hiểu là texture leak gây VRAM pressure dẫn đến render slow. Chi tiết trong [transcript phỏng vấn](../../references/interviews/resource-management-thu-cong-sdl.md).

## Nguồn tham khảo

- [SDL2 Wiki - SDL_CreateTextureFromSurface](https://wiki.libsdl.org/SDL2/SDL_CreateTextureFromSurface) — mỗi lần gọi cấp memory mới
- [SDL2 Wiki - SDL_DestroyTexture](https://wiki.libsdl.org/SDL2/SDL_DestroyTexture) — hàm phải gọi để free
- [GPU Texture Residency - Microsoft Direct3D documentation](https://learn.microsoft.com/en-us/windows/win32/direct3d12/residency) — cơ chế driver evict texture khi VRAM đầy
- [Source sdl_game/snake/Snake.cpp:89 - dẫn chứng leak](../../references/repos/sdl_game/snake/Snake.cpp)

## Liên kết tri thức

- [Cấp resource ở đâu, giải phóng ở đó - quy tắc gốc, texture leak là dẫn chứng concrete](../System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md)
- [CPU và GPU resource trong SDL2 - phân biệt 4 loại resource, texture là loại đặc biệt nhạy với leak vì VRAM giới hạn](./CPU%20v%C3%A0%20GPU%20resource%20trong%20SDL2.md)
- [Game loop cơ bản - vòng lặp chính là nơi leak biểu hiện rõ vì tăng tuyến tính theo frame](./Game%20loop%20c%C6%A1%20b%E1%BA%A3n.md)
- [Time-based movement thay vì sleep trong game loop - cùng họ "tránh làm việc không cần thiết trong vòng lặp"](./Time-based%20movement%20thay%20v%C3%AC%20sleep%20trong%20game%20loop.md)
