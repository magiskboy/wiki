---
title: "Quá trình inference cho Large Language Model"
date: "2025-07-13T14:30:00+07:00"
tags:
- llm
- ai
categories:
- LLM
- AI
description: "Trong bài viết này, mình chia sẻ cách một LLM được thực thi (inference) trên các inference server, từ đó giúp chúng ta hiểu rõ hơn về nguyên lý hoạt động của LLM, ý nghĩa của các tham số khi gọi model và cách các inference server tối ưu quá trình inference."
---


Để dễ dàng theo dõi bài viết này, bạn nên có:
- Kiến thức cơ bản về đại số tuyến tính và các phép biến đổi ma trận, vector như nhân vô hướng/có hướng, chuyển vị,…
- Hiểu biết nền tảng về machine learning và deep learning, chẳng hạn như perceptron, cách mô hình hoạt động và sinh ra giá trị dự đoán,…
- Trải nghiệm sử dụng LLM (Large Language Model).

OK, giờ thì hãy bắt đầu.


Một trong những bài toán cơ bản của LLM là hoàn thiện phần còn lại của 1 câu văn. Ví dụ: "Tôi đi học..." thì output của LLM có thể là "Tôi đi học 5 ngày trong tuần".


## I. Hiểu về quá trình inference

### 1. Transformer

Ở bước này, chúng ta sẽ tính toán mối quan hệ giữa các từ trong prompt, xác định từ nào có liên hệ với từ nào và mức độ liên hệ đó ra sao.
Để thực hiện điều này, chúng ta forward đầu vào $X_0$ - ma trận embedding của các token trong prompt qua các __Transformer block__.


<figure>
<img src="/images/llm-1.png">
</figure>

 
Như trong hình, mỗi Transformer block gồm hai thành phần chính:
- Attention: tính toán mối quan hệ giữa các từ trong prompt.
- Feed Forward Neural Network (MLP – Multi-Layer Perceptron): thực hiện các biến đổi phi tuyến tính để trích xuất và biểu diễn đặc trưng ở mức cao hơn.

__Tính Attention__

Tính $Q, K, V$ của n tokens trong prompt

$$
Q_i = X_0 \ . \ W_{q_i} \ (1) \\
K_i = X_0 \ . \ W_{k_i} \ (2) \\
V_i = X_0 \ . \ W_{v_i} \ (3) \\
$$

trong đó

$$
W_{q_i}, \ W_{k_i}, \ W_{v_i} \in \mathbb{R}^{d_{model}, \ d_{head}} \ \text{với} \ i = 1...n_{head}, \\
X_0 \in \mathbb{R}^{n, \ d_{model}} \\
\Rightarrow \ Q_i, K_i, V_i \in \mathbb{R}^{n, \: d_{head}} \ \text{với} \ i = 1...n_{head}
$$

Lưu ý: trong các kiến trúc khác, kích thước của các ma trận $W_q, W_k, W_v$ có thể là khác nhau.

Tính Attention (A)

$$
\text{Attention}(Q_i, K_i, V_i) = \text{softmax}\!\left( \frac{Q_i \ . \ K_i^{T}}{\sqrt{d_{head}}} \right) \ . \ V_i \ (4)
$$

trong đó

$$
Q_i, \ K_i, \ V_i \in \mathbb{R}^{n, \ d_{head}} \ \text{với} \ i = 1...n_{head} \\
\Rightarrow \text{Attention}(Q_i, K_i, V_i) \in \mathbb{R}^{n, \ d_{head}} \text{với} \ i = 1...n_{head}
$$


Nối head

$$
O = \mathrm{reshape}(A, (n, d_{head} . n_{head})) \\
\Rightarrow A \in \mathbb{R}^{n, \ d_{model}}
$$


Residual Connection

$$
R = X_0 + O \ \text{trong đó} \ X_0, \ O \in \mathbb{R}^{n, d_{model}} \ (5)
$$

Chuẩn hoá dữ liệu

$$
\mathrm{LN}(R_i) = \frac{R_i - \mu_i}{\sqrt{\sigma_i^2 + \epsilon}} \ \text{với} \ i = 1 .. n \ (6)
$$

Trong đó

