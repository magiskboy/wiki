---
tags:
  - ai
date: 2026-05-29
---
# Self-Organizing Map

Self-Organizing Map (SOM) do Teuvo Kohonen công bố năm 1982 là unsupervised neural network ánh xạ dữ liệu high-dimensional xuống một lưới neuron 2D (rectangular hoặc hexagonal), giữ tính chất **topology preservation**: các vector input gần nhau trong input space sẽ kích hoạt các neuron gần nhau trên lưới. Nhờ đặc tính này SOM được dùng cho visualization, clustering và là nền tảng cho [Supervised SOM](./Supervised%20SOM.md) trong các bài toán phân loại có cấu trúc không gian.

# Quy tắc cập nhật và neighborhood function

Mỗi neuron `i` có một weight vector `w_i` cùng số chiều với input. Với mỗi input `x`, tìm best matching unit (BMU) `c = argmin ||x − w_c||` rồi cập nhật trọng số mọi neuron theo `w_i(t+1) = w_i(t) + α(t) · h_{ci}(t) · (x − w_i)`. Tham số `α(t)` là learning rate giảm dần, và `h_{ci}(t)` là **neighborhood function** quyết định mức độ neuron `i` được "kéo theo" BMU `c`.

Hai dạng neighborhood phổ biến đã có sẵn trong [lvq_network.py](../../references/repos/wipm-old/service/ml_toolkit/lvq_network.py:458):

- **Gaussian** — `h_{ci} = exp(−||r_c − r_i||² / 2σ(t)²)`, mềm và tác động xa, phù hợp pha học sớm khi prototype còn xa tối ưu.
- **Bubble** — bằng 1 trong bán kính `σ(t)`, bằng 0 ngoài, dạng step function rẻ về tính toán, phù hợp pha fine-tune.

Bán kính `σ(t)` cũng giảm dần theo iteration (annealing), kết hợp với giảm dần learning rate để mạng hội tụ về cấu trúc topology ổn định.

# Khác biệt với clustering thông thường

Các thuật toán clustering như k-means tìm centroid tối ưu cục bộ độc lập, không có quan hệ vị trí giữa các centroid. SOM ép các neuron lân cận trên lưới cùng học giống nhau, kết quả là biểu diễn output có cấu trúc liên tục: hai vùng dữ liệu lân cận sinh ra hai vùng neuron lân cận. Đây là tính chất topology preservation, giúp SOM dùng được để visualize không gian high-dimensional thành bản đồ 2D đọc được.

# Khởi tạo trọng số

Hai chiến lược khởi tạo phổ biến cài trong [lvq_network.py](../../references/repos/wipm-old/service/ml_toolkit/lvq_network.py:514):

- **PCA initialization** — đặt prototype dọc theo hai principal component đầu tiên của data, giúp SOM hội tụ nhanh và ổn định hơn so với random.
- **Sample initialization** — chọn ngẫu nhiên các mẫu thật từ data làm prototype ban đầu, đảm bảo prototype luôn nằm trong vùng dữ liệu hợp lệ.

# Conscience để cân bằng số lần thắng

Giống [LVQ](./Learning%20Vector%20Quantization.md), SOM thường có bias function (conscience) ngăn vài neuron thắng quá nhiều và bỏ học các neuron còn lại. Cài đặt mặc định ở [ssom_util.py](../../references/repos/wipm-old/service/ml_toolkit/ssom_util.py:27) giảm bias mọi neuron 10% và tăng riêng bias neuron thắng để hạ "lợi thế" của nó ở vòng sau.

# Nguồn tham khảo

- Kohonen, T. (1982), "Self-organized formation of topologically correct feature maps", *Biological Cybernetics*, 43(1): 59-69 — DOI: 10.1007/BF00337288
- Kohonen, T. (2013), "Essentials of the self-organizing map", *Neural Networks*, 37: 52-65 — <https://www.sciencedirect.com/science/article/abs/pii/S0893608012002596>
- Cottrell, M. et al. (2018), "Self-Organizing Maps, theory and applications", HAL preprint — <https://hal.science/hal-01796059/document>
- Source code tham khảo: [lvq_network.py](../../references/repos/wipm-old/service/ml_toolkit/lvq_network.py)

# Liên kết tri thức

- [Learning Vector Quantization - SOM là tiền đề unsupervised của LVQ](./Learning%20Vector%20Quantization.md)
- [Supervised SOM - mở rộng SOM bằng nhãn lớp](./Supervised%20SOM.md)
- [Well log và phân tích tầng chứa - SOM dùng cụm hóa dữ liệu log giếng](./Well%20log%20v%C3%A0%20b%C3%A0i%20to%C3%A1n%20ph%C3%A2n%20t%C3%ADch%20t%E1%BA%A7ng%20ch%E1%BB%A9a.md)
