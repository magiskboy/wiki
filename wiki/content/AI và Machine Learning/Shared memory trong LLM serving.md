---
tags:
  - infrastructure
  - ai
date: 2026-05-29
---
# Shared memory trong LLM serving

`/dev/shm` (POSIX shared memory) là một biến hạ tầng nhỏ nhưng có nhiều vai trò chồng lên nhau trong một worker LLM, nên một giá trị cấu hình duy nhất ảnh hưởng tới nhiều thành phần khác nhau. Hiểu các vai trò này giải thích vì sao thiếu shared memory có thể làm hỏng cả việc load model lẫn việc khởi tạo đường truyền KV cache.

## Vai trò trong tensor parallel

vLLM chạy trên PyTorch, mà PyTorch dùng shared memory để chia sẻ dữ liệu giữa các tiến trình khi inference tensor parallel. Khi TP lớn hơn một, các worker process trao đổi qua segment shared memory; NCCL cũng tạo segment `/dev/shm/nccl-*` lúc khởi tạo. `/dev/shm` quá nhỏ làm bước tạo shared memory thất bại hoặc OOM.

## Vai trò trong khởi tạo UCX và NIXL

UCX dùng segment shared memory cho transport intra-node (`sm`: posix/sysv) và cho bước bootstrap/control lúc khởi tạo backend. Khi `/dev/shm` không đủ, UCX báo `shmget ... No space left on device`; trong container chạy user namespace có thể gặp lỗi permission khi tạo posix shm. UCX không khởi tạo được transport thì NIXL không tạo được backend, nên KV cache không truyền được giữa prefill và decode.

Trên Kubernetes, `/dev/shm` được cấp qua một volume tmpfs:

```yaml
volumes:
  - name: dshm
    emptyDir: { medium: Memory, sizeLimit: 16Gi }   # 16Gi vLLM, 80Gi TensorRT-LLM
volumeMounts:
  - { name: dshm, mountPath: /dev/shm }
```

## Một biến, nhiều hệ quả

Trên Kubernetes, `/dev/shm` thường là `emptyDir{medium: Memory}`, vừa quyết định khả năng chạy tensor parallel và khởi tạo UCX/NIXL, vừa cộng vào ngân sách bộ nhớ của pod. Đặt quá nhỏ thì vỡ ở pha load model hoặc pha truyền KV; đặt quá lớn thì ăn vào limit và đẩy pod tới OOM. Đây là một điểm phải cân bằng có chủ đích chứ không thể đặt tùy tiện.

## Trải nghiệm thực tế

Một giá trị `/dev/shm` duy nhất từng gây hai loại sự cố trái ngược: đặt quá nhỏ thì vỡ ở pha truyền KV (UCX không tạo được backend) hoặc ở multiproc tensor parallel; đặt quá lớn thì cộng vào limit và đẩy pod tới OOMKilled. Đây là lý do phải đặt `/dev/shm` có chủ đích theo backend (16Gi cho vLLM, 80Gi cho TensorRT-LLM) thay vì để mặc định hoặc tăng tùy tiện.

## Nguồn tham khảo

- [Disagg Communication - NVIDIA Dynamo (sharedMemory 16Gi vLLM, 80Gi TRT-LLM)](https://docs.nvidia.com/dynamo/dev/kubernetes-deployment/deployment-guide/disagg-communication)
- [NVIDIA Dynamo Multinode Deployment - shared memory cho distributed runtime](https://docs.nvidia.com/dynamo/latest/kubernetes/deployment/multinode-deployment.html)
- [UCX shared memory error (shmget no space)](https://github.com/openucx/ucx/issues/5280)
- [Kubernetes Volumes - emptyDir medium Memory](https://kubernetes.io/docs/concepts/storage/volumes/)

## Liên kết tri thức

- [UCX - shared memory là transport intra-node và là bước bootstrap khi khởi tạo](../System%20level/UCX.md)
- [NIXL - UCX không khởi tạo được vì thiếu shared memory thì NIXL không tạo được backend](./NIXL.md)
- [Ngân sách bộ nhớ pod trên Kubernetes - /dev/shm là tmpfs tính vào cgroup limit](../DevOps%20v%C3%A0%20Infrastructure/Ng%C3%A2n%20s%C3%A1ch%20b%E1%BB%99%20nh%E1%BB%9B%20pod%20tr%C3%AAn%20Kubernetes.md)
- [Vòng đời bộ nhớ khi load LLM - tensor parallel dùng shared memory ngay trong pha load](./V%C3%B2ng%20%C4%91%E1%BB%9Di%20b%E1%BB%99%20nh%E1%BB%9B%20khi%20load%20LLM.md)
- [Chọn transport trong Open MPI - BTL vader cũng dùng shared memory cho giao tiếp rank intra-node](../System%20level/Ch%E1%BB%8Dn%20transport%20trong%20Open%20MPI.md)