- $R_i$ là hàng thứ $i$ của ma trận $R \in \mathbb{R}^{n, \: d_{model}}$ — vector ẩn của $token_i \in R^{d_{model}}$
- $\mu_i = \frac{1}{d_{\text{model}}} \sum_j R_{i,j}$
- $\sigma_i^2 = \frac{1}{d_{\text{model}}} \sum_j (R_{i,j} - \mu_i)^2$
- $\gamma, \beta \in \mathbb{R}^{d_{\text{model}}}$ là hai vector trainable parameters (scale và shift)

> 💡 *Nhận xét cá nhân:* Các bước trên có thể được xem như quá trình LLM tự động trích xuất đặc trưng về mối quan hệ giữa các token trong prompt. Cách làm này khá tương đồng với các kỹ thuật Feature Extraction (tự động) như PCA, SIFT, HOG,… hoặc Feature Engineering (thủ công) như thống kê, tính xác suất, v.v.

__Feed Forward Network__

$$
F_1 = R \ . \ W_1 \ + \ b_1 \ \text{trong đó} \ R \in \mathbb{R}^{n, \; d_{model}} W_1 \in \mathbb{R}^{d_{model}, \; d_{ff}}, \ b_1 \in \mathbb{R}^{d_{ff}} \ (7) \\
F_2 = F_1 \ . \ W_2 \ + \ b_2 \ \text{trong đó} \ F_1 \in \mathbb{R}^{n, \; d_{ff}} W_2 \in \mathbb{R}^{d_{ff}, \; d_{model}}, \ b_2 \in \mathbb{R}^{d_{model}} \ (8) \\
F_3 = \mathrm{GELU}(F_2) \text{trong đó} \ F_2 \in \mathbb{R}^{n, \: d_{model}} \ (9)
$$

