---
tags:
  - ai
  - petrophysics
date: 2026-05-29
---
# HIMFA

HIMFA (Hierarchical Mixture of Facies Classifier) là kiến trúc phân loại facies hai tầng trong wipm-old, đối ứng cho bài toán classification của [HIMPE](./HIMPE.md) bên regression. Tên HIMFA là naming nội bộ trong code base mà không có paper trùng acronym; khuôn khổ lý thuyết gần nhất là **hierarchical classification** (Silla & Freitas, 2011) và cascade clustering-then-supervised (Silva et al., 2012).

# Hai tầng coarse-to-fine

Tầng 1 — **group classifier**: gom các facies tương đồng vào "group" do người dùng định nghĩa (ví dụ sand-dominant, shale-dominant, carbonate). Hàm `group_data` trong [clf_helper.py](../../references/repos/wipm-old/service/ml_toolkit/clf_helper.py:52) map nhãn facies gốc về chỉ số group, rồi `HIMFAClassifier.fit` train `groups_model` trên dữ liệu đã re-label theo group. Đây là bài toán classification dễ hơn vì số class ít và sự khác biệt giữa group lớn.

Tầng 2 — **facies classifier theo group**: với mỗi group, một classifier con được train chỉ trên các sample thuộc group đó (tham số `include=group` ở `__init__` của classifier con sẽ lọc dữ liệu). Khi predict, sample được routed qua group classifier trước, sau đó qua đúng facies classifier của group được predict.

Cấu trúc này cài đặt ở `HIMFAClassifier` trong [HIMFAClassifier.py](../../references/repos/wipm-old/service/ml_toolkit/HIMFAClassifier.py:27), với `groups_model` cho tầng 1 và `facies_models` (list) cho tầng 2.

# Plug-and-play backbone

HIMFA không cố định loại classifier. Dict `CLASSIFIER` ở đầu [HIMFAClassifier.py](../../references/repos/wipm-old/service/ml_toolkit/HIMFAClassifier.py:11) liệt kê các lựa chọn `NeuralNetClassifier`, `DecisionTreeClassifier`, `KNN`, `LogisticRegression`, `RandomForestClassifier`, `S_SOM`. User chỉ định backbone qua tham số `groups_model` (string) cho tầng 1, và `facies_models` (list of dict `{type, group}`) cho tầng 2. Nhờ vậy có thể chọn backbone mạnh khác nhau cho mỗi tầng và cho mỗi group, ví dụ dùng [S-SOM](./Supervised%20SOM.md) cho group facies có topology rõ và RandomForest cho group có biên ngang phức tạp.

# Hậu xử lý smoothen theo độ sâu

Predict ở mỗi tầng đều đi qua `smoothen` (cũng ở [clf_helper.py](../../references/repos/wipm-old/service/ml_toolkit/clf_helper.py:68)) với bán kính cửa sổ `radius`. Hàm này tính mode trong cửa sổ trượt để loại các điểm "nhảy đơn lẻ" — một facies có nhãn khác hẳn hàng xóm gần như luôn là noise vì facies thay đổi tự nhiên thành dải liền theo độ sâu. Smoothing áp dụng cả ở pred group lẫn pred facies cuối, nhân đôi hiệu ứng làm mượt.

Tham số `threshold` được forward xuống `groups_model.predict` để gán nhãn rỗng cho sample có confidence thấp — kết hợp với hàm `judge` ([clf_helper.py](../../references/repos/wipm-old/service/ml_toolkit/clf_helper.py:159)), HIMFA biết "từ chối" predict thay vì ép một nhãn không chắc chắn.

# Train/val split giữ thứ tự

`HIMFAClassifier.__init__` gọi `split_data` với `proportional=True, keep_order=True` để val set giữ tỉ lệ class gốc và thứ tự theo độ sâu. Điều này cần thiết khi đánh giá vì smoothen theo cửa sổ chỉ có nghĩa nếu mẫu liền kề trong val set vẫn liền kề theo độ sâu thật, không bị xáo trộn ngẫu nhiên.

# Vì sao hierarchical hợp với facies

Số facies trong một bồn trầm tích thường nhiều (10-20 facies), trong đó một số facies hiếm chỉ chiếm vài phần trăm dataset. Một classifier flat đối mặt class imbalance nặng và phải học decision boundary giữa mọi cặp facies. Tách thành group + facies-in-group làm hai bài toán nhỏ hơn: tầng 1 chỉ phân biệt vài group (mất cân bằng nhẹ hơn), tầng 2 chỉ phân biệt các facies "gần nhau" trong cùng group nên decision boundary đơn giản hơn nhiều. Đây cũng là tinh thần local-expert giống [HIMPE](./HIMPE.md), khác ở chỗ HIMPE dùng cluster tự động còn HIMFA dùng group do người dùng định nghĩa theo kiến thức địa chất.

# Nguồn tham khảo

- Silla Jr., C.N. & Freitas, A.A. (2011), "A survey of hierarchical classification across different application domains", *Data Mining and Knowledge Discovery*, 22(1-2): 31-72 — khung lý thuyết hierarchical classification
- Silva, A.A., Lima, R.S., Bom, C.R. et al. (2012), "Unsupervised and supervised learning in cascade for petroleum geology", *Expert Systems with Applications* — <https://www.sciencedirect.com/science/article/abs/pii/S0957417412003673>
- Vietnam Petroleum Institute (2024), "VPI-MLogs", arXiv:2410.05332 — <https://arxiv.org/abs/2410.05332>
- Source code tham khảo: [HIMFAClassifier.py](../../references/repos/wipm-old/service/ml_toolkit/HIMFAClassifier.py)

# Liên kết tri thức

- [HIMPE - phiên bản hierarchical cho regression permeability](./HIMPE.md)
- [Supervised SOM - backbone thường dùng cho facies classifier con](./Supervised%20SOM.md)
- [Learning Vector Quantization - nền tảng của S-SOM, được HIMFA dùng gián tiếp](./Learning%20Vector%20Quantization.md)
- [Cross Recurrence Plot và RQA - phương án thay thế cho phát hiện facies hiếm](./Cross%20Recurrence%20Plot%20v%C3%A0%20RQA.md)
- [Well log và phân tích tầng chứa - bài toán đích của HIMFA](./Well%20log%20v%C3%A0%20b%C3%A0i%20to%C3%A1n%20ph%C3%A2n%20t%C3%ADch%20t%E1%BA%A7ng%20ch%E1%BB%A9a.md)
