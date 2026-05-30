---
tags:
  - web
date: 2026-05-29
---
# Gom monorepo build vào một Node.js runtime

Workflow phổ biến trong monorepo Node.js là dùng `yarn workspaces foreach` (hoặc lerna `run`, npm script lặp qua package) để chạy `build` trên từng sub-package. Mỗi lần chạy như vậy spawn một process Node.js mới và khởi tạo lại runtime — load V8, init module system, parse `package.json`, resolve dependencies. Chi phí khởi tạo cố định (~80-300ms cold, ~30-100ms warm) cộng dồn nhanh khi monorepo có hàng chục package. Một build tool tối ưu hơn gộp toàn bộ pipeline vào một process Node duy nhất, gọi bundler (Rollup, esbuild) qua API thay vì CLI.

## Phép tính chi phí

Một monorepo 30 package, build tuần tự bằng `yarn foreach`:

- Mỗi spawn Node ~150ms (cold cache, môi trường CI typical)
- Mỗi spawn Yarn wrapper ~200ms (Yarn 1) hoặc ~50ms (Yarn Berry PnP)
- 30 package × 350ms ≈ 10s tax thuần startup, *trước khi bundler chạy bất cứ việc gì*

Với single-runtime tool, chi phí cố định chỉ phát sinh một lần — phần còn lại là build thực sự. Khi build mỗi package mất ~500ms-2s, tax startup chiếm 10-30% tổng thời gian, đáng để loại bỏ.

## Cách triển khai

teko-kit là một ví dụ cụ thể: thay vì exec rollup CLI cho mỗi package, nó import `rollup` programmatically và gọi `rollup.rollup(options)` trong cùng process. Mỗi `Package` instance giữ một `PackageBuilder` riêng (cấu hình Rollup khác nhau), nhưng tất cả chia sẻ một event loop.

```javascript
class PackageBuilder {
  async build() {
    const builder = await rollup.rollup(this.options);
    await Promise.all(outputOptions.map(builder.write));
    await builder.close();
  }
}
```

Các tool monorepo trưởng thành áp dụng cùng triết lý: Nx có "Nx CLI daemon" giữ process sống và serve build request; Turborepo có một process gốc đọc cache và spawn child worker khi cần; Rush dùng plugin-based runner trong cùng process.

## Đánh đổi cần biết

Một runtime chung không phải lúc nào cũng hơn:

- **Memory leak lan giữa các build**: nếu Rollup plugin giữ reference, build package thứ 30 mang theo "rác" của 29 package trước. Process tách bạch không có vấn đề này.
- **OOM một lần là chết cả pipeline**: package có config nặng làm hết heap → toàn bộ pipeline crash, không phải mỗi package đó.
- **Khó isolate failure**: stack trace từ một package có thể bị nhiễu bởi async state của package khác.
- **Worker_threads là lối thoát**: cho phần CPU-bound (như `tsc` emit declaration), có thể dispatch sang worker thread để không block event loop chính mà vẫn ở trong một process. teko-kit dùng pattern này trong `worker.js` cho TypeScript compile.

## Khi nào nên đi hướng này

- Monorepo có > 10 package, build chạy CI mỗi commit
- Bundler/tooling expose programmatic API (Rollup, esbuild, swc, Vite đều có)
- Có cấu hình build chung phần lớn các package
- Chấp nhận đầu tư viết tool nội bộ thay vì dùng tool có sẵn (Nx, Turborepo là lựa chọn dễ hơn nếu không có constraint riêng)

## Trải nghiệm cá nhân

teko-kit (viết tại Teko, 5/2025) được tạo chính vì lý do này — `yarn foreach` trên monorepo của Teko Web chạm trần thời gian build chấp nhận được trên CI. Single-runtime cộng với dependency-aware orchestration (xem [Điều phối build qua dependency graph](../System%20level/%C4%90i%E1%BB%81u%20ph%E1%BB%91i%20build%20qua%20dependency%20graph%20v%C3%A0%20observer%20pattern.md)) là hai cải tiến chính. README repo ghi rõ "Single Node.js process eliminates the overhead of spawning multiple runtimes" là động lực thiết kế đầu tiên.

## Nguồn tham khảo

- [Source teko-kit - bin/cli.js dispatch trong một process](https://github.com/magiskboy/teko-kit/blob/master/bin/cli.js)
- [Source teko-kit - PackageBuilder gọi Rollup programmatic](https://github.com/magiskboy/teko-kit/blob/master/src/package-builder.js)
- [Source teko-kit - worker.js dùng worker_threads cho TS compile](https://github.com/magiskboy/teko-kit/blob/master/src/worker.js)
- [Rollup JavaScript API](https://rollupjs.org/javascript-api/)
- [Nx daemon process - architecture](https://nx.dev/concepts/nx-daemon)
- [Turborepo task graph engine](https://turbo.build/repo/docs/core-concepts/monorepos/task-dependencies)

## Liên kết tri thức

- [Điều phối build qua dependency graph và observer - cùng tool đi xa hơn với orchestration thông minh](../System%20level/%C4%90i%E1%BB%81u%20ph%E1%BB%91i%20build%20qua%20dependency%20graph%20v%C3%A0%20observer%20pattern.md)
- [Arbiter và worker trong ASGI server - đối lập triết lý: tách process để isolate; cần thiết khi workload là long-running server thay vì batch build](./Arbiter%20v%C3%A0%20worker%20trong%20ASGI%20server.md)
- [Hội nhập ecosystem qua interface có sẵn - dùng Rollup API thay vì CLI là một dạng bám interface có sẵn để tận dụng lifecycle hooks](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/H%E1%BB%99i%20nh%E1%BA%ADp%20ecosystem%20qua%20interface%20c%C3%B3%20s%E1%BA%B5n.md)