> 💡 *Nhận xét cá nhân:* Ở bước FFN, LLM thực hiện biến đổi phi tuyến tính trên dữ liệu đầu vào (kết quả attention giữa các token).
> Quá trình này tương tự như:
> - Các lớp ẩn (hidden layer) trong mạng neural, nơi dữ liệu được biến đổi phi tuyến để học biểu diễn trừu tượng hơn.
> - Các phép biến đổi phi tuyến (kernel trick) trong một số thuật toán machine learning, chẳng hạn như [Support Vector Machine](https://www.youtube.com/watch?v=3liCbRZPrZA).


Layer Norm

$$
X_1 = \mathrm{LN}(F_3 + R) \ \text{trong đó} \ F3, R \in \mathbb{R}^{n, \; d_{model}} \ (10)
$$

Sau khi đi qua một Transformer block, ta thu được đầu ra $X_1$.

Tuy nhiên, trong thực tế, một LLM thường bao gồm từ 12 đến 120 Transformer block, và quá trình tính toán được thực hiện tuần tự như sau:

$$
X_1 = \mathrm{TRANFORMER}(X_0) \\
X_2 = \mathrm{TRANFORMER}(X_1) \\
... \\
X_m = \mathrm{TRANFORMER}(X_{m-1})
$$


### 2. Sinh từ 

Giả sử LLM được huấn luyện trên một bộ từ vựng gồm $n_{vocab}$ từ.

Khi đó, ta có một ma trận biểu diễn không gian embedding của toàn bộ từ vựng, được định nghĩa như sau:

$$
W_{vocab} \in \mathbb{R}^{d_{vocab}, \: d_{model}} \\
b_{vocab} \in \mathbb{R}^{n_{vocab}}
$$

Ta chiếu vector đặc trưng của token cuối cùng trong prompt lên không gian từ vựng để tính giá trị logits, tức là mức độ phù hợp của token đó với từng từ trong bộ từ vựng.

$$
logits = X_m[-1] \ . \ W_{vocab}^{T} \ + \ b_{vocab} \ (11) \\
\Rightarrow logits \in \mathbb{R}^{n_{vocab}}
$$


Sau đó, ta tính phân phối xác suất trên toàn bộ từ vựng bằng cách chuẩn hóa các giá trị logits (thường thông qua hàm softmax) để xác định xác suất xuất hiện của từng từ.

$$
p_i = \frac{\mathrm{exp}(\frac{\text{logits}_i}{T})}{\sum_{j=1}^{n_{vocab}} \mathrm{exp}(\frac{\text{logits}_j}{T})} \ (12) \\
$$

hay

$$
p = \mathrm{softmax}(logits)
$$

Do đó, tổng xác suất của tất cả các từ trong bộ từ vựng sẽ là $\sum_{i=1}^{n_{vocab}}p_i = 1$

Bước tiếp theo liên quan đến các tham số điều khiển quá trình inference, cụ thể là chiến lược chọn token (sampling strategy).

Các phương pháp chọn token phổ biến gồm:

- Greedy: chọn $argmax_i , p_i$ — tức là chọn token có xác suất cao nhất.
- Top-k: chỉ giữ lại k token có xác suất cao nhất, sau đó chọn ngẫu nhiên trong nhóm này.
- Top-p (nucleus sampling): chọn nhóm nhỏ nhất các token có tổng xác suất ≥ p, rồi lấy ngẫu nhiên trong nhóm đó.
- Temperature scaling: chia logits cho temperature $T$ trước khi áp dụng softmax, giúp điều chỉnh mức độ ngẫu nhiên của đầu ra.


Ta ký hiệu các token được sinh tại bước sau là $X_m[n+t]$, trong đó $t$ bắt đầu từ 1.

Sau khi chọn được $token_{n+t}$, ta cần tính toán mức độ liên quan giữa token mới này và các token trước đó theo các bước sau:
- Tính embedding của $token_{n+t}$.
- Tính các ma trận Q, K, V và Attention giữa $token_{n+t}$ và toàn bộ các token còn lại trong prompt.
- Lặp lại quá trình sinh token cho đến khi thỏa mãn điều kiện dừng (ví dụ: gặp token kết thúc hoặc đạt độ dài tối đa).

Phần dưới đây sẽ giải thích chi tiết quá trình tính Attention cho token mới.


Tiếp theo, ta tính các ma trận $Q$, $K$, $V$ cho token $n+t$ dựa trên vector đặc trưng $X_m[n+t]$ như sau:

$$
Q_i = X_m[n+t] \ . \ W_{q_i} \ (13) \\
K_i = X_m[n+t] \ . \ W_{k_i} \ (14) \\
V_i = X_m[n+t] \ . \ W_{v_i} \ (15) \\
$$

trong đó

$$
X_m[n+t] \in \mathbb{R}^{d_{model}} \\
\Rightarrow \ Q_i, K_i, V_i \in \mathbb{R}^{d_{model}, \: d_{head}} \ \text{với} \ i = 1...n_{head}
$$

Tính Attention 

$$
\text{Attention}\!\left(Q_i^{(t)}, K_i^{(1 \dots n+t)}, V_i^{(1 \dots n+t)}\right)
= \text{softmax}\!\left( \frac{Q_i^{(n+t)} K_i^{(1 \dots n+t)^\top}}{\sqrt{d_{\text{head}}}} \right)
\, V_i^{(1 \dots n+t)}
$$

trong đó

$$
Q^{n+t}_i \in \mathbb{R}^{ d_{head}} \ \text{với} \ i = 1...n_{head} \\
K_i, \ V_i \in \mathbb{R}^{n+t, \ d_{head}} \ \text{với} \ i = 1...n_{head} \\
\Rightarrow \text{Attention}(Q_i, K_i, V_i) \in \mathbb{R}^{n+t, \ d_{head}} \text{với} \ i = 1...n_{head} \\
\Rightarrow A \in \mathbb{R}^{n+t, \: d_{model}}
$$

Sau bước này, ta tiếp tục lặp lại quy trình tương tự như trong phần Transformer để sinh các token tiếp theo, cho đến khi đạt điều kiện dừng (ví dụ: sinh ra token kết thúc hoặc đạt độ dài tối đa).

## II. Một số phương pháp tối ưu

Ở phần trước, chúng ta đã tìm hiểu các bước giúp LLM sinh ra token mới.
Trong phần này, mình sẽ chia sẻ những phương pháp tối ưu hóa mà các inference server thường sử dụng để tăng tốc và giảm chi phí cho quá trình inference.

### 1. KV cache

Quan sát lại công thức (16), để tính Attention của token sinh thứ $t$, ta cần thực hiện phép nhân $Q \ . \ K^{T}$ có kích thước là $(n+t, \: n+t)$.

Do đó, độ phức tạp tính toán của phép nhân ma trận này là $O(n^2)$, và sẽ tăng nhanh theo độ dài của prompt.

Để giải quyết vấn đề này, các inference server thường dùng một phần bộ nhớ (RAM hoặc VRAM) để lưu trữ cache cho các giá trị $K$ và $V$ của prompt cùng các token đã sinh, nhằm tái sử dụng kết quả cũ và tránh tính toán dư thừa ở các bước tiếp theo.


### 2. Flash Attention

Nhìn lại công thứ 4, kết quả của $O = Q \ . \ K^T \text{với} \ O \in \mathbb{R}^{n, \: n}$

Dưới đây là bảng số liệu cho mức độ tương quan giữa số lượng token trong prompt, độ phức tạp tính toán $O$, và lượng bộ nhớ cần sử dụng trong quá trình inference:


| n_tokens | shape(0) | size(0) in FP16 (Gi) |
| --- | --- | --- |
| 512 | 262.144 | 0.00048 |
| 2048 | 4.194.304 | 0.0078 |
| 32.768 | 1.073.741.824 | 2 |


Với các model hỗ trợ 32k token, một head khi tính toán Attention có thể chiếm khoảng 2 GiB bộ nhớ.
Các model như GPT-3.5 hoặc GPT-4o có khoảng 100 head, nên chi phí lưu trữ và tính toán trở nên rất lớn.

Một số vấn đề phát sinh bao gồm:
- I/O lớn do phải tải và truy xuất lượng thông tin khổng lồ.
- Độ phức tạp tính toán cao khi số lượng token tăng.
- Bộ nhớ yêu cầu rất lớn để lưu trữ các giá trị trung gian (đặc biệt là $K$, $V$ cache).


Để giải quyết vấn đề này, người ta sử dụng thuật toán Flash Attention, trong đó các ma trận $Q$, $K$, $V$ được chia nhỏ thành các khối (block) có kích thước cố định (thường là 128 × 128).
Việc tính toán Attention trên từng khối nhỏ giúp giảm đáng kể lượng bộ nhớ tạm cần dùng, tăng khả năng song song hóa trên GPU, và giữ kết quả trung gian trong SRAM thay vì DRAM, từ đó tăng tốc độ và giảm chi phí tính toán.

Như vậy, ta có $Q_i, K_i, V_i \in \mathbb{R}^{128, \: 128} \text{với} \ i = 1...m$. Ta gọi tập $Q_i, K_i, V_i$ là các tensor.

Để tính toán các tensor một cách hiệu quả, người ta sử dụng một thành phần chuyên dụng trong GPU gọi là Tensor Core.
Tensor Core đảm nhiệm hai chức năng chính:
Tính toán hiệu quả trên 2 ma trận có precision khác nhau, ví dụ FP16 x INT8, phù hợp cho các quantization model


Trên CPU hoặc CUDA core, cơ chế vectorization cho phép thực hiện song song nhiều phép tính trên các phần tử của một vector (tương tự SIMD – Single Instruction, Multiple Data).
Trong khi đó, Tensor Core nâng cấp mức song song này — thay vì xử lý từng vector riêng lẻ, nó thực hiện phép nhân giữa các ma trận nhỏ (tức là nhiều vector cùng lúc) chỉ trong một chu kỳ lệnh, giúp tăng tốc độ xử lý vượt trội trong các bài toán như attention và matrix multiplication.

Trên đây là hai tối ưu quan trọng liên quan trực tiếp đến các công thức tính toán của LLM.
Tuy nhiên, trong thực tế, các inference server còn áp dụng nhiều kỹ thuật tối ưu khác như Paged KV Cache, Weight Sharing, Operator Fusion,…
Những nội dung này mình sẽ trình bày chi tiết hơn trong các bài viết tiếp theo.

## II. Tổng kết

Vậy mà mình đã chia sẻ cách mà các Large Language Model hoạt động để chúng ta thấy được những pain point trong quá trình inference cũng như cách các inference server và GPU tối ưu chúng.

Trong những bài viết sau, mình sẽ chia sẻ về ý nghĩa toán học ở high level (low level thì chắc không do mình không phải dân chuyên 😄) cách LLM được thiết kế cũng như training/triển khai 1 LLM bằng Tensorflow code.

## III. Tài liệu tham khảo
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135)
- [Tensor Cores in a Nutshell](https://www.youtube.com/watch?v=yyR0ZoCeBO8)