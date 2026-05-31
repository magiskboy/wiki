---
tags:
  - ai
  - petrophysics
date: 2026-05-29
---
# Well log và bài toán phân tích tầng chứa

Well log (log giếng khoan) là chuỗi đo dọc theo độ sâu giếng các thuộc tính vật lý của đá và chất lưu, dùng để mô tả tầng chứa dầu khí mà không cần lấy mẫu lõi toàn bộ. Mỗi mét độ sâu sinh ra một vector đặc trưng nhiều chiều, vì vậy log giếng tự nhiên là time series theo trục độ sâu và phù hợp với mô hình machine learning đầu vào nhiều biến.

# Các log đầu vào phổ biến

Pipeline trong [wipm-old](../../references/repos/wipm-old/service/ml_toolkit) dùng 6 log làm feature và một biến mục tiêu PERM_CORE:

- **GR** — Gamma Ray, đo phóng xạ tự nhiên của đá, phân biệt sét và cát kết.
- **NPHI** — Neutron porosity, phản ánh hàm lượng hydrogen, ước lượng porosity tổng.
- **RHOB** — Bulk density, mật độ khối, kết hợp NPHI để tính porosity và nhận diện chất lưu.
- **DT** — Sonic transit time, thời gian truyền sóng âm, liên quan porosity và đặc tính cơ học.
- **VCL** — Volume of clay, hàm lượng sét tính từ GR hoặc tổ hợp log.
- **PHIE** — Effective porosity, porosity hiệu dụng đã hiệu chỉnh sét.
- **PERM_CORE** — permeability đo trực tiếp trên mẫu lõi, đóng vai trò ground truth khi train mô hình permeability.

Tài liệu mở của Schlumberger và Halliburton mô tả định nghĩa và đơn vị chi tiết cho từng log.

# Hai bài toán cốt lõi

Phân loại **facies** (tướng đá): mỗi mét độ sâu được gán nhãn rời rạc là một facies (ví dụ sand, shale, carbonate, các sub-class theo môi trường trầm tích). Đây là supervised classification, ground truth lấy từ mô tả mẫu lõi do nhà địa chất gán nhãn. Vì số facies có thể lớn và phân bố mất cân bằng, người ta thường tổ chức theo hierarchy (xem [Hierarchical Mixture of Facies Classifier](./HIMFA.md)).

Dự đoán **permeability**: ước lượng độ thấm (đơn vị mD) từ log, vì đo permeability trên lõi tốn kém và chỉ có rải rác. Bài toán là regression với quan hệ phi tuyến mạnh và phụ thuộc rock type, nên hay được giải bằng cách chia-để-trị qua mixture-of-experts (xem [HIMPE](./HIMPE.md)).

# Đặc tính dữ liệu ảnh hưởng tới chọn model

Tính chuỗi theo độ sâu khiến các mẫu liền kề có nhãn tương quan cao, vì thế các hậu xử lý kiểu smoothing theo cửa sổ (như `smoothen` trong [clf_helper.py](../../references/repos/wipm-old/service/ml_toolkit/clf_helper.py)) cải thiện được độ chính xác. Cùng lý do, các phương pháp dựa trên reconstruct phase space của time series như [Cross Recurrence Plot và RQA](./Cross%20Recurrence%20Plot%20v%C3%A0%20RQA.md) cũng được dùng để phát hiện facies hiếm.

Phân bố facies thường mất cân bằng và overlap mạnh ở biên, nên các mô hình có khái niệm prototype và topology như [Self-Organizing Map](./Self-Organizing%20Map.md), [Learning Vector Quantization](./Learning%20Vector%20Quantization.md), [Supervised SOM](./Supervised%20SOM.md) được dùng phổ biến.

Permeability có quan hệ phụ thuộc rock type — cùng porosity có thể cho permeability khác nhau ở các loại đá khác nhau — nên các mô hình lai cluster + regression cục bộ như [ANFIS](./ANFIS.md) hoặc [HIMPE](./HIMPE.md) thường vượt trội so với một regressor đơn.

# Nguồn tham khảo

- Schlumberger Oilfield Glossary: <https://glossary.slb.com/>
- Vietnam Petroleum Institute (2024), "VPI-MLogs: A web-based machine learning solution for applications in petrophysics", arXiv:2410.05332 — <https://arxiv.org/abs/2410.05332>
- Tabesh & Mirjalili (2006), "Permeability prediction by fuzzy logic and Kangan reservoir" — <https://academic.oup.com/jge/article/3/4/356/5127665>

# Liên kết tri thức

- [Learning Vector Quantization](./Learning%20Vector%20Quantization.md) — backbone classifier cho prototype-based facies
- [Self-Organizing Map](./Self-Organizing%20Map.md) — clustering bảo toàn topology cho log giếng
- [Supervised SOM](./Supervised%20SOM.md) — biến thể có giám sát cho facies classification
- [ANFIS](./ANFIS.md) — neuro-fuzzy regression dùng cho permeability
- [Cross Recurrence Plot và RQA](./Cross%20Recurrence%20Plot%20v%C3%A0%20RQA.md) — phát hiện facies bằng phân tích time series phi tuyến
- [HIMPE](./HIMPE.md) — mixture-of-experts cho permeability
- [HIMFA](./HIMFA.md) — hierarchical classification cho facies
- [Dữ liệu là tài sản cốt lõi](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/D%E1%BB%AF%20li%E1%BB%87u%20l%C3%A0%20t%C3%A0i%20s%E1%BA%A3n%20c%E1%BB%91t%20l%C3%B5i.md) — ground truth từ core data quyết định chất lượng model
