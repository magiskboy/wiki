# Hành trình tổ chức code game: từ 1-file global vars → OOP nghiêm túc — transcript khai quật

> Đã chưng cất lên wiki: [OOP phù hợp cho game vì domain modeling](../../wiki/Game%20development/OOP%20ph%C3%B9%20h%E1%BB%A3p%20cho%20game%20v%C3%AC%20domain%20modeling.md).
> Leaf gốc trong [`_source/track.md`](../../_source/track.md), section "Personal → Game programming với SDL2 (2016–2017)".
> Repo: [references/repos/sdl_game](../repos/sdl_game/).
> Leaf meta — về sự trưởng thành trong tổ chức code qua 3 game (doge_space, doge_snake, snake).

## Trí nhớ — trật tự thời gian 3 game

**[Chưa chắc]** Người dùng không nhớ thứ tự làm 3 game. Carry-over từ leaf 1 — vẫn không xác định được snake/ hay doge_snake/ làm trước. Code style cho thấy arc *doge_space → doge_snake → snake* (1 file → 1 file có class đầy đủ → đa file OOP) nhưng không có evidence trực tiếp từ ký ức.

## Trí nhớ — vì sao OOP phù hợp với game

**[Trí nhớ — INSIGHT]** Người dùng nhận ra: viết game bằng OOP *thuận tiện và dễ dàng quản lý object cũng như mô phỏng game dễ dàng hơn*. Lý do: tư duy của người viết dễ tổ chức và suy luận **từ các object trong đời thật** hơn là lập trình hàm.

**[Bổ sung — đặt vào bối cảnh]** Đây chính là khái niệm **domain modeling fit** trong software design: paradigm nào có vocabulary trùng với vocabulary của domain thì code đó dễ nghĩ và dễ viết. Game có nhiều thực thể tách biệt (Snake, Map, Food, Wall, Player) với state riêng và behavior riêng — chính là từ vựng của OOP (class, instance, method). Trong khi REST API có bản chất stateless với request độc lập — từ vựng của procedural (function với input/output).

Đây là **ví dụ đối lập** của cùng tư duy trong node [Tư duy theo bản chất vấn đề](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/T%C6%B0%20duy%20theo%20b%E1%BA%A3n%20ch%E1%BA%A5t%20v%E1%BA%A5n%20%C4%91%E1%BB%81.md): node đó kết luận "REST stateless → chọn procedural"; insight của người dùng cho game kết luận ngược: "game stateful nhiều entity → chọn OOP". Cùng tư duy chọn paradigm theo bản chất bài toán, khác kết luận vì bản chất khác.

## Trí nhớ — chọn organization theo scope

**[Trí nhớ — INSIGHT]** Tư duy của người dùng hiện tại:
- Game nhỏ → tổ chức như `doge_space/` (1 file, global vars)
- Game lớn và chuẩn chỉ → tổ chức như `snake/` (đa file, OOP nghiêm túc)
- **Tư duy chủ đạo là simple-first**
- Không cứng nhắc 1 stack — luôn biết mình làm gì và hệ thống đòi hỏi gì

**[Bổ sung — kết nối]** Đây là cùng họ với:
- [Đơn giản hơn linh hoạt trong thiết kế API](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/%C4%90%C6%A1n%20gi%E1%BA%A3n%20h%C6%A1n%20linh%20ho%E1%BA%A1t%20trong%20thi%E1%BA%BFt%20k%E1%BA%BF%20API.md) — chọn API gọn trước khi cho phép linh hoạt
- [Tư duy theo bản chất vấn đề](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/T%C6%B0%20duy%20theo%20b%E1%BA%A3n%20ch%E1%BA%A5t%20v%E1%BA%A5n%20%C4%91%E1%BB%81.md) — chọn công cụ theo bài toán, không theo định kiến
- [Phân tích đánh đổi khi đề xuất giải pháp](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Ph%C3%A2n%20t%C3%ADch%20%C4%91%C3%A1nh%20%C4%91%E1%BB%95i%20khi%20%C4%91%E1%BB%81%20xu%E1%BA%A5t%20gi%E1%BA%A3i%20ph%C3%A1p.md) — đánh đổi giữa "viết nhanh sửa nhanh" và "viết chậm ít bug" là một trade-off điển hình của scale

Sự khác giữa người dùng năm 2016 và bây giờ: lúc đó *cứng nhắc một stack* (snake/ phải OOP, doge phải global) — chưa chọn theo scope. Bây giờ đã có meta-skill "chọn cấu trúc theo scope".

## Mối nối ra đồ thị wiki (cho bước tinh)

- **Node mới đề xuất**: "OOP phù hợp cho game vì domain modeling" — bổ sung dẫn chứng đối lập cho [Tư duy theo bản chất vấn đề](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/T%C6%B0%20duy%20theo%20b%E1%BA%A3n%20ch%E1%BA%A5t%20v%E1%BA%A5n%20%C4%91%E1%BB%81.md). Có thể trở thành node tham chiếu khi gặp câu hỏi "khi nào dùng OOP, khi nào dùng procedural/functional".
- Insight "chọn organization theo scope, simple-first" đã được phủ bởi 3 node mindset hiện có — không tách node riêng, chỉ thêm trải nghiệm vào node mới như dẫn chứng cá nhân.

## Chưa chắc

- Trật tự thời gian 3 game không rõ (xem mục đầu).
- Không rõ Coursera Design Pattern (đã có trong track.md ở section Coursera) có học trước hay sau khi viết snake/ — nếu trước thì đó là một nguồn rõ của việc dùng Singleton + State pattern.
