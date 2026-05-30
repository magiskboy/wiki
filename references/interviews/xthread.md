# Phỏng vấn khai quật: xthread

- **Leaf**: xthread — pause/unpause và non-preemptive stop cho thread (`_source/track.md` > Personal > Tự cài lại bằng tay)
- **Repo**: https://github.com/magiskboy/xthread — mirror local: `references/repos/xthread/`
- **Thời điểm repo**: 2023-07-13 → 2023-07-14 (9 commit, 2 ngày)
- **Wiki node hiện có**: [dieu-khien-thread-bang-cooperative-event](../../wiki/System%20level/%C4%90i%E1%BB%81u%20khi%E1%BB%83n%20thread%20b%E1%BA%B1ng%20cooperative%20event.md) — đã có phần kiến thức nền từ source code, chưa có phần `[Trí nhớ]`
- **Phiên phỏng vấn**: 2026-05-24

## Bối cảnh

- [Trí nhớ] Thời điểm viết: tháng 7/2023, đang ở mảng SRE của Teko.
- [Trí nhớ] Không có project cụ thể buộc phải có thư viện này. Động lực sinh từ *quan sát chung*: nhiều dev trong team dùng `threading.Thread` sai cách.
- [Trí nhớ] Mục tiêu kép: (1) tạo công cụ giúp dev quản lý thread dễ và ít lỗi hơn, (2) tự củng cố kiến thức về threading và kỹ năng Python.
- [Trí nhớ] xthread là tool dạng practice/showcase, không phải tool nội bộ Teko bắt buộc dùng.

## Vấn đề thật muốn giải

Các anti-pattern khi dev dùng `threading.Thread` trần mà xthread muốn loại bỏ (user xác nhận toàn bộ):

- [Trí nhớ] Thread chạy mãi không dừng được vì code không có stop-flag chuẩn.
- [Trí nhớ] Exception trong target bị nuốt → bug âm thầm.
- [Trí nhớ] Quên `join()` → thread leak khi process exit.
- [Trí nhớ] Dev nhầm tưởng `Thread.stop()` tồn tại và đi tìm cách "kill" preemptive.
- [Trí nhớ] Mỗi dev tự viết một biến thể stop-flag → khó review.

## Tên gọi và triết lý API

- [Trí nhớ] "Threading for human" lấy cảm hứng có chủ đích từ `requests` ("HTTP for humans"). Mục tiêu là API dễ dùng nhất có thể.
- [Trí nhớ] Mục tiêu cho dev khả năng tự quản lý thread theo nhu cầu một cách dễ dàng — đó là lý do API có pause/unpause kèm callback, không vì một use case bắt buộc nào.

## Thiết kế đã chọn

### Composition thay vì subclass

- [Trí nhớ] Từ đầu chủ đích dùng composition (bao `threading.Thread`), không kế thừa. Lý do: dễ bảo trì.
- [Trí nhớ] Kiến thức composition pattern đến từ khoá *Design Pattern* (Toronto University, Coursera).

### threading.Event làm tín hiệu

- [Trí nhớ] Dùng hai `threading.Event` (`__is_running`, `__resume`) để quản lý flow theo hướng event-driven, chủ động hơn so với Lock/Condition.
- [Chưa chắc] Lý do cụ thể chọn Event thay vì Condition — không nhớ rõ.

### daemon=True cho thread bên trong

- [Trí nhớ] Chủ đích — xthread chỉ dành cho thread phụ, không được block main thread khi process exit.

### Mental model có sẵn

- [Trí nhớ] Cấu trúc code và kỹ thuật triển khai đã có sẵn trong đầu từ lâu. Tự tin với phần low-level Python nên có nhu cầu thì viết ra, không cần vẽ giấy hay tham khảo thư viện khác.

## Vùng vấp và bug

- [Chưa chắc] Không nhớ có bug bất ngờ nào lúc viết.
- [Bổ sung — nguồn] Git history (https://github.com/magiskboy/xthread/commits) xác nhận: 9 commit trong 2 ngày, không có commit "fix bug". Toàn bộ implementation ra hoàn chỉnh từ commit đầu (`bde8a5542b65`).

## Iterate sau commit đầu

- [Trí nhớ] Version 0.0.2 thêm 3 property `is_active`, `is_paused`, `is_running` vì sau khi tự dùng (dogfood) nhận ra logic bên ngoài cần query state mà API chưa cho phép.
- [Bổ sung — nguồn] Commit `e9994464a5ea` xác nhận đây là feature mới, không phải fix.

## Lifecycle sau publish

- [Trí nhớ] xthread là dự án practice/showcase. Không chắc có ai dùng thật.
- [Trí nhớ] Không quay lại maintain sau khi rời Teko.
- [Trí nhớ] Không có ý định viết lại trong 2026.

## Bài học đọng lại

- [Trí nhớ] Insight chính rút ra: **"API gọn quan trọng hơn flexibility — thừa option là độc"**.

## Mở rộng đồ thị tri thức

Hai mạch xuất hiện trong phiên này đáng nối tiếp:

- **Coursera > Design Pattern (Toronto University)**: leaf mới chưa có trong `_source/track.md`. Composition pattern dùng trong xthread là dẫn chứng cụ thể.
- **Triết lý "API gọn hơn flexibility"**: có thể tách node mindset riêng, nối với [phan-tich-danh-doi-khi-de-xuat-giai-phap](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Ph%C3%A2n%20t%C3%ADch%20%C4%91%C3%A1nh%20%C4%91%E1%BB%95i%20khi%20%C4%91%E1%BB%81%20xu%E1%BA%A5t%20gi%E1%BA%A3i%20ph%C3%A1p.md), [uu-tien-tinh-dung-dan-dai-han](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/%C6%AFu%20ti%C3%AAn%20t%C3%ADnh%20%C4%91%C3%BAng%20%C4%91%E1%BA%AFn%20d%C3%A0i%20h%E1%BA%A1n.md), [hieu-cong-nghe-truoc-khi-ap-dung](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Hi%E1%BB%83u%20c%C3%B4ng%20ngh%E1%BB%87%20tr%C6%B0%E1%BB%9Bc%20khi%20%C3%A1p%20d%E1%BB%A5ng.md).
