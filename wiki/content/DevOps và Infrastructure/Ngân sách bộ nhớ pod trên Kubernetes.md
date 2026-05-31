---
tags:
  - infrastructure
date: 2026-05-29
---
# Ngân sách bộ nhớ pod trên Kubernetes

Memory limit của pod trên Kubernetes nên được hiểu như một ngân sách chung. Mọi phần bộ nhớ nằm trong cgroup của pod đều tiêu vào ngân sách đó: bộ nhớ của tiến trình, cache của runtime, CUDA context, vùng `/dev/shm`, và các vùng offload xuống host RAM.

Vì vậy, khi pod bị `OOMKilled`, câu hỏi quan trọng không phải là từng cấu hình riêng lẻ có lớn hay không. Câu hỏi quan trọng là tổng các khoản cùng bị tính vào cgroup có vượt `limits.memory` hay không.

## Request, limit và cgroup

`requests.memory` là lượng memory mà scheduler dùng để chọn node phù hợp cho pod. `limits.memory` là mức trần mà kubelet cấu hình bằng cgroup để kernel enforce trong lúc pod chạy.

Khi tổng memory usage trong cgroup vượt `limits.memory`, kernel có thể kill tiến trình trong pod. Điểm dễ nhầm là `limits.memory` không chỉ áp lên RSS của tiến trình. Kubernetes cũng tính các volume memory-backed, ví dụ `emptyDir` dùng `medium: Memory`, vào memory usage của container.

## /dev/shm là một khoản trong ngân sách

Trong pod, `/dev/shm` thường là một tmpfs nằm trên RAM. Khi `/dev/shm` được tạo từ `emptyDir` với `medium: Memory`, dữ liệu ghi vào `/dev/shm` cũng tiêu memory của container.

Điều này đặc biệt quan trọng với workload LLM. `sharedMemory` lớn giúp các tiến trình giao tiếp nhanh hơn, nhưng phần dung lượng thực sự được dùng trong `/dev/shm` vẫn nằm trong cùng ngân sách với tiến trình Python, CUDA context, runtime inference, UCX/NIXL, và các buffer khác.

## Cách cộng bộ nhớ khi chạy LLM

```text
memory limit của pod
  = memory của tiến trình
  + peak host RAM khi load model
  + /dev/shm thực sự được dùng
  + KV cache hoặc buffer offload xuống host RAM
  + overhead của runtime, CUDA, UCX/NIXL
```

Nếu tổng các khoản này lớn hơn `limits.memory`, pod có thể bị `OOMKilled`.

Ví dụ một pod có `limits.memory = 512Gi`. Nếu cấu hình `sharedMemory` là `256Gi` và `host_cache_size` là `256Gi`, hai khoản này đã chiếm toàn bộ ngân sách trên giấy. Pod gần như không còn khoảng trống cho Python, CUDA context, UCX/NIXL, buffer tạm, và đỉnh host RAM khi load model.

```text
limits.memory                 = 512 Gi
sharedMemory                  = 256 Gi
host_cache_size               = 256 Gi
còn lại cho phần còn lại       = 0 Gi
nguy cơ OOMKilled              = rất cao
```

Vì vậy, cách xử lý không phải chỉ nhìn một giá trị rồi tăng hoặc giảm. Cần cộng toàn bộ ngân sách, sau đó quyết định giảm `/dev/shm`, giảm host KV/offload, giảm peak khi load model, hoặc tăng `limits.memory`.

## Ý nghĩa khi cấu hình inference đa GPU

Với inference đa GPU, `/dev/shm` thường phục vụ giao tiếp giữa process, tensor parallel, hoặc các transport như UCX/NIXL. NVIDIA Dynamo khuyến nghị `sharedMemory.size` khoảng `16Gi` cho vLLM và `80Gi` cho TensorRT-LLM, đồng thời thêm capability `IPC_LOCK` để NIXL/UCX có thể pin memory cho RDMA.

Các con số khuyến nghị này không thay thế cho bài toán ngân sách. Chúng chỉ là điểm bắt đầu để cấu hình shared memory. Pod vẫn cần đủ memory limit cho toàn bộ phần còn lại của workload.

## Trải nghiệm thực tế

Pod worker có thể bị `OOMKilled` dù từng tham số nhìn riêng có vẻ hợp lý. Nguyên nhân là `sharedMemory` và `host_cache_size` cùng tiêu vào memory limit của pod.

Trong trường hợp `sharedMemory = 256Gi`, `host_cache_size = 256Gi`, và `limits.memory = 512Gi`, ngân sách đã hết trước khi tính phần load model và runtime. Nâng một phần tài nguyên mà không cân lại toàn bộ ngân sách sẽ không giải quyết được OOM. Cần nhìn pod như một bảng cộng memory duy nhất.

## Nguồn tham khảo

- [Disagg Communication - NVIDIA Dynamo (khuyến nghị sharedMemory, IPC_LOCK)](https://docs.nvidia.com/dynamo/dev/kubernetes-deployment/deployment-guide/disagg-communication)
- [Kubernetes Resource Management - cgroup, memory-backed emptyDir](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kubernetes Volumes - emptyDir medium Memory (tmpfs)](https://kubernetes.io/docs/concepts/storage/volumes/)

## Liên kết tri thức

- [Vòng đời bộ nhớ khi load LLM - đỉnh host RAM lúc load là một khoản cộng vào ngân sách pod](../AI%20v%C3%A0%20Machine%20Learning/V%C3%B2ng%20%C4%91%E1%BB%9Di%20b%E1%BB%99%20nh%E1%BB%9B%20khi%20load%20LLM.md)
- [Shared memory trong LLM serving - /dev/shm vừa phục vụ tensor parallel và UCX vừa tính vào limit](../AI%20v%C3%A0%20Machine%20Learning/Shared%20memory%20trong%20LLM%20serving.md)
- [Quan sát hệ thống trong Kubernetes - theo dõi memory pod để phát hiện sớm nguy cơ OOM](./Quan%20s%C3%A1t%20h%E1%BB%87%20th%E1%BB%91ng%20trong%20Kubernetes.md)
- [Ràng buộc hạ tầng khi triển khai LLM - OOM do cộng dồn là biểu hiện coupling giữa cấu hình phần mềm và giới hạn phần cứng](../AI%20v%C3%A0%20Machine%20Learning/R%C3%A0ng%20bu%E1%BB%99c%20h%E1%BA%A1%20t%E1%BA%A7ng%20khi%20tri%E1%BB%83n%20khai%20LLM.md)
