---
tags:
  - ai
  - petrophysics
date: 2026-05-29
---
# Supervised SOM

Supervised SOM (S-SOM) mở rộng [Self-Organizing Map](./Self-Organizing%20Map.md) để giải bài toán classification bằng cách kết hợp lợi thế topology preservation của SOM với label thật từ supervised data. Trong wipm-old, S-SOM được triển khai dưới dạng `AdaptiveLVQ` ở [lvq_network.py](../../references/repos/wipm-old/service/ml_toolkit/lvq_network.py:616) và được wrap thành `S_SOMClassifier` ở [S_SOMClassifier.py](../../references/repos/wipm-old/service/ml_toolkit/S_SOMClassifier.py).

# Hai phase huấn luyện

Pha 1 — **train competitive layer kiểu SOM** (unsupervised): chạy SOM update với gaussian/bubble neighborhood để các prototype phân bố theo topology của input. Bước này không dùng nhãn nên prototype tự tổ chức theo cấu trúc dữ liệu thật.

Pha 2 — **label hóa prototype và fine-tune kiểu LVQ**: gán nhãn class cho mỗi prototype bằng một trong các chiến lược dưới, rồi chạy bước cập nhật [LVQ](./Learning%20Vector%20Quantization.md) để tinh chỉnh prototype theo decision boundary.

Hai pha này gọi tương ứng là `train_competitive` và `train_batch` trong `AdaptiveLVQ.fit`. Đầu vào nhận hai cặp tham số riêng `(first_num_iteration, first_epoch_size)` và `(second_num_iteration, second_epoch_size)` để điều chỉnh độ dài mỗi pha.

# Ba chiến lược label neuron

`exponential_distance` — với mỗi prototype, tính khoảng cách tới mọi sample, lấy `k = 10` neighbor gần nhất, cộng dồn trọng số `exp(−d²)` theo class của neighbor; class có tổng lớn nhất thắng. Trọng số tắt nhanh theo khoảng cách nên neighbor xa hầu như không ảnh hưởng. Đây là mặc định mà `S_SOMClassifier.fit` chọn.

`inverse_distance` — tương tự nhưng dùng trọng số `1/d`, tắt chậm hơn nên neighbor xa vẫn có ảnh hưởng nhỏ.

`uniform` — đếm số lần mỗi prototype thắng cho mỗi class trên toàn bộ train set, lấy class chiếm đa số. Phương án đơn giản nhất, nhưng không phân biệt prototype thắng "sát" hay thắng "rộng rãi".

Cả ba chiến lược đều có cơ chế **cân bằng số neuron theo class** — khi nhiều class cùng thắng ở một prototype, chọn class hiện ít prototype nhất để gán, tránh class trội nuốt hết prototype.

# Confidence score khi predict

Ngoài nhãn, S-SOM trả thêm confidence dựa trên một trong hai tiêu chí (`crit` trong `AdaptiveLVQ.predict`):

`distance` — tính lại trọng số `exp(−d²)` của `k = n_subclass / 20` neighbor gần nhất; tỷ lệ tổng trọng số của class thắng trên tổng tất cả neighbor là confidence. Cách này phản ánh mức độ tập trung của các prototype cùng class quanh input.

`winner_neuron` — đọc trực tiếp `_neurons_confidence[win_idx, y]` đã ghi lại từ pha label hóa. Cách này nhanh hơn nhưng không xét lân cận khi predict.

Sau đó hàm `judge` ở [clf_helper.py](../../references/repos/wipm-old/service/ml_toolkit/clf_helper.py:159) gán nhãn rỗng cho các sample có confidence dưới threshold, để xử lý sample không chắc chắn thay vì ép predict.

# Preprocessing đặc trưng

`S_SOMClassifier` chuẩn hóa feature về `[-1, 1]` bằng `MinMaxScaler`, vì khoảng cách Euclidean nhạy với scale. Việc dùng range đối xứng quanh 0 (thay vì `[0, 1]`) cho phép khởi tạo PCA dễ trải đều prototype quanh tâm.

# Ứng dụng phân loại facies

Trong wipm-old, S-SOM được dùng làm backbone classifier cho facies giếng khoan (xem [Well log và phân tích tầng chứa](./Well%20log%20v%C3%A0%20b%C3%A0i%20to%C3%A1n%20ph%C3%A2n%20t%C3%ADch%20t%E1%BA%A7ng%20ch%E1%BB%A9a.md)). Tính topology preservation từ pha 1 khớp tự nhiên với cấu trúc tướng đá: các facies có log signature tương tự sẽ chiếm vùng prototype lân cận trên lưới, giúp class hiếm vẫn được biểu diễn thay vì bị nuốt như trong các classifier global. S-SOM cũng được [HIMFA](./HIMFA.md) chọn làm classifier con cho từng nhóm facies.

# Nguồn tham khảo

- Riese, F.M., Keller, S., Hinz, S. (2020), "Supervised and Semi-Supervised Self-Organizing Maps for Regression and Classification Focusing on Hyperspectral Data", *Remote Sensing*, 12(1): 7 — <https://www.mdpi.com/2072-4292/12/1/7>
- Riese, F.M. & Keller, S. (2019), "SuSi: Supervised Self-Organizing Maps for Regression and Classification in Python", arXiv:1903.11114 — <https://arxiv.org/abs/1903.11114>
- Mai-Cao, L. & Le, C. (2018), "A Self-Organizing Map, Machine Learning Approach to Lithofacies Classification", *IJSSST*, 19(03) — <https://edas.info/doi/10.5013/IJSSST.a.19.03.16>
- Source code tham khảo: [S_SOMClassifier.py](../../references/repos/wipm-old/service/ml_toolkit/S_SOMClassifier.py), [lvq_network.py](../../references/repos/wipm-old/service/ml_toolkit/lvq_network.py)

# Liên kết tri thức

- [Self-Organizing Map - nền tảng pha 1 unsupervised của S-SOM](./Self-Organizing%20Map.md)
- [Learning Vector Quantization - nền tảng pha 2 fine-tune của S-SOM](./Learning%20Vector%20Quantization.md)
- [HIMFA - dùng S-SOM làm classifier con cho từng nhóm facies](./HIMFA.md)
- [Well log và phân tích tầng chứa - bài toán đích của S-SOM trong wipm-old](./Well%20log%20v%C3%A0%20b%C3%A0i%20to%C3%A1n%20ph%C3%A2n%20t%C3%ADch%20t%E1%BA%A7ng%20ch%E1%BB%A9a.md)
