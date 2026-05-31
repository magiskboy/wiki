---
tags:
  - ai
  - petrophysics
date: 2026-05-29
---
# HIMPE

HIMPE (Hierarchical Mixture of Permeability Estimators) là một pipeline hierarchical kiểu mixture-of-experts dùng để dự đoán permeability (PERM_CORE) từ well log trong wipm-old. Tên HIMPE xuất hiện như naming nội bộ trong code base mà không có paper public peer-review trùng acronym; ý tưởng cốt lõi của HIMPE là chia-để-trị bằng cách gom mẫu thành cụm rồi để mỗi cụm có một regressor chuyên biệt, đây chính là pattern **mixture-of-experts** (Jacobs et al., 1991).

# Quy trình ba bước

Bước 1 — **clustering**: hàm `clustering` trong [himpe.py](../../references/repos/wipm-old/service/ml_toolkit/himpe.py:43) chạy fuzzy c-means (`Probabilistic` từ `skcmeans`) trên `n_clusters` cụm. Có hai chế độ:

- `by='data'` — cụm hóa trên feature space `(GR, NPHI, RHOB, DT, VCL, PHIE)` để mỗi cụm tương ứng một rock type với log signature riêng.
- `by='target'` — cụm hóa trên `PERM_CORE` để chia trục permeability thành các dải giá trị.

Nhãn cluster `argmin distances` được append vào DataFrame thành cột `LABEL`.

Bước 2 — **gating network**: hàm `gen_classifier` train một pipeline `StandardScaler + XGBClassifier(n_estimators=300, max_depth=30)` để học mapping từ feature sang `LABEL`. Khi predict permeability cho sample mới, gating network quyết định sample thuộc cluster nào.

Bước 3 — **local experts**: hàm `gen_estimators` tạo một danh sách `MLPRegressor` (hidden `(10, 20, 30, 10)`, `adam`, `max_iter=1000`) và `MinMaxScaler` riêng cho mỗi cluster, train chỉ trên data thuộc cluster đó. Mỗi MLP học một sub-manifold permeability đồng nhất hơn so với một MLP global học mọi rock type cùng lúc.

Hàm `predict` trong [himpe.py](../../references/repos/wipm-old/service/ml_toolkit/himpe.py:187) nối ba bước: gating XGBoost chọn cluster, sample được forward qua đúng `MLPRegressor` của cluster đó, trả về scalar permeability.

# Vì sao kiến trúc này hợp với permeability

Permeability có quan hệ phi tuyến rất mạnh với log và phụ thuộc rock type — cùng porosity có thể cho permeability khác nhau ở sandstone, carbonate, tight rock. Một regressor đơn phải học một mặt phẳng phức tạp ôm mọi rock type, dễ bị bias về rock type phổ biến và bỏ tail giá trị. Tách dataset theo cụm rock type rồi train local expert giảm độ phức tạp của hàm mỗi expert phải học, đồng thời cho phép expert đặc trị cho rock type ít phổ biến.

Chế độ `by='target'` tạo cụm theo dải permeability cũng có lý do: phân phối permeability thường lệch (log-normal hoặc heavy tail), nên chia dải permeability giúp expert ở vùng tail có model riêng thay vì bị nuốt bởi vùng peak.

# Liên hệ với khuôn khổ lý thuyết

HIMPE cụ thể hóa kiến trúc **adaptive mixture of local experts** của Jacobs et al. (1991): gating network chia input space, mỗi expert chuyên về một region. Khác biệt là HIMPE huấn luyện gating và expert tách rời (cluster trước, expert sau) thay vì end-to-end với softmax gating như nguyên gốc — đây là dạng "hard gating" đơn giản hóa, dễ train, ít rủi ro mode collapse.

Pattern cluster + local expert cũng xuất hiện trong [ANFIS](./ANFIS.md) của wipm-old, nơi fuzzy c-means partition dữ liệu rồi MLPRegressor học toàn cục với chỉ số cluster làm thêm feature; HIMPE đi xa hơn ở chỗ mỗi cluster có MLP riêng hoàn toàn.

# Nguồn tham khảo

- Jacobs, R.A., Jordan, M.I., Nowlan, S.J., Hinton, G.E. (1991), "Adaptive Mixtures of Local Experts", *Neural Computation*, 3(1): 79-87 — paper gốc mixture-of-experts
- Tabesh, M. & Mirjalili, A. (2006), "Permeability prediction by fuzzy logic and Kangan reservoir", *Journal of Geophysics and Engineering* — <https://academic.oup.com/jge/article/3/4/356/5127665>
- Vietnam Petroleum Institute (2024), "VPI-MLogs: A web-based machine learning solution for applications in petrophysics", arXiv:2410.05332 — context các pipeline ML cho well log của VN — <https://arxiv.org/abs/2410.05332>
- Source code tham khảo: [himpe.py](../../references/repos/wipm-old/service/ml_toolkit/himpe.py)

# Liên kết tri thức

- [ANFIS - cùng pattern cluster + local regressor, mức độ chia sẻ tham số khác](./ANFIS.md)
- [HIMFA - phiên bản hierarchical cho bài toán classification](./HIMFA.md)
- [Well log và phân tích tầng chứa - bài toán đích của HIMPE](./Well%20log%20v%C3%A0%20b%C3%A0i%20to%C3%A1n%20ph%C3%A2n%20t%C3%ADch%20t%E1%BA%A7ng%20ch%E1%BB%A9a.md)
