---
tags:
  - infrastructure
  - ai
date: 2026-05-29
---
# UCX

UCX (Unified Communication X) là framework truyền thông hiệu năng cao cho HPC và AI, đóng vai trò backend transport mặc định bên dưới NIXL. UCX trừu tượng hóa nhiều loại đường truyền (shared memory, TCP, RDMA verbs, CUDA) sau một API thống nhất và tự chọn đường truyền tối ưu theo vị trí của hai đầu giao tiếp. Đây là lớp quyết định KV cache giữa hai GPU được chuyển qua cách nào.

## Ba tầng UCT, UCP, UCS

UCX gồm ba tầng. UCT (transport layer) trừu tượng hóa phần cứng, ánh xạ trực tiếp xuống driver Verbs, shared memory hoặc CUDA, cung cấp các thao tác short/bcopy/zcopy. UCP (protocol layer) là tầng giao thức cấp cao, chịu trách nhiệm chọn transport, phân mảnh thông điệp và dùng nhiều rail song song. UCS (service layer) là tiện ích nền (cấu trúc dữ liệu, quản lý bộ nhớ).

## Transport và tự chọn theo locality

UCX expose nhiều transport (gọi là TLS): `cuda_ipc` (GPU-to-GPU cùng node qua PCIe hoặc NVLink), `cuda_copy` và `gdr_copy` (copy tới/từ VRAM), `rc`/`dc`/`ud` (Verbs InfiniBand cho truyền liên node, trong đó `rc` hợp quy mô nhỏ, `dc`/`ud` hợp quy mô lớn), `tcp` (socket Ethernet), `sm` (shared memory intra-node), `self` (loopback).

Mặc định UCX dò mọi thiết bị và chọn transport theo bandwidth, latency và NUMA locality: hai tiến trình trên cùng node dùng shared memory hoặc `cuda_ipc`; hai node có RDMA dùng `rc`/`dc`; nếu chỉ có Ethernet thì dùng TCP. Người dùng ép lựa chọn này qua biến môi trường `UCX_TLS` (danh sách transport được phép) và `UCX_NET_DEVICES` (thiết bị mạng được dùng).

```yaml
# Cấu hình RDMA cho disaggregated serving (NVIDIA Dynamo)
env:
  - { name: UCX_TLS, value: "cuda_ipc,cuda_copy,rc" }   # GPU IPC + GPU staging + RDMA
  - { name: UCX_NET_DEVICES, value: "mlx5_0:1" }         # chỉ định HCA, tránh device bonded LID=0
```

Khi chỉ định `UCX_TLS` tường minh với bộ nhớ GPU, phải kèm `cuda_copy` hoặc `cuda_ipc` thì UCX mới nhận diện được buffer trên VRAM. Trong pod Kubernetes thiếu InfiniBand, một cấu hình thường gặp là ép `UCX_TLS=cuda_ipc,cuda_copy,self,sm` để chỉ dùng GPU IPC và shared memory, tránh UCX cố mở verbs device. Pin được bộ nhớ GPU cho RDMA còn cần capability `IPC_LOCK` trên container.

## Vai trò shared memory khi khởi tạo

UCX dùng segment shared memory cho transport intra-node (`sm`: posix/sysv) và cho bước bootstrap/control lúc khởi tạo. Khi `/dev/shm` không đủ dung lượng, UCX báo `shmget ... No space left on device`; trong container chạy user namespace có thể gặp lỗi permission khi tạo posix shm. Khi shared memory không khả dụng, UCX có thể không tìm được active messages transport và khởi tạo thất bại, kéo theo NIXL không tạo được backend. Đây là lý do triển khai trên Kubernetes thường phải tăng `/dev/shm`.

## Trải nghiệm thực tế

Để chẩn đoán vì sao KV cache không truyền được, cách nhanh nhất là chạy `ucx_info -d` ngay trong pod worker và xem memory domain của HCA có dòng `cuda (access,reg,cache)` hay không; nếu chỉ thấy `host` thì GPUDirect RDMA không hoạt động và transfer sẽ phải staging qua host. Lỗi `NIXL_ERR_BACKEND` ngay tại `createBackend` thường quy về việc UCX không tìm được transport phù hợp: thiết bị bonded `mlx5_bond_0` có LID=0, sai phiên bản UCX/OFED so với host, hoặc pod không được inject thiết bị RDMA.

## Nguồn tham khảo

- [Disagg Communication - NVIDIA Dynamo (UCX_TLS, ucx_info -d, nguyên nhân NIXL_ERR_BACKEND)](https://docs.nvidia.com/dynamo/dev/kubernetes-deployment/deployment-guide/disagg-communication)
- [UCX repository](https://github.com/openucx/ucx)
- [UCX FAQ - UCT/UCP/UCS, transport selection, GPU, TLS](https://github.com/openucx/ucx/blob/master/docs/source/faq.md)
- [UCX environment parameters](https://github.com/openucx/ucx/wiki/UCX-environment-parameters)
- [UCX shared memory error (shmget no space)](https://github.com/openucx/ucx/issues/5280)

## Liên kết tri thức

- [NIXL - NIXL dùng UCX làm backend transport mặc định để truyền KV cache](../AI%20v%C3%A0%20Machine%20Learning/NIXL.md)
- [RDMA - các transport rc/dc/ud của UCX là RDMA verbs trên InfiniBand](./RDMA.md)
- [Shared memory trong LLM serving - UCX cần shared memory cho transport intra-node và bootstrap](../AI%20v%C3%A0%20Machine%20Learning/Shared%20memory%20trong%20LLM%20serving.md)
- [Chọn transport trong Open MPI - đối ngẫu cấu hình, UCX ép dùng transport còn Open MPI ép bỏ UCX](./Ch%E1%BB%8Dn%20transport%20trong%20Open%20MPI.md)
- [NVIDIA Dynamo - chuyển KV giữa worker dựa trên NIXL trên nền UCX](../AI%20v%C3%A0%20Machine%20Learning/NVIDIA%20Dynamo.md)
