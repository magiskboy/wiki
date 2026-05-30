---
tags:
  - web
date: 2026-05-29
---
# Observer pattern

Observer pattern (còn gọi là pub/sub pattern) là một behavioral design pattern, trong đó một object gọi là subject duy trì danh sách các dependent gọi là observer và tự động thông báo cho chúng mỗi khi trạng thái thay đổi, thường bằng cách gọi một method của observer. Pattern này giải quyết bài toán thông báo cho nhiều thành phần biết về sự thay đổi của một thành phần, qua đó giảm phụ thuộc giữa các thành phần và giúp mở rộng hệ thống mà không phải sửa nhiều mã nguồn.

## Cơ chế

Subject (observable) cung cấp ba thao tác cốt lõi: đăng ký một observer vào danh sách listener, hủy đăng ký một observer khỏi danh sách, và thông báo để trigger toàn bộ listener khi có thay đổi. Mỗi observer cài đặt một method `update` để nhận thông báo từ subject.

```typescript
class Observable {
  private observers: Observer[] = [];

  registerObserver(o: Observer) { this.observers.push(o); }
  unregisterObserver(o: Observer) {
    this.observers = this.observers.filter((x) => x !== o);
  }
  notifyObservers() { this.observers.forEach((o) => o.update()); }
}
```

## Áp dụng trong web frontend

Trong một ứng dụng web, data model đóng vai trò subject còn UI đóng vai trò observer: mọi thay đổi của data model được ánh xạ lên UI thông qua việc gọi `notifyObservers`. Một todo application minh họa rõ điều này khi tách thành model và view. Model (kế thừa observable) chứa toàn bộ logic quản lý danh sách task và gọi `notifyObservers` sau mỗi lần thêm hoặc cập nhật task. View (là observer) đăng ký với model lúc khởi tạo, cài đặt `update` để render lại danh sách lên DOM, đồng thời truyền các event từ UI ngược về model khi người dùng tương tác.

Việc tách model và view theo cách này tách phần logic ứng dụng khỏi phần hiển thị, giúp mã nguồn dễ đọc và dễ bảo trì. Cũng chính cơ chế này được các framework lớn như React, Angular và Vue dùng để quản lý state và đồng bộ lên UI.

# Nguồn tham khảo

- [Sử dụng observer pattern trong lập trình web](https://www.nkthanh.dev/posts/using-observer-pattern-in-web-development)
- [Wikipedia — Observer pattern](https://en.wikipedia.org/wiki/Observer_pattern)
- [Mã nguồn ví dụ todo-app](https://github.com/magiskboy/todo-observer-pattern)

# Liên kết tri thức

- [Khởi tạo dự án phần mềm](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Kh%E1%BB%9Fi%20t%E1%BA%A1o%20d%E1%BB%B1%20%C3%A1n%20ph%E1%BA%A7n%20m%E1%BB%81m.md) - Observer là một design pattern phổ biến được áp dụng khi tổ chức mã nguồn dự án
- [State pattern trong game - cùng họ design pattern delegation, observer notify nhiều subscriber còn state delegate cho object hiện tại](../Game%20development/State%20pattern%20trong%20game.md)
