---
tags:
  - ai
  - petrophysics
date: 2026-05-29
---
# Cross Recurrence Plot và RQA

Recurrence Plot (RP) là kỹ thuật phân tích nonlinear dynamics của time series bằng cách reconstruct không gian pha và đánh dấu các cặp thời điểm có trạng thái "gần nhau". Cross Recurrence Plot (CRP) mở rộng cho hai time series khác nhau — đo simultaneous occurrence của similar states. Recurrence Quantification Analysis (RQA) trích xuất các đặc trưng định lượng từ ma trận đó để dùng cho classification và detection. Trong wipm-old, CRP được dùng để phát hiện một facies cụ thể trong chuỗi log giếng theo độ sâu.

# Time-delay embedding để reconstruct phase space

Một time series một biến `{x_i}` được biến thành chuỗi vector trong không gian pha qua **time-delay embedding** (Takens 1981) với hai tham số: **embedding dimension** `m` (`dim` trong code) và **delay** `τ` (`tau`). Mỗi vector pha là `\vec{x}_i = (x_i, x_{i+τ}, x_{i+2τ}, \ldots, x_{i+(m-1)τ})`. Hàm `create_table_index` trong [crp.py](../../references/repos/wipm-old/service/ml_toolkit/crp.py:12) tạo bảng chỉ số `num_vectors = m − (dim−1)·tau` tuyến tính, sau đó `get_vector_each_vector_timeseries` reshape time series gốc theo bảng chỉ số đó cho mỗi feature.

Chọn `m` và `τ` đủ lớn sẽ giữ được geometry của attractor; chọn quá nhỏ sẽ làm sập các cấu trúc khác nhau vào cùng vùng pha.

# Recurrence và threshold epsilon

Recurrence Plot là ma trận nhị phân `R_{ij} = Θ(ε − ||\vec{x}_i − \vec{x}_j||)` với `Θ` là hàm Heaviside. Hai trạng thái được coi là **recurrent** khi khoảng cách giữa chúng dưới ngưỡng `ε`. Trong wipm-old, `cdist(vectors_train, vectors_test, 'minkowski', p=1)` dùng Manhattan distance — chọn `p=1` thường ổn định hơn Euclidean với chuỗi nhiễu.

Cross Recurrence Plot khác RP ở chỗ hai trục là hai chuỗi khác nhau (`vectors_train` vs `vectors_test`), nên ma trận không nhất thiết đối xứng và cũng không có diagonal "tự recurrence" cố định.

# Recurrence Quantification Analysis

RQA biến CRP/RP từ một hình ảnh thành các scalar measure cho classification:

- **%REC** (recurrence rate) — tỉ lệ điểm recurrent trên toàn ma trận, đo mật độ tái phát chung.
- **%DET** (determinism) — tỉ lệ điểm nằm trên diagonal lines, đo mức độ chuỗi có deterministic dynamics.
- **%LAM** (laminarity) — tỉ lệ trên vertical lines, đo mức "đóng băng" trạng thái.

Code wipm-old dùng dạng RQA tối giản: với mỗi cột (mỗi vector test) đếm số dòng có recurrence `r = sum(r_dist < ε, axis=0)`, rồi threshold `lambda` để quyết định vector test đó có thuộc class đang xét không. Đây là binary classifier per-class: mỗi facies có một file train riêng và một `ε, λ` riêng được tune (thấy ở mảng `epsilon = [..., 0.035, 0.1, 0.02, ...]` ứng với từng `curve_number`).

# Tham số percent để mở rộng nhãn

Sau khi xác định các vị trí `index` có `r > λ` (phát hiện match), code mở rộng nhãn ra `int(dim * percent)` mẫu liên tiếp xung quanh — vì mỗi vector pha tham chiếu một cửa sổ `dim` mẫu của time series gốc, nên một phát hiện đại diện cho cả cửa sổ đó là facies dương. Đây là cách hậu xử lý hợp với bản chất time-delay embedding chứ không phải predict điểm độc lập.

# Nguồn tham khảo

- Marwan, N., Romano, M.C., Thiel, M., Kurths, J. (2007), "Recurrence plots for the analysis of complex systems", *Physics Reports*, 438(5-6): 237-329 — DOI: 10.1016/j.physrep.2006.11.001 — PDF: <http://www.recurrence-plot.tk/marwan_PhysRep2007.pdf>
- Marwan, N. & Kurths, J. (2002), "Nonlinear analysis of bivariate data with cross recurrence plots", *Physics Letters A*, 302(5-6): 299-307 — arXiv: <https://arxiv.org/abs/physics/0201061>
- Trang tổng hợp của Marwan: <http://www.recurrence-plot.tk/>
- Wallot, S. & Leonardi, G. (2018), "Analyzing multivariate dynamics using cross-recurrence quantification analysis", tutorial — <https://pmc.ncbi.nlm.nih.gov/articles/PMC6288366/>
- Source code tham khảo: [crp.py](../../references/repos/wipm-old/service/ml_toolkit/crp.py)

# Liên kết tri thức

- [Well log và phân tích tầng chứa - CRP phát hiện facies hiếm trong chuỗi log](./Well%20log%20v%C3%A0%20b%C3%A0i%20to%C3%A1n%20ph%C3%A2n%20t%C3%ADch%20t%E1%BA%A7ng%20ch%E1%BB%A9a.md)
- [HIMFA - phương án thay thế phân loại facies dùng classifier mixture](./HIMFA.md)
