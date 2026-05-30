---
tags:
  - web
date: 2026-05-29
---
# Time to First Byte

Time to First Byte (TTFB) là chỉ số đo thời gian từ khi request một tài nguyên tới khi nhận được byte response đầu tiên. TTFB đo lường thời gian kết nối và phản hồi của máy chủ, giúp phát hiện trường hợp server phản hồi request quá chậm. Với request điều hướng (request cho tài liệu HTML), TTFB đứng trước tất cả các chỉ số loading time khác.

## Các pha cấu thành

TTFB là tổng của các pha xảy ra trước khi byte đầu tiên về client:

- Thời gian điều hướng (redirect nếu có).
- Thời gian khởi động service worker (nếu có).
- Phân giải tên miền (DNS lookup).
- Thiết lập kết nối và khởi tạo TLS.
- Request tài nguyên cho tới khi nhận byte đầu tiên trong response.

Giảm độ trễ thiết lập kết nối và độ trễ khởi tạo backend góp phần làm giảm TTFB.

## Ngưỡng tốt

TTFB không phải là một Core Web Vital, nên một trang không bắt buộc phải đạt giá trị TTFB tốt miễn là nó không làm ảnh hưởng tới các chỉ số quan trọng. Tuy nhiên vì TTFB đứng trước các user-centric metric như First Contentful Paint (FCP) và Largest Contentful Paint (LCP), server cần phản hồi đủ nhanh để 75% người dùng đạt ngưỡng FCP tốt. Theo các nghiên cứu sơ bộ, đa số trang web nên hướng tới TTFB dưới 0.8 giây.

## Đo lường

TTFB đo được cả trong lab và trong field. Trong field dùng Chrome User Experience Report (CrUX) hoặc thư viện web-vitals; trong lab dùng network panel của Chrome DevTools hoặc WebPageTest. TTFB áp dụng cho mọi request chứ không riêng request điều hướng, và các tài nguyên cross-origin thường trễ hơn do phải thiết lập kết nối mới.

Trong JavaScript, TTFB của request điều hướng đo qua Navigation Timing API bằng PerformanceObserver:

```javascript
new PerformanceObserver((entryList) => {
  const [pageNav] = entryList.getEntriesByType('navigation');
  console.log(`TTFB: ${pageNav.responseStart}`);
}).observe({ type: 'navigation', buffered: true });
```

TTFB của các tài nguyên đo qua Resource Timing API với cùng cơ chế nhưng lấy entry `resource`. Một số tài nguyên trả về `responseStart` bằng 0 do được lấy từ cache hoặc do tài nguyên cross-origin không có header `Timing-Allow-Origin`, trong đó cross-origin không đặt header này thì không thể đo TTFB trong lab. Vì không phải browser nào cũng hỗ trợ PerformanceObserver hay cờ `buffered`, thư viện web-vitals là cách đo đơn giản và tương thích rộng hơn qua hàm `onTTFB`.

## Cải thiện

Cải thiện TTFB phụ thuộc phần lớn vào nhà cung cấp hosting và stack backend. Giá trị TTFB cao thường do hạ tầng không đủ tải, server thiếu bộ nhớ dẫn tới thrashing, bảng cơ sở dữ liệu không được tối ưu, hoặc cấu hình database dưới mức tối ưu. Các biện pháp gồm chọn nhà cung cấp có hạ tầng đáp ứng cao kết hợp CDN, dùng Server-Timing API để thu thập dữ liệu hiệu năng backend, tránh nhiều lần redirect, preconnect tới server cross-origin, thêm origin vào danh sách HSTS preload để bỏ độ trễ redirect HTTP sang HTTPS, dùng HTTP/2 hoặc HTTP/3, cân nhắc predictive prefetching, và ưu tiên server-side generation (SSG) thay cho server-side rendering (SSR) khi có thể.

# Nguồn tham khảo

- [Time to First Byte (TTFB)](https://www.nkthanh.dev/posts/time-to-first-byte)
- [web.dev — Time to First Byte](https://web.dev/articles/ttfb)

# Liên kết tri thức

- [Hiệu năng web](./Hi%E1%BB%87u%20n%C4%83ng%20web.md) - TTFB đứng trước FCP và LCP nên ảnh hưởng toàn bộ các user-centric metric
- [Tối ưu hiệu năng web](./T%E1%BB%91i%20%C6%B0u%20hi%E1%BB%87u%20n%C4%83ng%20web.md) - Caching và giảm thời gian SSR là biện pháp chung để hạ TTFB
- [Công cụ đo lường hiệu năng web](./C%C3%B4ng%20c%E1%BB%A5%20%C4%91o%20l%C6%B0%E1%BB%9Dng%20hi%E1%BB%87u%20n%C4%83ng%20web.md) - Network panel của DevTools đo TTFB trong lab
- [TTFT và TPOT](../AI%20v%C3%A0%20Machine%20Learning/TTFT%20v%C3%A0%20TPOT.md) - TTFT là metric đối ứng của TTFB trong ngữ cảnh LLM serving
