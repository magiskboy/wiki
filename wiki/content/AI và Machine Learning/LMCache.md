---
tags:
  - ai
date: 2026-05-29
---
# LMCache

LMCache là một KVCache Management

# LMCache quản lý KVCache theo phân tầng lưu trữ
- L1 (GPU Memory): Tốc độ cao nhất, dung lượng hạn chế.
- L2 (CPU RAM): Nơi đầu tiên KV Cache được offload để giải phóng VRAM mà không làm mất dữ liệu hoàn toàn.
- L3 (Remote Storage/Disk): Sử dụng các giải pháp như Redis hoặc Distributed File System để chia sẻ cache giữa các node khác nhau trong cụm (cluster).

# Tái sử dụng KVCache hiệu quả
LMCache hỗ trợ 2 cơ chế tái sử dụng KVCache
- prefix caching (tương tự prefix caching của vLLM)
- non-prefix caching: CacheBlend. LMCache cố gắng tái sử dụng KVCache của từng segment thay vì chỉ match phần prefix, đây là một điểm cộng lớn so với prefix caching vốn có của vLLM.

# LMCache hỗ trợ disaggregation
LMCache có thể tích hợp với nhiều backend/transport mechanism để đạt được hiệu năng truyền tải KVCache tốt nhất như NIXL, UCX, ...

# Use cases
Những trường hợp nên sử dụng LMCache
- **RAG** và **QA trên tài liệu dài** với phần ngữ cảnh lặp lại
- **hội thoại nhiều lượt**
- triển khai **nhiều instance** cần **chia sẻ KV**
- mục tiêu hệ thống là **tách prefill và decode** trên cụm phân tán

Những trường hợp **không nên** sử dụng LMCache:
- workload có **độ đa dạng prompt cao** và **tỷ lệ trùng token thấp**
- KV cache gắn chặt với **kiến trúc và trọng số** mô hình, nên thay đổi phiên bản có thể làm **mất hiệu lực cache** hoặc gây **không nhất quán** nếu không quản lý versioning
- chi phí truyền tải cao, không bù đắp được cho chi phí tính toán

## Liên kết

- [Kiến trúc NVIDIA Dynamo trên Kubernetes - LMCache tích hợp làm lớp KV cache phân tán cho Dynamo](./NVIDIA%20Dynamo.md)
- [Kết nối vLLM và LMCache server trên Dynamo Kubernetes - failure mode multiprocess trên K8s](../vllm-lmcache-connection-on-dynamo-kubernetes.md)
- [Quá trình inference của Large Language Model - KV cache trong inference pipeline](./Qu%C3%A1%20tr%C3%ACnh%20inference%20c%E1%BB%A7a%20Large%20Language%20Model.md)
- [Retrieval-Augmented Generation - reuse KV cho context lặp lại](./Retrieval-Augmented%20Generation.md)
- [NIXL - LMCache tích hợp NIXL làm transport để chia sẻ KV cache giữa node](./NIXL.md)
- [ZeroMQ - heartbeat control giữa worker và LMCache server chạy trên ZeroMQ](../System%20level/ZeroMQ.md)
