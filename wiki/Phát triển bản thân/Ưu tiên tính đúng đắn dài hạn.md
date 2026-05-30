---
tags:
  - mindset
date: 2026-05-29
---
# Ưu tiên tính đúng đắn dài hạn

Một lỗi tư duy phổ biến là chỉ cố hoàn thành công việc để đáp ứng yêu cầu tức thời của task mà bỏ qua tính đúng đắn của toàn bộ dự án về lâu dài. Ưu tiên tính đúng đắn dài hạn là nguyên tắc chọn cách làm đúng với mục đích của công cụ và bền vững theo thời gian, thay vì cách làm chỉ vừa đủ để qua được nhu cầu trước mắt.

Một minh họa là việc ghi log. Để debug, nhiều người dùng các hàm in dữ liệu thay vì dùng chức năng logging của ngôn ngữ. Với mục đích trước mắt, hàm in thỏa mãn vì cả hai đều đẩy dữ liệu ra stdout và stderr. Nhưng về lâu dài và về khả năng mở rộng, cơ chế logging có ưu thế rõ rệt nhờ khả năng filter, định danh dữ liệu log và các tính năng vốn được sinh ra cho đúng công việc đó. Cách làm đúng tận dụng công cụ phù hợp với mục đích thật của vấn đề.

Tính đúng đắn dài hạn được củng cố bởi các thực hành ở giai đoạn khởi tạo dự án, như tổ chức mã nguồn rõ ràng, không gán cứng dữ liệu nhạy cảm, và duy trì việc ghi log đầy đủ cho các luồng nghiệp vụ. Đây là sự đầu tư cho khả năng bảo trì và mở rộng, đối lập với cách tối ưu hóa giá trị tạm thời của một task đơn lẻ.

# Nguồn tham khảo

- [Mình rút ra được những bài học gì sau 4 năm làm lập trình viên - Phần 1](https://www.nkthanh.dev/posts/minh-rut-ra-duoc-nhung-bai-hoc-gi-sau-4-nam-lam-lap-trinh-vien-phan-1)

# Liên kết tri thức

- [Khởi tạo dự án phần mềm](./Kh%E1%BB%9Fi%20t%E1%BA%A1o%20d%E1%BB%B1%20%C3%A1n%20ph%E1%BA%A7n%20m%E1%BB%81m.md) - Tổ chức mã nguồn và logging đầy đủ là các thực hành phục vụ tính đúng đắn dài hạn
- [Phân tích đánh đổi khi đề xuất giải pháp](./Ph%C3%A2n%20t%C3%ADch%20%C4%91%C3%A1nh%20%C4%91%E1%BB%95i%20khi%20%C4%91%E1%BB%81%20xu%E1%BA%A5t%20gi%E1%BA%A3i%20ph%C3%A1p.md) - Lựa chọn giữa giá trị tạm thời và giá trị dài hạn là một quyết định đánh đổi
- [Quy trình tạo niềm tin trong cộng tác](./Quy%20tr%C3%ACnh%20t%E1%BA%A1o%20ni%E1%BB%81m%20tin%20trong%20c%E1%BB%99ng%20t%C3%A1c.md) - Làm đúng theo chuẩn chung là điều kiện để kết quả công việc đáng tin theo thời gian
