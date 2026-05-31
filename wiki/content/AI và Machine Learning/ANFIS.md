---
tags:
  - ai
  - petrophysics
date: 2026-05-29
---
# ANFIS

ANFIS (Adaptive-Network-Based Fuzzy Inference System) là kiến trúc neuro-fuzzy do J.-S. Roger Jang công bố năm 1993, biểu diễn một **Sugeno (TSK) fuzzy model** dưới dạng adaptive network 5 layer feedforward để có thể huấn luyện được bằng các kỹ thuật giống neural network. Ý tưởng nền là giữ tính diễn giải của fuzzy rule trong khi vẫn học được tham số tự động từ dữ liệu.

# Kiến trúc 5 layer

**Layer 1 — Fuzzification**: mỗi node là một membership function (thường Gaussian hoặc bell-shaped) ánh xạ giá trị đầu vào thành mức độ thuộc về fuzzy set. Tham số của các membership function được gọi là **premise parameters**.

**Layer 2 — Rule firing**: với mỗi rule, tính firing strength `w_i = ∏ μ(x_j)` qua T-norm (thường là tích). Mỗi node ở layer này tương ứng một fuzzy rule.

**Layer 3 — Normalization**: chuẩn hóa firing strength `w̄_i = w_i / Σ_j w_j` để tổng bằng 1.

**Layer 4 — Defuzzification**: tính `w̄_i · f_i` với `f_i = p_i x + q_i y + r_i` (linear consequent kiểu Sugeno bậc 1). Các tham số `p, q, r` gọi là **consequent parameters**.

**Layer 5 — Output**: cộng tổng `Σ w̄_i f_i` ra kết quả cuối.

# Hybrid learning

Điểm tinh tế của ANFIS là tách quá trình huấn luyện thành hai pha. **Forward pass**: cố định premise parameters, truyền tín hiệu tới layer 4 rồi giải **Least Squares Estimation** cho consequent parameters — đây là bài toán tuyến tính theo `p, q, r` nên có nghiệm đóng. **Backward pass**: cố định consequent parameters, dùng **gradient descent (backpropagation)** truyền sai số ngược về cập nhật premise parameters.

Hybrid learning hội tụ nhanh hơn pure gradient descent rất nhiều vì giải tuyến tính một nửa số tham số mà không cần lặp.

# Triển khai trong wipm-old

Lớp `Anfis` ở [anfis.py](../../references/repos/wipm-old/service/ml_toolkit/anfis.py:13) không cài đặt 5 layer kinh điển mà dùng một biến thể lai pragmatic cho permeability:

- Một `DecisionTreeRegressor` (max_depth=6) học `y_pseudo` từ `X` để tạo target trung gian.
- Hai `Probabilistic` fuzzy c-means clusterer phân cụm cả `X` (`n_clusters=4`) và `y` (`n_clusters=6`), gán mỗi sample vào cluster gần nhất qua `argmin distances`. Hai chỉ số cluster `_f1, _f2` đóng vai trò **fuzzy membership feature** rời rạc, thay cho membership function của ANFIS gốc.
- Concat `[X, _f1, _f2]`, MinMax scale, rồi đưa vào một `MLPRegressor` để học mapping cuối ra `y`.

Khi predict, decision tree sinh `y_pseudo`, dùng `y_pseudo` để chọn cluster `_f2` (vì `y` thật chưa biết), rồi MLP cho output. Phiên bản này gần với **mixture-of-experts** hơn là ANFIS Jang chuẩn, nhưng giữ tinh thần dùng cluster làm fuzzy partition và regression tuyến tính/phi tuyến trong từng partition. Ý tưởng cluster vừa theo input vừa theo output là điểm chung với [HIMPE](./HIMPE.md).

# Khi nào ANFIS phù hợp

ANFIS hay được dùng cho regression có domain knowledge về quan hệ phi tuyến giữa input-output (như permeability từ well log, điều khiển fuzzy), nhờ vừa cho prediction tốt vừa cho ra rule diễn giải được. Hạn chế chính là số rule bùng nổ theo số input (curse of dimensionality của fuzzy partition) — Jang đề xuất dùng subtractive clustering hoặc fuzzy c-means để giảm số rule, đúng tinh thần mà bản wipm-old đã cài.

# Nguồn tham khảo

- Jang, J.-S.R. (1993), "ANFIS: Adaptive-Network-Based Fuzzy Inference System", *IEEE Transactions on Systems, Man, and Cybernetics*, 23(3): 665-685 — DOI: 10.1109/21.256541 — <https://ieeexplore.ieee.org/document/256541/>
- Bản trên ResearchGate (full PDF): <https://www.researchgate.net/publication/3113825>
- Source code tham khảo: [anfis.py](../../references/repos/wipm-old/service/ml_toolkit/anfis.py)

# Liên kết tri thức

- [HIMPE - cùng pattern cluster + local regressor cho permeability](./HIMPE.md)
- [Well log và phân tích tầng chứa - ANFIS dự đoán PERM_CORE](./Well%20log%20v%C3%A0%20b%C3%A0i%20to%C3%A1n%20ph%C3%A2n%20t%C3%ADch%20t%E1%BA%A7ng%20ch%E1%BB%A9a.md)
