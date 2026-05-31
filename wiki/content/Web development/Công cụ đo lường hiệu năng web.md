---
tags:
  - web
date: 2026-05-29
---
# Công cụ đo lường hiệu năng web

Việc tối ưu hiệu năng web bắt đầu từ đo lường. Các công cụ trong Chrome DevTools và Google PageSpeed cho biết chỉ số hiện tại là gì, chúng quan hệ với nhau ra sao và bundle đang gặp vấn đề gì, từ đó định hướng nơi cần tối ưu. Mỗi công cụ nên được chạy cả trước và sau mỗi lần tối ưu để theo dõi tiến độ.

## Lighthouse và PageSpeed

Lighthouse (mở trong Chrome DevTools) và [Google PageSpeed](https://pagespeed.web.dev) phân tích trang và đưa ra điểm số tổng quan cùng sáu user-centric metric, kèm danh sách vấn đề và gợi ý hướng giải quyết.

- Có thể đo nhiều khía cạnh như Performance, SEO; khi tập trung hiệu năng nên bỏ chọn các khía cạnh khác.
- Lighthouse đo được trên cả desktop và mobile, với mobile sẽ throttle network về 3G và throttle CPU để mô phỏng thiết bị yếu.
- Trong lúc Lighthouse phân tích cần tránh thực hiện tác vụ khác để giảm sai số.
- Công cụ này giúp phát hiện các vấn đề điển hình như JS bundle dư thừa, thời gian thực thi JS quá dài, lựa chọn thư viện chưa hợp lý làm giảm hiệu năng trên mobile, vi phạm best practice và thời gian phản hồi server thấp.

Điểm Performance tổng quan được tính bằng trung bình có trọng số của từng metric, mỗi metric mang một trọng số khác nhau. Lighthouse phân nhóm metric theo màu: đỏ là cần khắc phục, vàng là nên cải thiện, xanh là tốt và cần duy trì. Ngoài điểm số, công cụ còn đưa ra phần dự đoán mức cải thiện khả thi (ví dụ cắt JS thừa, giảm thời gian phản hồi server) và phần chẩn đoán nguyên nhân hiện tại. Vì điểm số chỉ mang tính tương đối tại thời điểm đo (phụ thuộc network và cấu hình máy), nên đo nhiều lần. Phần dự đoán thời gian phản hồi server có thể được kiểm chứng chính xác hơn bằng cách đo Time to First Byte trên nhiều request với công cụ như [wrk](https://github.com/wg/wrk).

## Performance Insight

Performance Insight (Chrome DevTools) cho cái nhìn chi tiết về trang theo thời gian, cho biết các user-centric metric diễn ra như thế nào theo trục thời gian. Nếu Lighthouse trả lời vấn đề là gì và chỉ số cao hay thấp, thì Performance Insight làm rõ các vấn đề quan hệ với nhau ra sao.

## Performance panel

Performance panel (Chrome DevTools) cho biết cách tối ưu thông qua bốn vùng thông tin:

- Biểu đồ tổng quan khối lượng công việc browser phải làm khi load trang, mỗi màu ứng với một loại tác vụ.
- Chi tiết resource và thứ tự được tải về khi load trang (Network).
- Chi tiết các function/task thực thi trên main thread cùng thứ tự và quan hệ giữa chúng.
- Cùng dữ liệu main thread nhưng trình bày theo nhiều cách như Summary, Bottom-Up, Call Tree và Event Log.

## webpack-bundle-analyzer

[webpack-bundle-analyzer](https://www.npmjs.com/package/webpack-bundle-analyzer) phân tích bundle để phát hiện các vấn đề về kích thước và cấu trúc bundle, gồm code server bị bundle lẫn với client, duplicate module, và thư viện dùng CommonJS khiến bundle không thể tree shaking.

## React Developer Tools

React Developer Tools là extension trình duyệt giúp profiling ứng dụng React qua tab Profiler trong DevTools; ứng dụng cần chạy trong component Profiler của React. Việc đo bắt đầu bằng nút reload để record quá trình load và kết thúc bằng nút stop, sau đó kết quả hiển thị dưới dạng Flamegraph hoặc Ranked.

Công cụ này phản ánh quá trình render của React: mỗi lần render, React dựng component thành DOM Node (phase render) rồi so sánh với DOM Node hiện tại, chỉ thay thế khi khác biệt (phase commit), nên số lần render lớn hơn hoặc bằng số lần commit. Flamegraph thể hiện phân bố thời gian của một lần commit, trong đó thời gian render của component cha bằng tổng thời gian render của các component con cộng thời gian render chính nó. Barchart liệt kê thời gian render của từng commit; khi tối ưu nên click vào các cột cao nhất hoặc màu vàng vì đó là các commit tốn thời gian render nhất.

# Nguồn tham khảo

- [Optimize web performance](https://www.nkthanh.dev/posts/optimize-web-performance)
- [Sử dụng Lighthouse và React Developer Tools để đánh giá hiệu năng web](https://www.nkthanh.dev/posts/su-dung-lighthouse-va-react-developer-tools-de-danh-gia-hieu-nang-web)
- [Lighthouse](https://developer.chrome.com/docs/lighthouse/overview)
- [webpack-bundle-analyzer](https://www.npmjs.com/package/webpack-bundle-analyzer)

# Liên kết tri thức

- [Hiệu năng web](./Hi%E1%BB%87u%20n%C4%83ng%20web.md) - Công cụ định lượng các user-centric metric của trang
- [Tối ưu hiệu năng web](./T%E1%BB%91i%20%C6%B0u%20hi%E1%BB%87u%20n%C4%83ng%20web.md) - Kết quả đo lường định hướng các biện pháp tối ưu cần áp dụng
- [Khởi tạo dự án phần mềm](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Kh%E1%BB%9Fi%20t%E1%BA%A1o%20d%E1%BB%B1%20%C3%A1n%20ph%E1%BA%A7n%20m%E1%BB%81m.md) - Đo lường hiệu năng bổ trợ cho việc giám sát (observability) hệ thống
- [Time to First Byte](./Time%20to%20First%20Byte.md) - Đo TTFB là cách kiểm chứng chính xác thời gian phản hồi server mà Lighthouse dự đoán
