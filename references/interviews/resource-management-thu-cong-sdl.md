# Resource management thủ công trong C++ với SDL — transcript khai quật

> Đã chưng cất lên wiki: [CPU và GPU resource trong SDL2](../../wiki/Game%20development/CPU%20v%C3%A0%20GPU%20resource%20trong%20SDL2.md), [Texture leak làm game lag dần](../../wiki/Game%20development/Texture%20leak%20l%C3%A0m%20game%20lag%20d%E1%BA%A7n.md).
> Leaf gốc trong [`_source/track.md`](../../_source/track.md), section "Personal → Game programming với SDL2 (2016–2017)".
> Repo: [references/repos/sdl_game](../repos/sdl_game/).
> Liên quan tới wiki đã có: [Cấp resource ở đâu, giải phóng ở đó](../../wiki/System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md).

## Trí nhớ — Surface vs Texture

**[Trí nhớ]** Người dùng nhớ đại ý (cần verify): Surface chỉ là load pixel lên memory thông thường, còn Texture là dạng "finalize" để render — bao gồm scale, blend, đưa pixel lên màn hình.

**[Bổ sung — verify]** Đúng hướng. Phân biệt chính xác:
- `SDL_Surface`: pixel data nằm ở **CPU RAM**. Manipulation bằng CPU (`SDL_BlitSurface`, `SDL_FillRect`). Phù hợp cho software rendering / pixel-level processing.
- `SDL_Texture`: pixel data nằm ở **GPU VRAM**. Render bằng GPU (`SDL_RenderCopy`) — hardware acceleration. Phù hợp cho real-time rendering.

Lý do `SDL_ttf` tạo Surface trước rồi mới chuyển Texture: font rasterization (vẽ glyph từ vector outline thành bitmap) là CPU-bound — không có cách nào tránh phải pass qua CPU memory. Sau đó dev tự upload lên GPU bằng `SDL_CreateTextureFromSurface`. Đây là một ví dụ điển hình của trade-off "tách biệt concerns": SDL_ttf chỉ lo rasterization, không biết về renderer.

**[Bổ sung — bug ngầm]** `TTF_RenderText_Blended` trả về `SDL_Surface*` được cấp memory mới mỗi lần gọi. Anh phải `SDL_FreeSurface()` sau khi upload sang Texture xong, nếu không → leak CPU RAM. Code anh không free → mỗi lần update score là leak một surface ~120×40×4 byte ≈ 20KB. Lazyfoo có pattern wrapper class `LTexture` quản lý cả surface tạm và texture cuối.

## Trí nhớ — Mix_LoadMUS vs Mix_LoadWAV

**[Trí nhớ]** Người dùng nhớ là game audio vẫn hoạt động bình thường, không nhớ tiêu chí chọn.

**[Bổ sung — verify]** Hai pattern hoàn toàn khác về memory và playback:

| | `Mix_LoadMUS` → `Mix_Music` | `Mix_LoadWAV` → `Mix_Chunk` |
|---|---|---|
| Memory | Stream on-demand (decode dần) | Decode full vào RAM khi load |
| Channel | **Một music channel duy nhất** | Nhiều channel song song (default 8) |
| Phù hợp cho | Background music dài | Sound effect ngắn, có thể overlap |
| API play | `Mix_PlayMusic`, `Mix_PauseMusic` | `Mix_PlayChannel(-1, chunk, 0)` |

Trong code anh:
- `doge.wav` 13MB là music nền → đúng khi dùng `Mix_LoadMUS` (streaming, không tốn 13MB RAM lúc nào cũng giữ)
- `eat.wav` 66KB là sound effect → đúng khi dùng `Mix_LoadWAV` (preload, có thể chơi nhiều lần overlap khi ăn liên tiếp)

Game anh "work bình thường" vì chọn đúng — nếu ngược lại sẽ rõ ngay: dùng `Mix_LoadMUS` cho eat sẽ chỉ chơi 1 lần một lúc (lần ăn sau cắt lần ăn trước), dùng `Mix_LoadWAV` cho music sẽ load 13MB vào RAM cứng. Chứng tỏ anh đã chọn đúng (dù không nhớ vì sao).

## Trí nhớ — Texture leak và game lag dần

**[Trí nhớ — INSIGHT KẾT NỐI ĐƯỢC]** Người dùng quan sát thấy game chơi càng lâu thì càng lag, nhưng lúc đó không biết nguyên nhân. Hiện tại kết nối được: leak texture mỗi lần update score là thủ phạm.

**[Bổ sung — cơ chế chi tiết]** Mỗi lần ăn food trong [Snake.cpp:89](../../references/repos/sdl_game/snake/Snake.cpp:89):
```cpp
this->scoreTex = SDL_CreateTextureFromSurface(...);  // tạo MỚI
```
Không có `SDL_DestroyTexture(this->scoreTex)` trước đó. Pointer cũ bị overwrite, texture cũ vẫn nằm ở VRAM nhưng mất handle — không bao giờ free được.

Chuỗi nhân quả dẫn tới lag:
1. Mỗi lần ăn → leak 1 texture (~120×40×4 = 20KB VRAM)
2. Game dài chơi liên tục → VRAM lấp dần
3. Khi VRAM đầy, driver phải **evict** texture đang dùng ra system RAM, swap lại khi cần render
4. Mỗi swap qua PCIe bus rất chậm so với GPU access trực tiếp
5. Render time tăng → frame drop → game lag

Trên integrated GPU (Intel HD, Apple Silicon unified memory) không có PCIe swap nhưng tổng memory pressure tăng → OS swap virtual memory ra disk → lag thậm chí chậm hơn.

Thêm vào đó là **GPU memory fragmentation**: sau nhiều create không destroy, allocation mới phải tìm chỗ trống đủ to → tốc độ allocate chậm dần.

Pattern fix: hoặc destroy texture cũ trước khi tạo mới, hoặc chỉ tạo texture khi score thực sự đổi (đã được làm trong `Panel::Draw` xem [Panel.cpp:39](../../references/repos/sdl_game/snake/Panel.cpp:39): `if (this->score != _score)` — nhưng cũng không destroy cái cũ, chỉ tránh tạo dư khi score không đổi).

## Mối nối ra đồ thị wiki (cho bước tinh)

- **Node mới đề xuất**: "Texture leak làm game lag dần" — insight chính, áp dụng được cho web (DOM leak), mobile (image cache leak), bất kỳ context nào có resource pool có giới hạn.
- **Node mới đề xuất**: "Phân biệt CPU và GPU resource trong SDL2" — 4 loại Surface/Texture/Music/Chunk qua trục CPU vs GPU + streaming vs preload.
- Liên kết tới [`cap-resource-o-dau-giai-phong-o-do`](../../wiki/System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md) — texture leak là dẫn chứng concrete cho quy tắc đó.

## Chưa chắc

- Không rõ con số leak chính xác (giả định texture ~20KB dựa trên kích thước `scoreRect = { 500, 50, 120, 40 }` × 4 byte/pixel ARGB).
- Không rõ game thời điểm anh test chạy bao lâu mới lag rõ (5 phút? 30 phút?).
- Không rõ GPU lúc đó là integrated hay dedicated (ảnh hưởng đến cơ chế eviction).
