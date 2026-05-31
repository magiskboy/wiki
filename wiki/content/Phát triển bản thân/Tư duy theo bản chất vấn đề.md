---
tags:
  - mindset
date: 2026-05-29
---
# Tư duy theo bản chất vấn đề

Tư duy theo bản chất vấn đề là cách tiếp cận một bài toán bằng việc xác định đặc tính cốt lõi của nó trước, rồi mới chọn công cụ và giải pháp phù hợp, thay vì xuất phát từ quan điểm hay sở thích cá nhân. Quyết định kỹ thuật được đặt trên đặc tính của vấn đề, không phải trên thói quen của người giải.

Một minh họa là việc lựa chọn giữa lập trình hướng đối tượng và lập trình hướng thủ tục cho một RESTful API. Đặc tính cốt lõi của REST là stateless: server không lưu trạng thái của request từ client, các request độc lập với nhau. Lập trình hướng đối tượng duy trì trạng thái trong các object, còn lập trình hướng thủ tục chỉ tập trung vào logic xử lý với đầu vào và đầu ra. Vì bản chất stateless không cần lưu trạng thái, lập trình hướng thủ tục là lựa chọn hợp lý hơn nhờ đơn giản, dễ bảo trì và dễ kiểm thử. Lựa chọn này đến từ bản chất stateless của REST chứ không từ định kiến rằng một kiểu lập trình luôn tốt hơn kiểu còn lại.

Tư duy theo bản chất gắn liền với việc trừu tượng hóa và mô hình hóa vấn đề trong đầu trước khi thao tác. Khi nhìn ra bản chất, nhiều công nghệ phức tạp trở nên dễ tiếp cận: Protocol Buffer bản chất là một bộ serializer và deserializer dữ liệu, còn RESTful API và gRPC bản chất đều là lời gọi function. Hiểu được lớp trừu tượng cốt lõi giúp tiếp cận và xử lý vấn đề nhanh hơn vì người giải làm việc với khuôn mẫu tổng quát thay vì các chi tiết bề mặt rời rạc.

# Nguồn tham khảo

- [Mình rút ra được những bài học gì sau 4 năm làm lập trình viên - Phần 1](https://www.nkthanh.dev/posts/minh-rut-ra-duoc-nhung-bai-hoc-gi-sau-4-nam-lam-lap-trinh-vien-phan-1)
- [Trải nghiệm làm mentor trong 1 năm](https://www.nkthanh.dev/posts/trai-nghiem-lam-mentor-trong-1-nam)

# Liên kết tri thức

- [Sự tương đồng trong tư duy của trí tuệ nhân tạo và con người](../AI%20v%C3%A0%20Machine%20Learning/S%E1%BB%B1%20t%C6%B0%C6%A1ng%20%C4%91%E1%BB%93ng%20trong%20t%C6%B0%20duy%20c%E1%BB%A7a%20tr%C3%AD%20tu%E1%BB%87%20nh%C3%A2n%20t%E1%BA%A1o%20v%C3%A0%20con%20ng%C6%B0%E1%BB%9Di.md) - Trừu tượng hóa từ hiện tượng để rút ra quy luật là cùng một công thức quan sát – lý luận – tổng quát hóa
- [Hiểu công nghệ trước khi áp dụng](./Hi%E1%BB%83u%20c%C3%B4ng%20ngh%E1%BB%87%20tr%C6%B0%E1%BB%9Bc%20khi%20%C3%A1p%20d%E1%BB%A5ng.md) - Hiểu bản chất một công nghệ là điều kiện để chọn và dùng nó đúng với đặc tính vấn đề
- [Phân tích đánh đổi khi đề xuất giải pháp](./Ph%C3%A2n%20t%C3%ADch%20%C4%91%C3%A1nh%20%C4%91%E1%BB%95i%20khi%20%C4%91%E1%BB%81%20xu%E1%BA%A5t%20gi%E1%BA%A3i%20ph%C3%A1p.md) - Đặc tính cốt lõi của vấn đề là căn cứ để cân nhắc ưu và nhược điểm giữa các giải pháp
- [Rèn luyện tư duy giải quyết vấn đề](./R%C3%A8n%20luy%E1%BB%87n%20t%C6%B0%20duy%20gi%E1%BA%A3i%20quy%E1%BA%BFt%20v%E1%BA%A5n%20%C4%91%E1%BB%81.md) - Khả năng tổng quát hóa bài toán được rèn luyện qua thực hành liên tục
- [Triết lý làm mentor](./Tri%E1%BA%BFt%20l%C3%BD%20l%C3%A0m%20mentor.md) - Người dẫn đường hướng mentee tới bản chất và mô hình hóa vấn đề thay vì thao tác cụ thể
- [OOP phù hợp cho game vì domain modeling](../Game%20development/OOP%20ph%C3%B9%20h%E1%BB%A3p%20cho%20game%20v%C3%AC%20domain%20modeling.md) - Ví dụ đối lập cho cùng tư duy: game stateful nhiều entity → chọn OOP, ngược với REST stateless → procedural
