# Cài đặt operator trên cụm OpenShift air-gapped với oc-mirror

> Transcript phỏng vấn khai quật tri thức ngày 2026-05-23 — nguồn tham khảo gốc (primary source) cho phần tri thức trải nghiệm.
> Leaf gốc: Zen8labs → X company → "Setup K8s operators with air gaps cluster (keyword: oc-mirror, catalog, containers registry,...)".
> Trạng thái: đã chưng cất thành wiki — [Cài đặt operator trên OpenShift air-gapped](../../wiki/DevOps%20v%C3%A0%20Infrastructure/C%C3%A0i%20%C4%91%E1%BA%B7t%20operator%20tr%C3%AAn%20OpenShift%20air-gapped.md), [Multi-Instance GPU](../../wiki/AI%20v%C3%A0%20Machine%20Learning/Multi-Instance%20GPU.md).
>
> Quy ước marker:
> - **[Trí nhớ]** — do người dùng kể, là tài sản trải nghiệm gốc.
> - **[Bổ sung — nguồn]** — kiến thức nền do trợ lý bổ sung, kèm nguồn (cần verify link ở bước tinh).
> - **[Chưa chắc]** — vùng người dùng không nhớ rõ, giữ trung thực, không suy diễn.

## Bối cảnh

**[Trí nhớ]** Hệ thống ở X company, yêu cầu bảo mật thông tin nên air-gap hoàn toàn (không ra Internet). Toàn bộ nền tảng là Red Hat On-Premise, server đặt ngay cạnh chỗ ngồi.

**[Trí nhớ]** Cụm OpenShift chạy trên một VM (số node tương đối nhiều), nền quản lý là vSphere, hypervisor là VMware ESXi. GPU là NVIDIA A100 48GiB VRAM, chạy ở chế độ MIG.

**[Trí nhớ]** Driver GPU A100 do team khác cài và passthrough thẳng vào VM. Việc của người dùng là làm cho container nhận được GPU — tức cài GPU Operator và các thành phần phụ trợ.

## Bài toán gốc và cú sốc nhận thức

**[Trí nhớ]** Trước đây chỉ cài operator qua vài helm chart. Khi vào môi trường air-gap, không hình dung được phải pull image từ đâu và cài operator kiểu gì.

**[Bổ sung — nguồn]** OpenShift không cài operator qua helm mà qua OLM (Operator Lifecycle Manager) / OperatorHub, dựa trên `CatalogSource`. Trong môi trường disconnected phải mirror cả **catalog index image** (không chỉ image của operator), tạo `CatalogSource` trỏ về registry nội bộ, và tắt các default OperatorHub source vì chúng cố gọi ra `registry.redhat.io` rồi fail. (Nguồn cần verify: Red Hat OpenShift docs — "Disconnected installation mirroring" / "Using Operator Lifecycle Manager in disconnected environments".)

## Quy trình mirror

**[Trí nhớ]** Registry trong vùng air-gap đã có sẵn: Quay.

**[Trí nhớ]** Dùng một máy tính cá nhân có Internet để mirror image về máy đó trước. Các file tar rất nặng — tới ~71GiB. Sau đó copy sang bastion trong cụm air-gap rồi đẩy lên Quay.

**[Bổ sung — nguồn]** Đây đúng là mô hình hai pha của `oc-mirror`: pha "mirror-to-disk" (máy có mạng kéo image thành gói tar trên đĩa) và pha "disk-to-mirror" (bê đĩa vào vùng air-gap, push lên registry nội bộ). (Nguồn cần verify: Red Hat docs — "oc-mirror plugin".)

**[Trí nhớ]** `oc-mirror` rất nhạy với version: binary dùng ở hai pha lệch nhau, kể cả ở mức minor version, cũng có thể khiến hai pha không ăn khớp và fail.

**[Bổ sung — nguồn]** Khớp với việc Red Hat tách hai dòng v1/v2 định dạng không tương thích (có hướng dẫn migrate v1→v2) và yêu cầu push image set đúng thứ tự sequence; thực hành chuẩn là dùng cùng một version oc-mirror cho cả hai pha. (Nguồn: OKD docs — "Migrating from oc-mirror plugin v1 to v2".)

**[Trí nhớ]** Cấu hình sai vài lần ở khâu khai báo trước khi hiểu concept. Khi cấu hình đúng thì có 2 channel và có thể quy định mirror từng loại resource. Thứ cần mirror là 2 operator: **GPU Operator** và **NFD (Node Feature Discovery)**.

**[Bổ sung — nguồn]** Phần khai báo này là file `ImageSetConfiguration` của oc-mirror — nơi chọn catalog, package (operator) và channel để giới hạn phạm vi mirror. (Nguồn cần verify: Red Hat docs — "ImageSetConfiguration".) Lưu ý: gói ~71GiB lớn là dấu hiệu phạm vi mirror có thể đã rộng hơn mức cần; lọc đúng package/channel sẽ giảm dung lượng — điểm này nên kiểm lại ở bước tinh.

## Bài học đắt giá nhất (à-há của phiên)

**[Trí nhớ]** Sau khi mirror, người dùng **không** tạo cơ chế đổi hướng registry, mà apply thẳng các k8s definition lên OpenShift. Hệ quả: phải đi sửa tay registry từ `nvcr.io` và `registry.redhat.io` sang Quay trên từng resource — rất cực.

