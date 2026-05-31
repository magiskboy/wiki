---
tags:
  - mindset
  - infrastructure
date: 2026-05-29
---
# Khởi tạo dự án phần mềm

Quá trình khởi tạo và thiết lập một dự án phần mềm, đặc biệt là các dự án tích hợp hệ thống doanh nghiệp (enterprise), đòi hỏi sự quan tâm đến nhiều khía cạnh kỹ thuật và quy trình để đảm bảo khả năng vận hành, bảo trì và mở rộng sau này.

## Tối thiểu hoá khối lượng công việc

Việc tối ưu hoá nguồn lực giúp nhóm phát triển có thể tập trung vào chất lượng cốt lõi của sản phẩm:

- **Lựa chọn công nghệ**: Ưu tiên sử dụng các stack công nghệ mà nhóm hoặc người dẫn dắt (leader) đã có chuyên môn và kinh nghiệm triển khai.
- **Tận dụng tối đa công cụ có sẵn**: Sử dụng các giải pháp như hệ quản trị nội dung (CMS) hoặc tính năng quản trị có sẵn của framework thay vì xây dựng lại từ đầu.
- **Tự động hoá quy trình**: Thiết lập pipeline CI/CD, tự động kiểm tra mã nguồn (linting, formatting) và tự động tạo tài liệu hệ thống (như OpenAPI) để giảm thiểu các tác vụ thủ công lặp lại.

## Quản lí mã nguồn

- Áp dụng mô hình **Gitflow** một cách rõ ràng, chuẩn hoá quy trình phân nhánh giúp cho làm việc nhóm hiệu quả và tạo tiền đề thuận lợi cho việc xây dựng các công cụ tích hợp liên tục (CI/CD).

## Khả năng quan sát (Observability)

Khả năng theo dõi trạng thái hệ thống và ứng dụng là yếu tố bắt buộc để chẩn đoán, phát hiện và khắc phục sự cố sớm:

- **Giám sát tài nguyên (Monitoring)**: Đo lường các chỉ số như CPU, RAM, lưu lượng request và các kết nối tới cơ sở dữ liệu.
- **Phát hiện sự cố ứng dụng**: Thiết lập cơ chế gửi cảnh báo lỗi tự động tới các công cụ trao đổi công việc (Teams, Slack) hoặc email chuyên trách. Cảnh báo cần bao gồm thông tin về exception, thông tin request và môi trường thực thi.
- Duy trì việc ghi log (logging) một cách đầy đủ cho các luồng xử lí nghiệp vụ.

## Bảo mật và dữ liệu người dùng

Chủ động đánh giá và triển khai các rào chắn bảo mật hệ thống từ giai đoạn sớm nhất:

- **Bảo mật hạ tầng**: Kích hoạt tường lửa ứng dụng web (WAF) để ngăn chặn các cuộc tấn công phổ biến (như SQL Injection, XSS). Sử dụng các công cụ rà soát lỗ hổng (vulnerability scanning, ví dụ: Trivy) định kì trên mã nguồn và container image.
- **Bảo mật dữ liệu**: Áp dụng kiểm soát truy cập dựa trên vai trò (Role-based access), thiết lập giới hạn vòng đời của token xác thực, thiết lập dung lượng tối đa và định dạng cho phép tải lên.

## Tổ chức mã nguồn (Clean Code)

- Tuyệt đối không gán cứng (hardcode) dữ liệu nhạy cảm hoặc thay đổi nhiều, cần lưu trữ tập trung ở biến môi trường hoặc hệ thống cấu hình.
- Phân tầng mã nguồn rõ ràng (ví dụ: kiến trúc 3 lớp) và phân vùng theo tính năng (module hoá).
- Áp dụng các Design Pattern phổ biến và phù hợp.

# Nguồn tham khảo

- [Những vấn đề cần quan tâm khi bắt đầu một dự án phần mềm](https://www.nkthanh.dev/posts/experience-to-start-a-new-project)
