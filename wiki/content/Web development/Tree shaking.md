---
tags:
  - web
date: 2026-05-29
---
# Tree shaking

Tree shaking là kỹ thuật loại bỏ dead code khỏi bundle của ứng dụng web, qua đó giảm việc download, decompress, parse và execute code không cần thiết trên browser. Dead code là những đoạn code bị thừa trong artifact, ví dụ các feature của một dependency mà ứng dụng không dùng tới nhưng vẫn bị bundle vào output. Kỹ thuật này được hỗ trợ bởi các bundler như webpack, Rollup và esbuild, và là một biện pháp trực tiếp để giảm bundle size (ví dụ một ứng dụng giảm payload load trang từ 750kb xuống 340kb).

Tree shaking không phải tính năng bật/tắt một lần là xong: để hiệu quả cần liên tục monitor bundle, phát hiện code không tree shake được và áp dụng các kỹ thuật cấu trúc code phù hợp.

## Cơ chế hoạt động

Bundler dựng một dependency graph tại build time để biết thành phần nào phụ thuộc vào thành phần nào, từ đó xác định code dư thừa và loại bỏ trong quá trình minification. Điều kiện tiên quyết là code phải được cấu trúc sao cho bundler đọc được quan hệ phụ thuộc một cách tĩnh. Tree shaking chỉ diễn ra ở tầng application chứ không ở tầng library, vì chỉ ở application bundler mới biết đoạn code nào thực sự được dùng. Cách đơn giản để kiểm tra một thư viện có tree shake được hay không là bundle ứng dụng dùng thư viện đó rồi kiểm tra output có chứa code không sử dụng hay không.

## ESM là điều kiện cần

JavaScript có hai hệ thống module phổ biến là CommonJS (CJS) và ES Module (ESM). CJS cho phép import/export ở bất kỳ đâu, kể cả trong branching scope hay block scope tại runtime, khiến bundler không thể xác định tĩnh code nào được dùng. ESM bắt buộc import/export tại module scope một cách tường minh, nên bundler thấy rõ quan hệ phụ thuộc tại build time. Mặc định bundler không tree shake được code định dạng CJS, vì vậy ứng dụng browser nên dùng thư viện hỗ trợ ESM; entrypoint ESM khai báo ở trường `module` còn CJS ở trường `main` trong `package.json`.

## usedExports và sideEffects

Webpack có hai mức tối ưu trong tree shaking. `usedExports` gỡ những export không được dùng ở bất kỳ module nào trong ứng dụng, nhìn từ lá lên gốc của dependency graph. `sideEffects` bỏ qua toàn bộ một module khi không có nội dung nào của nó được sử dụng, nhìn từ gốc xuống để cắt cả subtree, nên hiệu quả hơn `usedExports`.

Một đối tượng có side-effect khi nó tác động lên trạng thái ngoài scope của nó, ví dụ gán giá trị cho biến global như `window` hay DOM; các hàm polyfill và việc import CSS là trường hợp side-effect phổ biến. Bundler mặc định coi thư viện là có side-effect hoàn toàn, nên giữ lại để tránh phá vỡ hành vi runtime. Khi một thư viện chắc chắn free side-effect, khai báo `"sideEffects": false` trong `package.json` để bật side-effect optimization; có thể liệt kê ngoại lệ như file CSS qua mảng `"sideEffects": ["dist/style.css"]`.

## Cấu trúc code thuận lợi cho tree shaking

Side-effect optimization chỉ phát huy khi code được chia thành các module đủ nhỏ và lỏng lẻo về phụ thuộc, tương tự lá nhỏ và khớp nối lỏng thì rung cây dễ rụng hơn. Một số thực hành cụ thể:

- Tránh viết nhiều thành phần dùng cho các entrypoint khác nhau vào cùng một file, vì `usedExports` đánh giá theo phạm vi toàn ứng dụng chứ không theo từng entrypoint, nên không loại được phần là dead code của riêng một entrypoint.
- Hạn chế `import * from '...'` vì nó báo cho bundler rằng toàn bộ thành phần của thư viện đều được dùng; chỉ import đúng thứ cần thiết.
- Tránh dùng class khi không cần, vì các thành phần của class có thể được dùng tại runtime nên bundler không tree shake được.
- Tránh bundle nhiều phiên bản của cùng một thư viện; cơ chế resolution như Plug'n'Play của Yarn Berry có thể tạo nhiều virtual package cho cùng một version (do peer dependency khác nhau) khiến cùng một đoạn code bị bundle nhiều lần, có thể kiểm tra bằng `yarn info`.
- Khi viết thư viện, giữ nguyên cấu trúc source code lúc compile (ví dụ `preserveModules: true` trong Rollup) để dễ kiểm soát tree shaking và tránh side-effect phát sinh từ quá trình bundle.

## Quan hệ với lazy loading và code splitting

Lazy loading và code splitting bổ trợ cho tree shaking bằng cách không tải toàn bộ code tại một thời điểm: mỗi route chỉ tải code của nó khi cần (`React.lazy`, `next/dynamic`, hoặc dynamic `import()` của JavaScript). Tuy nhiên với các chunk độc lập, webpack không tree shake được các exported module nếu chỉ dùng `usedExports`; lúc này `sideEffects` mới cắt được các nhánh không dùng trong từng chunk.

# Nguồn tham khảo

- [Tree Shaking](https://www.nkthanh.dev/posts/tree-shaking)
- [Tree Shaking cho ứng dụng web](https://www.nkthanh.dev/posts/tree-shaking-cho-ung-dung-web)
- [Theodo — Library tree shaking](https://blog.theodo.com/2021/04/library-tree-shaking)

# Liên kết tri thức

- [Tối ưu hiệu năng web](./T%E1%BB%91i%20%C6%B0u%20hi%E1%BB%87u%20n%C4%83ng%20web.md) - Tree shaking là biện pháp giảm bundle size, một hướng tối ưu chính
- [Hiệu năng web](./Hi%E1%BB%87u%20n%C4%83ng%20web.md) - Giảm bundle JS cải thiện Total Blocking Time và Speed Index
- [Công cụ đo lường hiệu năng web](./C%C3%B4ng%20c%E1%BB%A5%20%C4%91o%20l%C6%B0%E1%BB%9Dng%20hi%E1%BB%87u%20n%C4%83ng%20web.md) - webpack-bundle-analyzer phát hiện module không tree shake được