**[Bổ sung — nguồn]** `oc-mirror` tự sinh sẵn manifest `ImageContentSourcePolicy` (ICSP; bản mới là `ImageDigestMirrorSet`/IDMS) và `CatalogSource` trong thư mục kết quả (`oc-mirror-workspace/results-xxxx/`). Nếu `oc apply` đám này, cluster sẽ tự động đổi hướng mọi lệnh pull sang registry nội bộ, không phải sửa tay từng workload. Cái "rất cực" chính là cái giá của mảnh ICSP bị bỏ quên. (Nguồn cần verify: Red Hat docs — "Configuring image registry repository mirroring" / output của oc-mirror.)

**[Trí nhớ]** Nếu làm lại, điều muốn làm khác nhất: cập nhật registry (qua ICSP/IDMS do oc-mirror sinh) để không phải sửa từng workload.

## GPU Operator, NFD và MIG

**[Trí nhớ]** Hiểu về NFD: process nhận diện GPU trên node và gán các label đặc biệt của NVIDIA — node có hỗ trợ GPU, mode là MIG hay time-slicing, có bao nhiêu GPU, cấp phát được bao nhiêu.

**[Bổ sung — nguồn]** NFD phát hiện đặc tính phần cứng và dán label lên node; GPU Operator dựa vào đó để nhắm đúng node có GPU mà triển khai các thành phần (driver, container toolkit, device plugin, dcgm, mig-manager). (Nguồn cần verify: NVIDIA GPU Operator docs.)

**[Chưa chắc]** Việc có tắt `driver.enabled` trong `ClusterPolicy` (để Operator dùng driver passthrough sẵn có thay vì tự cài) — người dùng không nhớ và nghĩ là **chưa từng làm**. Để mở, không kết luận.

**[Trí nhớ]** MIG là cơ chế ảo hóa GPU, chia một GPU thành các vGPU nhỏ hơn; workload share GPU theo kiểu cô lập này thay vì time-slicing. Mỗi loại GPU có sẵn một số kiểu chia do nhà sản xuất định. Người dùng chia A100 thành **7 instance, mỗi instance 5GiB VRAM**. Bất ngờ: chia kiểu này có vẻ không tận dụng hết VRAM. Cần sửa một số rule trong một ConfigMap để quy định cách chia; process này nằm trong GPU Operator.

**[Bổ sung — nguồn]** 7×5GiB là profile nhỏ nhất `1g.5gb` của A100. VRAM không khớp tròn vì MIG cắt thành các slice cố định và giữ riêng overhead cho mỗi instance (7×5 = 35GiB lộ ra cho workload). Đây là đánh đổi của MIG: cô lập cứng (mỗi instance có SM + bộ nhớ + băng thông riêng) đổi lấy hao một phần dung lượng — khác time-slicing (chia sẻ mềm, không cách ly). ConfigMap được `mig-manager` (thành phần của GPU Operator) đọc; áp profile qua label `nvidia.com/mig.config` trên node. (Nguồn cần verify: NVIDIA MIG User Guide; GPU Operator MIG docs.)

## Vùng chưa khai thác / để mở

- **[Chưa chắc]** Có tắt driver trong ClusterPolicy hay không.
- Người dùng cho biết không còn mảnh nào khác đáng nhớ quanh chủ đề này (không nhớ pha verify `nvidia-smi` trong pod, monitoring dcgm-exporter, hay pha debug đặc biệt).

## Gợi ý liên kết đồ thị (cho bước tinh)

- [NVIDIA Dynamo](../../wiki/AI%20v%C3%A0%20Machine%20Learning/NVIDIA%20Dynamo.md) — cùng ngữ cảnh chạy AI/GPU trên Kubernetes; cách tư duy: cùng nền tảng triển khai.
- [Quá trình inference của LLM](../../wiki/AI%20v%C3%A0%20Machine%20Learning/Qu%C3%A1%20tr%C3%ACnh%20inference%20c%E1%BB%A7a%20Large%20Language%20Model.md) — MIG là cách cấp phát GPU cho workload inference; cách tư duy: hạ tầng phục vụ cho inference.
- [Phân tích đánh đổi khi đề xuất giải pháp](../../wiki/Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Ph%C3%A2n%20t%C3%ADch%20%C4%91%C3%A1nh%20%C4%91%E1%BB%95i%20khi%20%C4%91%E1%BB%81%20xu%E1%BA%A5t%20gi%E1%BA%A3i%20ph%C3%A1p.md) — MIG (cô lập cứng) vs time-slicing (chia sẻ mềm) là một đánh đổi điển hình; cách tư duy: cùng pattern đánh đổi.

## Tag dự kiến

infrastructure, ai

## Hạng mục cần làm ở bước tinh

- Verify link nguồn cho các mục [Bổ sung — nguồn].
- Quyết định tách thành mấy node wiki: có thể 1 node "Cài operator trên OpenShift air-gapped với oc-mirror" + 1 node "MIG trên NVIDIA GPU" (vì MIG là khái niệm độc lập, tái dùng được).
- Làm rõ hoặc gắn cờ vĩnh viễn vùng [Chưa chắc] về driver.
