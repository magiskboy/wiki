---
tags:
  - mindset
date: 2026-05-29
---
# Đơn giản hơn linh hoạt trong thiết kế API

Khi thiết kế thư viện hay API công khai, có hai trục thường mâu thuẫn: đơn giản (ít tuỳ chọn, đường dùng rõ ràng) và linh hoạt (nhiều tuỳ chọn, hỗ trợ nhiều use case). Quan điểm cân bằng thường thấy là cả hai đều quan trọng, nhưng kinh nghiệm xây sản phẩm cho thấy đơn giản nên thắng linh hoạt khi phải chọn — thừa tuỳ chọn không phải tài sản mà là gánh nặng cho cả người dùng và người duy trì.

## Vì sao thừa tuỳ chọn là độc

Mỗi tuỳ chọn mới đẩy chi phí về ba phía:

- **Người dùng** phải đọc thêm tài liệu, hiểu ngữ nghĩa của mỗi tuỳ chọn, và ra quyết định khi gọi. Quá nhiều lựa chọn dẫn tới decision fatigue và lỗi cấu hình ngầm — bug khó tái hiện vì phụ thuộc tổ hợp tuỳ chọn ít gặp.
- **Người duy trì** phải viết test cho mọi tổ hợp, giữ tương thích ngược cho mọi tuỳ chọn đã expose, và chống lại sự cám dỗ xoá tuỳ chọn ít dùng vì có thể đã có người phụ thuộc.
- **Bề mặt API** phình ra theo cấp số nhân của tổ hợp tuỳ chọn, làm tài liệu khó tổ chức và lỗi corner-case khó tìm.

Zen of Python (PEP 20) diễn đạt cùng triết lý này: *"There should be one — and preferably only one — obvious way to do it"*. Tiểu luận "Worse Is Better" của Richard Gabriel khẳng định rằng cài đặt đơn giản (dù không hoàn hảo) thường thắng cài đặt hoàn chỉnh phức tạp trong thực tế, vì người dùng và contributor đều ưu tiên cái mình hiểu được. Rich Hickey trong "Simple Made Easy" tách hai khái niệm bị nhầm lẫn: *simple* (không bện) khác với *easy* (gần tay), và software dài hạn phải đầu tư vào *simple*.

## Trải nghiệm với xthread

xthread (viết tại Teko, 7/2023) là một dẫn chứng cá nhân của bài học này — nhìn từ phía ngược lại. API ban đầu có 6 callback (`on_started`, `on_paused`, `on_unpaused`, `on_stopped`, `on_error`, `on_result`), hai tham số ít dùng (`autostart`, `pause_timeout`), và cặp `pause`/`unpause` được thêm vì *"muốn cho dev quyền tự quản lý"* dù không có use case bắt buộc nào. Sau khi dùng và public PyPI, nhận ra phần lớn flexibility đó không có người dùng nhưng vẫn phải maintain và document. Nếu viết lại, một API tối thiểu chỉ cần `start`, `stop`, `is_running` đã đủ cho gần như mọi case.

## Khi nào tuỳ chọn là chính đáng

Không phải mọi tuỳ chọn đều là độc. Một tuỳ chọn được coi là chính đáng khi:

- hỗ trợ một use case không thể giải bằng default cộng composition
- nếu xoá, người dùng buộc phải fork hoặc viết lại đáng kể
- chi phí test và document cho tuỳ chọn đó nhỏ so với giá trị nó mang lại

Heuristic ngược chiều: nếu một tuỳ chọn chỉ "đẹp về khả năng" mà không có người dùng kêu thiếu, đó là dấu hiệu nên bỏ. Nguyên tắc YAGNI ("You Aren't Gonna Need It") của Extreme Programming nói cùng ý — chỉ thêm tính năng khi có nhu cầu thật, không vì tưởng tượng nhu cầu.

## Nguồn tham khảo

- [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/)
- [Worse Is Better - Richard P. Gabriel](https://www.dreamsongs.com/RiseOfWorseIsBetter.html)
- [Simple Made Easy - Rich Hickey](https://www.infoq.com/presentations/Simple-Made-Easy/)
- [YAGNI - Martin Fowler](https://martinfowler.com/bliki/Yagni.html)
- [Transcript phỏng vấn xthread - dẫn chứng cá nhân](../../references/interviews/xthread.md)

## Liên kết tri thức

- [Phân tích đánh đổi khi đề xuất giải pháp - đơn giản và linh hoạt là một cặp đánh đổi điển hình cần phân tích trước khi thêm tuỳ chọn](./Ph%C3%A2n%20t%C3%ADch%20%C4%91%C3%A1nh%20%C4%91%E1%BB%95i%20khi%20%C4%91%E1%BB%81%20xu%E1%BA%A5t%20gi%E1%BA%A3i%20ph%C3%A1p.md)
- [Ưu tiên tính đúng đắn dài hạn - giữ API gọn là một cách trả nợ trước cho người duy trì tương lai](./%C6%AFu%20ti%C3%AAn%20t%C3%ADnh%20%C4%91%C3%BAng%20%C4%91%E1%BA%AFn%20d%C3%A0i%20h%E1%BA%A1n.md)
- [Tư duy theo bản chất vấn đề - mỗi tuỳ chọn phải gắn với một bản chất nhu cầu thật, không phải tưởng tượng](./T%C6%B0%20duy%20theo%20b%E1%BA%A3n%20ch%E1%BA%A5t%20v%E1%BA%A5n%20%C4%91%E1%BB%81.md)
- [Điều khiển thread bằng cooperative event - xthread là dẫn chứng cụ thể đi ngược với triết lý này, là nguồn rút ra bài học](../System%20level/%C4%90i%E1%BB%81u%20khi%E1%BB%83n%20thread%20b%E1%BA%B1ng%20cooperative%20event.md)
- [Hội nhập ecosystem qua interface có sẵn - bám interface có sẵn cũng là một cách giữ API gọn, vì interface đó đã được tinh chỉnh qua nhiều iteration](./H%E1%BB%99i%20nh%E1%BA%ADp%20ecosystem%20qua%20interface%20c%C3%B3%20s%E1%BA%B5n.md)
- [Cấp resource ở đâu, giải phóng ở đó - quy tắc đơn giản dễ tuân thủ hơn API memory management phức tạp cho phép sai](../System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md)
- [OOP phù hợp cho game vì domain modeling - simple-first áp dụng cho cả tổ chức code, chọn cấu trúc đơn giản nhất đủ work trước khi nghĩ tới OOP nghiêm túc](../Game%20development/OOP%20ph%C3%B9%20h%E1%BB%A3p%20cho%20game%20v%C3%AC%20domain%20modeling.md)
