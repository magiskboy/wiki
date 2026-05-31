---
tags:
  - mindset
  - game
date: 2026-05-29
---
# OOP phù hợp cho game vì domain modeling

OOP và các paradigm khác (procedural, functional, declarative) không tốt hơn nhau theo cách trừu tượng — paradigm nào *phù hợp* phụ thuộc vào **vocabulary** của bài toán. Một paradigm có vocabulary trùng với domain sẽ làm code dễ nghĩ, dễ viết, dễ đọc lại. Game là ví dụ điển hình của bài toán *map 1-1* với vocabulary của OOP.

## Vocabulary của game trùng vocabulary của OOP

Game cấu thành từ các *thực thể* (entity) tách biệt, mỗi thực thể có *trạng thái riêng* (state) và *hành vi riêng* (behavior). Snake giữ vị trí, hướng và độ dài; Food giữ vị trí và loại; Wall là tập rect tĩnh; Player có score và HP. Vocabulary này khớp gần như 1-1 với vocabulary OOP: class = loại entity, instance = entity cụ thể, field = state, method = behavior.

Hệ quả: dev tư duy ở tầng domain ("snake ăn food thì dài ra"), code ở tầng OOP cũng đọc tự nhiên như câu đó: `snake.eat(food); snake.grow();`. Khoảng cách giữa cách dev mô tả game trong đầu và cách code biểu đạt nó là gần như không. Đây gọi là **low impedance mismatch** giữa domain model và code model.

Procedural style cho cùng game phải viết: `eat_food(snake_state, food_state); grow_snake(snake_state);` — phải pass state object qua hàm, khó nhìn ra "ai sở hữu cái gì". Functional style phải viết `snake' = eat(snake, food)` — phải trả về state mới mỗi lần, không hợp với loop game tick mà entity được mutate liên tục.

## Khi nào paradigm khác phù hợp hơn

Tư duy quan trọng: *chọn paradigm theo bản chất bài toán, không theo định kiến.* Bài toán có bản chất khác sẽ chọn paradigm khác:

- **RESTful API stateless** → procedural phù hợp hơn. Mỗi request độc lập, không có state giữa request, không có entity nào "sở hữu" gì. OOP sẽ buộc tạo class chỉ để gói function — overhead không có giá trị. Xem [Tư duy theo bản chất vấn đề](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/T%C6%B0%20duy%20theo%20b%E1%BA%A3n%20ch%E1%BA%A5t%20v%E1%BA%A5n%20%C4%91%E1%BB%81.md) để có dẫn chứng chi tiết.
- **Data pipeline / batch processing** → functional phù hợp hơn. Map/filter/reduce match với "stream của data được biến đổi qua nhiều bước". Hadoop, Spark, dbt đều theo paradigm này.
- **UI declarative** → declarative/reactive (React, SwiftUI) phù hợp hơn imperative. Vocabulary là "UI nên trông như thế nào khi state là X", không phải "tay làm gì khi state đổi".

Game thì là entity-driven với state mutation liên tục — vocabulary OOP. REST thì stateless — vocabulary procedural. Cùng một dev có thể (và nên) chọn khác paradigm cho khác bài toán.

## Trade-off với scope

OOP không miễn phí: nhiều file, nhiều class, nhiều dependency để hiểu trước khi sửa được. Game *prototype* nhỏ (vài trăm dòng) có thể viết 1 file global vars vẫn rõ và sửa nhanh hơn. Game *production* (vài nghìn dòng, nhiều state, nhiều entity) thì OOP trả về investment qua khả năng mở rộng.

Quy tắc thực dụng: *simple-first.* Bắt đầu bằng cấu trúc đơn giản nhất đủ work, refactor sang OOP khi scope đòi hỏi. Đây là cùng tư duy với [Đơn giản hơn linh hoạt trong thiết kế API](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/%C4%90%C6%A1n%20gi%E1%BA%A3n%20h%C6%A1n%20linh%20ho%E1%BA%A1t%20trong%20thi%E1%BA%BFt%20k%E1%BA%BF%20API.md) — đơn giản trước, phức tạp khi có nhu cầu thật.

## Trải nghiệm cá nhân

Insight này được internalize qua 3 game SDL2 thời 2016–2017 ([repo sdl_game](../../references/repos/sdl_game/)):

- `doge_space/` — 1 file 236 dòng, global vars, 2 class inline đơn giản
- `doge_snake/` — 1 file 329 dòng, vẫn nhiều global, 1 class Snake đầy đủ hơn
- `snake/` — 16 file .h/.cpp, OOP nghiêm túc với Singleton, State pattern

Lý do nhận ra OOP phù hợp với game: *tư duy của người viết dễ tổ chức và suy luận từ các object trong đời thật hơn là lập trình hàm.* Bây giờ nếu prototype game nhỏ vẫn chọn 1 file đơn giản, game lớn mới chọn OOP nghiêm túc — đây là meta-skill *chọn cấu trúc theo scope* mà thời 2016 chưa có (lúc đó cứng nhắc một stack). Chi tiết trong [transcript phỏng vấn](../../references/interviews/hanh-trinh-to-chuc-code-game.md).

## Nguồn tham khảo

- [Object-oriented design - Wikipedia](https://en.wikipedia.org/wiki/Object-oriented_design) — định nghĩa và lịch sử của OOP cho domain modeling
- [Game Programming Patterns - Architecture, Performance, and Games](https://gameprogrammingpatterns.com/architecture-performance-and-games.html) — Robert Nystrom bàn về architecture trade-off trong game
- [Domain-Driven Design - Eric Evans](https://en.wikipedia.org/wiki/Domain-driven_design) — phương pháp luận đặt model trùng với domain
- [Source sdl_game - arc tổ chức code qua 3 game](../../references/repos/sdl_game/)

## Liên kết tri thức

- [Tư duy theo bản chất vấn đề - cùng tư duy chọn paradigm theo bản chất, kết luận ngược cho REST (stateless → procedural)](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/T%C6%B0%20duy%20theo%20b%E1%BA%A3n%20ch%E1%BA%A5t%20v%E1%BA%A5n%20%C4%91%E1%BB%81.md)
- [Đơn giản hơn linh hoạt trong thiết kế API - simple-first áp dụng cho cả tổ chức code, không chỉ API](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/%C4%90%C6%A1n%20gi%E1%BA%A3n%20h%C6%A1n%20linh%20ho%E1%BA%A1t%20trong%20thi%E1%BA%BFt%20k%E1%BA%BF%20API.md)
- [Phân tích đánh đổi khi đề xuất giải pháp - chọn OOP hay procedural là trade-off điển hình theo scope](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Ph%C3%A2n%20t%C3%ADch%20%C4%91%C3%A1nh%20%C4%91%E1%BB%95i%20khi%20%C4%91%E1%BB%81%20xu%E1%BA%A5t%20gi%E1%BA%A3i%20ph%C3%A1p.md)
- [State pattern trong game - một trong những pattern OOP cụ thể phát huy giá trị nhất ở game](./State%20pattern%20trong%20game.md)
- [Game loop cơ bản - vòng lặp tự nhiên delegate cho object qua polymorphism, biểu hiện của OOP fit game](./Game%20loop%20c%C6%A1%20b%E1%BA%A3n.md)
