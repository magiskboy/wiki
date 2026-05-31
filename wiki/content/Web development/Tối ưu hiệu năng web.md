---
tags:
  - web
date: 2026-05-29
---
# Tối ưu hiệu năng web

Tối ưu hiệu năng web hướng tới việc cải thiện các user-centric metric bằng hai nhóm biện pháp: giảm lượng JS mà browser phải thực thi (giảm main thread blocking) và rút ngắn thời gian load các blocking resource. Một nguyên tắc xuyên suốt là không lazy hoá những thành phần ảnh hưởng tới LCP và CLS.

## Tree shaking

Tree shaking là phương pháp loại bỏ dead code khỏi bundle, làm giảm kích thước file JS trả về client. Phương pháp này được hỗ trợ bởi các bundler như webpack, esbuild và rollup.

- Tree shaking chỉ thực hiện ở tầng application, không thực hiện ở tầng library, và chỉ hoạt động với ESM chứ không hỗ trợ CommonJS, nên ứng dụng trên browser cần hạn chế tối đa CommonJS.
- Để hỗ trợ bundler, nên khai báo trường `sideEffects` trong `package.json` với giá trị phù hợp và tránh `import * from ...`.
- Chỉ tách function ra shared package khi nó được dùng từ hai lần trở lên, và nên tách image ra file riêng phục vụ qua CDN thay vì bundle vào JS.
- Với ứng dụng hybrid như NextJS, code server dễ lẫn với code client nên cần dùng bundle analyzer như webpack-bundle-analyzer để theo dõi.

## Lazy import và lazy load

Lazy import giảm bundle size bằng cách chỉ import code của những tính năng cần thiết thay vì bundle toàn bộ. Ví dụ, code cho popup báo lỗi chỉ được load khi lỗi xảy ra, nên không tham gia vào bundle tại thời điểm load trang.

- Không lazy load những đoạn code ảnh hưởng tới LCP và CLS.
- Lazy import không tác động tới code chạy trên server.
- Tránh lạm dụng lazy import vì nó tạo ra các file JS quá nhỏ, làm giảm khả năng nén của web server và ảnh hưởng hiệu năng chung.
- Tận dụng lazy loading sẵn có của HTML như thuộc tính `loading` của `img`.

## Lazy hydrate

Lazy hydrate tránh việc code được thực thi không cần thiết, ví dụ chỉ render các component nằm trong viewport tại loading time để giảm thời gian CPU bị block. Kỹ thuật này thường kết hợp với IntersectionObserver. Vì việc phát hiện một component có trong viewport hay không do JS thực thi, nên các phần tử LCP không nên render bằng lazy hydrate.

## Time To First Byte

Time To First Byte (TTFB) không phải user-centric metric nhưng ảnh hưởng tới toàn bộ các chỉ số hiệu năng vì nó quyết định thời điểm resource bắt đầu về client. TTFB của file HTML quan trọng nhất do HTML là entrypoint của một webpage. Hai biện pháp cải thiện TTFB là caching và giảm thời gian SSR bằng cách loại bỏ các component không cần thiết.

## Tối ưu bandwidth khi loading

Tại thời điểm loading, giảm bandwidth giúp các resource quan trọng được load nhanh hơn và trang hiển thị sớm hơn.

- Tránh load thirdparty không quan trọng như tracking hay script marketing, và tránh preload quá nhiều resource.
- Chỉ đặt resource quan trọng trong thẻ `head`, chuyển các script không quan trọng xuống cuối thẻ `body`.
- Ưu tiên xử lý HTML tĩnh trước các resource như JS hay image chưa hiển thị trên trang.

## Tránh tác vụ làm trễ render

Hai nhóm thao tác làm tăng main thread blocking time cần tránh là [recalculate style](https://web.dev/articles/reduce-the-scope-and-complexity-of-style-calculations) (insert thẻ style, thay đổi style hàng loạt) và [layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing) (truy cập hoặc chỉnh sửa xen kẽ các thuộc tính vị trí và kích thước của element).

## Rủi ro từ script nhúng ngoài

Script do người quản lý website nhúng qua công cụ như Google Tag Manager (GTM) có thể phá bỏ kết quả tối ưu, vì GTM cho phép chèn JS, CSS, HTML một cách linh động ngoài tầm kiểm soát của codebase. Điểm số đo được vì vậy còn phụ thuộc vào script nhúng ngoài lẫn các yếu tố như thời gian phản hồi API, network và cấu hình máy người dùng.

# Nguồn tham khảo

- [Optimize web performance](https://www.nkthanh.dev/posts/optimize-web-performance)
- [web.dev — Reduce JavaScript payloads with tree shaking](https://web.dev/articles/reduce-javascript-payloads-with-tree-shaking)
- [web.dev — Reduce the scope and complexity of style calculations](https://web.dev/articles/reduce-the-scope-and-complexity-of-style-calculations)
- [web.dev — Avoid large, complex layouts and layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing)

# Liên kết tri thức

- [Hiệu năng web](./Hi%E1%BB%87u%20n%C4%83ng%20web.md) - Các biện pháp tối ưu nhắm vào các user-centric metric và các giai đoạn render
- [Công cụ đo lường hiệu năng web](./C%C3%B4ng%20c%E1%BB%A5%20%C4%91o%20l%C6%B0%E1%BB%9Dng%20hi%E1%BB%87u%20n%C4%83ng%20web.md) - Công cụ xác định điểm cần tối ưu trước và sau khi thực hiện
- [Tree shaking](./Tree%20shaking.md) - Chi tiết kỹ thuật loại bỏ dead code để giảm bundle size
- [Time to First Byte](./Time%20to%20First%20Byte.md) - Chi tiết chỉ số phản hồi server và cách hạ TTFB
- [Khởi tạo dự án phần mềm](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Kh%E1%BB%9Fi%20t%E1%BA%A1o%20d%E1%BB%B1%20%C3%A1n%20ph%E1%BA%A7n%20m%E1%BB%81m.md) - Caching và tự động hoá là thực hành chung giữa tối ưu hiệu năng và thiết lập dự án
