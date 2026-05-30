---
tags:
  - game
date: 2026-05-29
---
# State pattern trong game

Một game thường có nhiều màn hình phân biệt rõ: menu chính, màn chơi, màn credit, dialog pause, màn over. Mỗi màn hình có logic update, render và xử lý input khác hẳn nhau, nhưng chia sẻ chung resource (renderer, font, audio). State pattern là cách tổ chức để mỗi màn hình thành một class độc lập, game loop chỉ delegate cho state hiện tại mà không cần biết chi tiết.

## Hợp đồng năm method

Mỗi state implement năm method tương ứng với các pha trong vòng đời của state:

```cpp
class State {
public:
    virtual void Init();    // gọi khi state trở thành active
    virtual void Update();  // mỗi frame: chạy logic
    virtual void Draw();    // mỗi frame: render
    virtual void Handle();  // mỗi frame: xử lý input
    virtual void Exit();    // gọi khi rời state
};
```

Tại sao tách `Init` khỏi constructor và `Exit` khỏi destructor? Vì lifecycle của state không trùng với lifecycle của object. Khi `LogoState::Handle()` gọi `new PlayState(core)` để chuẩn bị transition, constructor chạy ngay nhưng state mới chưa thực sự active. `Init` được trì hoãn tới khi state machine swap — đảm bảo resource SDL (texture, surface) chỉ được tạo khi state đã sẵn sàng nhận render. Tương tự, `Exit` cho phép cleanup logic độc lập với `delete`, vì state machine có thể không gọi `delete` ngay (xem mục dưới về memory).

## State machine và lazy transition

Class trung tâm là `MachineState` giữ `currentState` và `nextState`. `changeState()` *không* swap ngay — chỉ set `nextState`. Swap thực sự xảy ra ở đầu hàm `Update()` của loop kế:

```cpp
void MachineState::Update() {
    if (currentState != nextState) {
        if (currentState != NULL) currentState->Exit();
        nextState->Init();
        currentState = nextState;
    }
    currentState->Update();
    currentState->Draw();
}
```

Lazy transition giải quyết một bẫy ngầm: nếu `LogoState::Handle()` gọi `changeState(new PlayState(core))` và swap ngay lập tức, các dòng code phía sau trong cùng hàm `Handle()` vẫn đọc `this->choiceState` — nhưng `this` đã `Exit` xong, các invariant có thể đã bị phá. Lazy transition đảm bảo state hiện tại được "đọc xong" trong frame của nó trước khi nhường chỗ. Pattern này có tên kỹ thuật là *deferred state transition*, cùng họ với double buffering rendering và copy-on-write — *thay đổi không hiệu lực ngay, đợi điểm an toàn.*

## Khác với state machine cho parser

State pattern trong game khác với state machine của HTTP parser ([HTTP parser dạng máy trạng thái](../Web%20development/HTTP%20parser%20d%E1%BA%A1ng%20m%C3%A1y%20tr%E1%BA%A1ng%20th%C3%A1i.md)) ở hai điểm:

- **Transition trigger**: parser tự transition theo dữ liệu (gặp space → đổi state). Game state transition theo *quyết định* của state hiện tại (user nhấn Enter → state chọn chuyển sang Play).
- **Behavior per state**: parser chỉ thay đổi cách interpret byte. Game state có toàn bộ vòng đời (Init/Update/Draw/Handle/Exit) — gần với *State pattern* của Gang of Four hơn là FSM thuần.

Game Programming Patterns gọi đây là *"changing behavior by changing the object it delegates to"* — game loop không có if/switch theo loại màn hình, chỉ gọi `currentState->Update()` và để polymorphism làm việc.

## Khi nào cần pushdown automaton

State machine cơ bản chỉ nhớ state hiện tại — không nhớ đã từng ở đâu. Khi cần dialog pause overlay (rời play tạm thời, rồi quay lại đúng chỗ), cần thêm stack: push state mới lên, pop để quay lại. Nystrom gọi đây là *pushdown automaton*. Code snake không cần tới mức này — chỉ ba state phẳng — nhưng đáng nhớ cho game phức tạp hơn.

## Trải nghiệm cá nhân

Pattern được internalize qua snake game thời 2016–2017 ([repo sdl_game/snake](../../references/repos/sdl_game/snake/)). Lý do chọn năm method là *đảm bảo Single Responsibility Principle*: mỗi method một trách nhiệm rõ ràng, dễ override khi tạo state mới. Lý do dùng lazy transition là *trạng thái hiện tại không bị phá khi đang xử lý — tránh bug conflict data*. Hiện tại nhìn lại, design có một số chỗ có thể cải thiện: `MachineState` không nên là singleton, `isRunning` không nên ở trong `MachineState` mà ở `Game`. Chi tiết trong [transcript phỏng vấn](../../references/interviews/state-pattern-va-singleton-machinestate.md).

## Nguồn tham khảo

- [Game Programming Patterns - State](https://gameprogrammingpatterns.com/state.html) — Robert Nystrom, chương về state pattern và pushdown automaton trong game
- [Gang of Four - State Pattern](https://en.wikipedia.org/wiki/State_pattern) — định nghĩa gốc của pattern
- [Source sdl_game/snake/State.h - hợp đồng năm method](../../references/repos/sdl_game/snake/State.h)
- [Source sdl_game/snake/MachineState.cpp - lazy transition](../../references/repos/sdl_game/snake/MachineState.cpp)
- [Source sdl_game/snake/LogoState.cpp - state concrete với menu](../../references/repos/sdl_game/snake/LogoState.cpp)

## Liên kết tri thức

- [Game loop cơ bản - game loop delegate Update/Draw/Handle cho state hiện tại](./Game%20loop%20c%C6%A1%20b%E1%BA%A3n.md)
- [HTTP parser dạng máy trạng thái - cùng họ state machine nhưng transition tự động theo dữ liệu thay vì quyết định](../Web%20development/HTTP%20parser%20d%E1%BA%A1ng%20m%C3%A1y%20tr%E1%BA%A1ng%20th%C3%A1i.md)
- [Cấp resource ở đâu, giải phóng ở đó - bug memory khi viết Exit của state là nguồn rút ra quy tắc này](../System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md)
- [Observer pattern - cùng họ design pattern delegation, callback vs delegation tới state](../System%20level/Observer%20pattern.md)
