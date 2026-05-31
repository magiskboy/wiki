---
tags:
  - ai
date: 2026-05-29
---
# Learning Vector Quantization

Learning Vector Quantization (LVQ) là supervised classification algorithm do Teuvo Kohonen đề xuất, học một tập **prototype vector** (còn gọi là codebook vector) trong feature space, sao cho lớp của một input mới được quyết định bởi prototype gần nhất theo Euclidean distance. LVQ là phiên bản có giám sát của vector quantization và quan hệ gần với [Self-Organizing Map](./Self-Organizing%20Map.md) ở chỗ cùng dùng competitive layer winner-takes-all, nhưng khác ở mục tiêu: SOM bảo toàn topology của input space, còn LVQ học decision boundary giữa các class.

# Kiến trúc hai tầng

LVQ gồm hai layer. **Competitive layer** chứa các prototype `w_i`, mỗi prototype có cùng số chiều với input; tìm prototype thắng (best matching unit, BMU) bằng cách chọn `i* = argmin ||x − w_i||`. **Linear layer** ánh xạ chỉ số prototype thắng sang nhãn class qua một ma trận trọng số thưa, mỗi prototype được gán cố định cho đúng một class — phép `classify` chỉ là argmax của tích `linear_layer_weights · win`. Mỗi class có thể có nhiều prototype, cho phép biểu diễn class phi lồi.

Trong [lvq_network.py](../../references/repos/wipm-old/service/ml_toolkit/lvq_network.py) của wipm-old, lớp `LvqNetwork` cài đặt đúng cấu trúc này: `_competitive_layer_weights` là ma trận `(n_subclass, n_feature)`, `_linear_layer_weights` là ma trận `(n_class, n_subclass)` được khởi tạo chia đều prototype cho mỗi class trước khi huấn luyện.

# Quy tắc cập nhật LVQ1, LVQ2, LVQ3

LVQ1 là quy tắc cơ bản: nếu BMU cùng class với mẫu thì kéo prototype lại gần `w ← w + α(x − w)`, nếu khác class thì đẩy ra `w ← w − α(x − w)`. Quy tắc này gây bất ổn ở biên decision boundary vì prototype có thể bị đẩy ra ngoài vùng dữ liệu.

LVQ2 cập nhật đồng thời hai prototype gần nhất khi mẫu rơi vào "window" gần biên: một prototype đúng class được kéo lại, một prototype sai class bị đẩy ra. Quy tắc này tinh chỉnh decision boundary chính xác hơn nhưng dễ phân kỳ nếu áp dụng quá dài.

LVQ3 thêm hạng tử ổn định (stabilizing term `ε`) khi cả hai prototype gần nhất cùng đúng class, để giữ ổn định trong quá trình tinh chỉnh dài.

Triển khai trong wipm-old là biến thể LVQ1 bất đối xứng — bước cập nhật khi sai class dùng learning rate nhỏ hơn `β = α/3` để giảm chấn (`update` trong [lvq_network.py](../../references/repos/wipm-old/service/ml_toolkit/lvq_network.py:158)).

# Conscience và learning rate decay

LVQ thường có cơ chế "conscience" (bias) để tránh hiện tượng một số prototype thắng quá nhiều, làm các prototype còn lại không học được. Quy tắc mặc định trong [ssom_util.py](../../references/repos/wipm-old/service/ml_toolkit/ssom_util.py:27) là giảm bias mọi prototype theo hệ số 0.9 và tăng bias prototype thắng để hạ "lợi thế" của nó ở vòng tiếp theo. Đây là khái niệm conscience của DeSieno (1988), được Kohonen tích hợp vào LVQ-PAK.

Learning rate giảm dần theo iteration để hội tụ ổn định, dạng phổ biến là `α(t) = α_0 / (1 + decay · t)`, được dùng làm mặc định trong code.

# Mở rộng theo neighborhood và adaptive

Biến thể `LvqNetworkWithNeighborhood` xếp prototype trên lưới 2D `n_rows × n_cols` và áp dụng hàm neighborhood (gaussian hoặc bubble) khi cập nhật, tương tự [Self-Organizing Map](./Self-Organizing%20Map.md) nhưng có thông tin class. Phiên bản `AdaptiveLVQ` triển khai một pipeline hai pha: pha 1 train competitive layer không giám sát (như SOM), pha 2 gán nhãn class cho mỗi prototype bằng `label_neurons` rồi fine-tune theo quy tắc LVQ — đây chính là kiến trúc [Supervised SOM](./Supervised%20SOM.md).

# Nguồn tham khảo

- Kohonen, T. (1990), "The Self-Organizing Map", *Proceedings of the IEEE*, 78(9): 1464-1480 — DOI: 10.1109/5.58325
- Kohonen, T. et al. (1996), "LVQ-PAK: The Learning Vector Quantization Program Package", Helsinki University of Technology Report A30 — <https://www.researchgate.net/publication/220048682>
- Nova, D. & Estévez, P.A. (2014), "A review of learning vector quantization classifiers", *Neural Computing and Applications* — <https://www.researchgate.net/publication/259486415>
- Source code tham khảo: [lvq_network.py](../../references/repos/wipm-old/service/ml_toolkit/lvq_network.py)

# Liên kết tri thức

- [Self-Organizing Map - LVQ là biến thể có giám sát](./Self-Organizing%20Map.md)
- [Supervised SOM - hiện thực hóa qua AdaptiveLVQ trong wipm-old](./Supervised%20SOM.md)
- [Well log và phân tích tầng chứa - LVQ làm backbone cho facies classifier](./Well%20log%20v%C3%A0%20b%C3%A0i%20to%C3%A1n%20ph%C3%A2n%20t%C3%ADch%20t%E1%BA%A7ng%20ch%E1%BB%A9a.md)
- [HIMFA - dùng S_SOM (kế thừa từ LVQ) làm classifier con](./HIMFA.md)
