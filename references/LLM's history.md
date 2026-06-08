# Lịch sử tiến hóa kiến trúc LLM — Tuyển tập bài báo gốc

> Bản report theo dòng thời gian, tập trung vào **các bài báo công bố kiến trúc kỹ thuật**. Mỗi mục gồm: tên bài, link nguồn (ưu tiên arXiv → Hugging Face → venue gốc), độ uy tín (số trích dẫn), và tóm tắt sơ.

## Ghi chú về cách đọc

- **Về số trích dẫn:** Con số là **ước lượng theo Google Scholar (GS), thời điểm đầu năm 2026**. GS thường cao hơn Semantic Scholar (SS) 20–40%. Trích dẫn thay đổi liên tục — hãy coi đây là _thang độ ảnh hưởng tương đối_ chứ không phải con số tuyệt đối; bấm link để xem số hiện hành. Mốc duy nhất được xác thực qua tra cứu là _Attention Is All You Need_ (>200.000 GS / ~158.000 SS).
- **Về nền kiến thức của bạn:** Bạn đã quen MLP, CNN, RNN, backprop. Vì vậy các tóm tắt dưới đây sẽ neo khái niệm mới vào nền đó (ví dụ: attention được giải thích như "lời đáp cho điểm yếu của RNN"; MoE như "thay khối FFN dày đặc bằng nhiều chuyên gia thưa").
- **Đường dây chính của tiến hóa:** RNN/attention phụ trợ → Transformer thuần attention → tách nhánh encoder (BERT) / decoder (GPT) → scaling → quy luật scaling → alignment (RLHF) → mở nguồn & hiệu quả (MoE) → tiền tuyến (MLA, MTP) + nhánh thay thế attention (SSM/Mamba).

---

## Giai đoạn 1 — Nền tảng tiền-Transformer (2013–2016)

_Bối cảnh: NLP dựa vào RNN/LSTM xử lý tuần tự — khó song song hóa, yếu với phụ thuộc xa. Đây là các hạt giống của ý tưởng "biểu diễn phân tán" và "attention"._

### 1.1. Efficient Estimation of Word Representations in Vector Space (Word2Vec)

- **arXiv:** https://arxiv.org/abs/1301.3781
- **Trích dẫn:** ≈ 45.000+ (GS)
- **Tóm tắt:** Mikolov et al. (2013) giới thiệu cách học _word embedding_ phân tán hiệu quả (CBOW & Skip-gram). Biến mỗi từ thành một vector mật độ cao mang ngữ nghĩa, thay cho one-hot thưa thớt. Đây là tiền đề cho mọi mô hình ngôn ngữ về sau: ý tưởng "ngữ nghĩa nằm trong không gian vector".

### 1.2. Sequence to Sequence Learning with Neural Networks (Seq2Seq)

- **arXiv:** https://arxiv.org/abs/1409.3215
- **Trích dẫn:** ≈ 30.000+ (GS)
- **Tóm tắt:** Sutskever, Vinyals & Le (2014) đề xuất kiến trúc _encoder–decoder_ dùng LSTM: encoder nén toàn bộ câu nguồn vào một vector ngữ cảnh cố định, decoder sinh câu đích từ đó. Mở ra paradigm "ánh xạ chuỗi sang chuỗi" — nhưng nút thắt là vector ngữ cảnh cố định.

### 1.3. Neural Machine Translation by Jointly Learning to Align and Translate (Bahdanau Attention)

- **arXiv:** https://arxiv.org/abs/1409.0473
- **Trích dẫn:** ≈ 40.000+ (GS)
- **Tóm tắt:** Bahdanau, Cho & Bengio (2014) khai sinh **cơ chế attention**. Thay vì ép cả câu vào một vector cố định (nút thắt của Seq2Seq), decoder được phép "nhìn lại" và đánh trọng số mọi vị trí của câu nguồn ở mỗi bước sinh. Đây là viên gạch khái niệm trực tiếp dẫn tới Transformer — lúc này attention vẫn chỉ là _phụ trợ_ cho RNN.

---

## Giai đoạn 2 — Transformer và hai nhánh pretraining (2017–2019)

_Bối cảnh: Bước ngoặt. Attention từ "phụ trợ" trở thành "tất cả". Transformer sau đó tách thành hai dòng: encoder-only (hiểu) và decoder-only (sinh)._

### 2.1. Attention Is All You Need (Transformer) ⭐ BẮT BUỘC ĐỌC

- **arXiv:** https://arxiv.org/abs/1706.03762
- **Venue:** NeurIPS 2017
- **Trích dẫn:** **> 200.000 (GS, 12/2025)** — một trong các bài có ảnh hưởng nhất lịch sử AI.
- **Tóm tắt:** Vaswani et al. (2017) đề xuất kiến trúc dựa **hoàn toàn vào attention**, loại bỏ recurrence và convolution. Hai trụ cột: _self-attention_ (mỗi token "trò chuyện" với mọi token khác trong chuỗi) và _multi-head attention_. Ưu thế quyết định so với RNN: **song song hóa được trên GPU** → huấn luyện nhanh hơn và mô hình lớn hơn nhiều. Đây là nền móng của gần như mọi LLM hiện đại.

### 2.2. BERT: Pre-training of Deep Bidirectional Transformers

- **arXiv:** https://arxiv.org/abs/1810.04805
- **Trích dẫn:** ≈ 130.000+ (GS)
- **Tóm tắt:** Devlin et al. (2018) — nhánh **encoder-only**. Huấn luyện hai chiều (nhìn cả trái lẫn phải) qua _masked language modeling_ (đoán từ bị che) và _next sentence prediction_. Vượt trội cho các bài toán _hiểu_ văn bản (phân loại, hỏi đáp, NER). Đối trọng với dòng GPT về triết lý: hiểu vs. sinh.

### 2.3. Improving Language Understanding by Generative Pre-Training (GPT-1)

- **Nguồn (OpenAI report, không có arXiv):** https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf
- **Trích dẫn:** ≈ 12.000+ (GS)
- **Tóm tắt:** Radford et al. (2018) khởi đầu nhánh **decoder-only** sinh văn bản — tổ tiên trực tiếp của ChatGPT. Công thức: pretraining tự giám sát (đoán token kế tiếp) trên corpus lớn, rồi fine-tune cho từng tác vụ.

### 2.4. Language Models are Unsupervised Multitask Learners (GPT-2)

- **Nguồn (OpenAI report):** https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
- **Trích dẫn:** ≈ 15.000+ (GS)
- **Tóm tắt:** Radford et al. (2019) mở rộng decoder-only lên 1,5B tham số. Phát hiện cốt lõi: chỉ cần scale, mô hình bắt đầu làm được nhiều tác vụ _mà không cần fine-tune riêng_ (zero-shot). Gợi mở mối liên hệ "quy mô ↔ năng lực đa nhiệm".

---

## Giai đoạn 3 — Kỷ nguyên scaling và các quy luật (2020–2022)

_Bối cảnh: Câu hỏi trung tâm chuyển thành "nếu cứ phóng to thì sao?". Sau đó là các bài lượng hóa chính xác việc phóng to nên làm thế nào._

### 3.1. Language Models are Few-Shot Learners (GPT-3) ⭐

- **arXiv:** https://arxiv.org/abs/2005.14165
- **Hugging Face:** https://huggingface.co/papers/2005.14165
- **Trích dẫn:** ≈ 45.000+ (GS)
- **Tóm tắt:** Brown et al. (2020) — 175B tham số, gấp 10× mọi mô hình dày đặc trước đó. Kiến trúc gần như y hệt GPT-2, chỉ scale lên. Đột phá về _hành vi_: **in-context / few-shot learning** — mô hình giải tác vụ mới chỉ từ vài ví dụ trong prompt, không cập nhật gradient. Đây là bài làm cả ngành tin vào sức mạnh của scale.

### 3.2. Scaling Laws for Neural Language Models

- **arXiv:** https://arxiv.org/abs/2001.08361
- **Trích dẫn:** ≈ 3.500+ (GS)
- **Tóm tắt:** Kaplan et al. (2020) phát hiện hiệu năng (loss) tuân theo **quy luật lũy thừa (power law)** trơn tru theo ba yếu tố: số tham số, lượng dữ liệu, và compute. Lần đầu việc "scale" trở thành một khoa học có thể _dự đoán_ thay vì thử-sai. Nền tảng tư duy cho mọi quyết định huấn luyện sau này.

### 3.3. Training Compute-Optimal Large Language Models (Chinchilla) ⭐

- **arXiv:** https://arxiv.org/abs/2203.15556
- **Trích dẫn:** ≈ 4.000+ (GS)
- **Tóm tắt:** Hoffmann et al. (2022, DeepMind) **hiệu chỉnh lại** quy luật của Kaplan: với một ngân sách compute cho trước, hầu hết mô hình lớn lúc đó bị _thiếu dữ liệu nghiêm trọng_. Tỷ lệ tối ưu xấp xỉ ~20 token dữ liệu cho mỗi tham số. Chinchilla 70B đánh bại các mô hình lớn hơn nhiều. Bài cực kỳ quan trọng về mặt khái niệm — định hình lại toàn ngành.

### 3.4. PaLM: Scaling Language Modeling with Pathways

- **arXiv:** https://arxiv.org/abs/2204.02311
- **Trích dẫn:** ≈ 8.000+ (GS)
- **Tóm tắt:** Chowdhery et al. (2022, Google) — dense Transformer 540B. Đáng đọc để thấy đỉnh cao của hướng "mô hình dày đặc khổng lồ" và các kết quả về khả năng suy luận xuất hiện khi đủ lớn (emergent abilities).

---

## Giai đoạn 4 — Bản lề alignment: từ mô hình thô thành trợ lý (2022)

_Bối cảnh: Mô hình lớn giỏi đoán token kế tiếp nhưng không nhất thiết làm theo ý người dùng. Đây là mảnh ghép biến năng lực thô thành sản phẩm hữu dụng._

### 4.1. Training Language Models to Follow Instructions with Human Feedback (InstructGPT) ⭐

- **arXiv:** https://arxiv.org/abs/2203.02155
- **Hugging Face:** https://huggingface.co/papers/2203.02155
- **Trích dẫn:** ≈ 15.000+ (GS)
- **Tóm tắt:** Ouyang et al. (2022, OpenAI) giới thiệu **RLHF** (học tăng cường từ phản hồi con người): huấn luyện một _reward model_ từ so sánh của người, rồi tối ưu mô hình ngôn ngữ theo phần thưởng đó (PPO). Bản lề trực tiếp tạo ra ChatGPT. Đáng chú ý: một mô hình 1,3B sau alignment được ưa thích hơn GPT-3 175B chưa align — chứng minh "căn chỉnh" quan trọng ngang "quy mô".

---

## Giai đoạn 5 — Mở nguồn, hiệu quả hóa và Mixture-of-Experts (2021–2024)

_Bối cảnh: Trọng tâm chuyển từ "lớn nhất" sang "hiệu quả nhất trên mỗi đơn vị compute" và "mở để cộng đồng dùng được". MoE là ý tưởng then chốt: tách tổng số tham số khỏi chi phí tính toán mỗi token._

### 5.1. Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer

- **arXiv:** https://arxiv.org/abs/1701.06538
- **Trích dẫn:** ≈ 3.000+ (GS)
- **Tóm tắt:** Shazeer et al. (2017) — gốc rễ của MoE hiện đại. Thay một khối FFN dày đặc bằng _nhiều "chuyên gia"_ (mỗi expert là một FFN), và một _gating network_ định tuyến mỗi token tới vài expert phù hợp. Kết quả: số tham số tăng vọt nhưng chi phí tính toán mỗi token gần như giữ nguyên (kích hoạt thưa).

### 5.2. Switch Transformers: Scaling to Trillion Parameter Models

- **arXiv:** https://arxiv.org/abs/2101.03961
- **Venue:** JMLR 2022 — https://jmlr.org/papers/v23/21-0998.html
- **Trích dẫn:** ≈ 3.500+ (GS)
- **Tóm tắt:** Fedus, Zoph & Shazeer (2021, Google) đơn giản hóa MoE: mỗi token chỉ định tuyến tới **đúng một** expert (top-1, k=1) thay vì top-k. Giảm chi phí định tuyến, ổn định huấn luyện, và mở đường tới mô hình nghìn tỷ tham số. Một mốc kỹ thuật quan trọng của nhánh thưa.

### 5.3. LLaMA: Open and Efficient Foundation Language Models ⭐

- **arXiv:** https://arxiv.org/abs/2302.13971
- **Trích dẫn:** ≈ 18.000+ (GS)
- **Tóm tắt:** Touvron et al. (2023, Meta) chứng minh mô hình _nhỏ hơn_ huấn luyện trên _nhiều dữ liệu hơn_ (tinh thần Chinchilla) có thể sánh GPT-3. Quan trọng hơn: phổ cập một bộ "thành phần kiến trúc hiện đại" giờ thành chuẩn — **RMSNorm**, **SwiGLU**, **RoPE** (rotary positional embedding). Việc mở trọng số đã châm ngòi cho hệ sinh thái mô hình mở.

### 5.4. Mixtral of Experts

- **arXiv:** https://arxiv.org/abs/2401.04088
- **Hugging Face:** https://huggingface.co/papers/2401.04088
- **Trích dẫn:** ≈ 2.500+ (GS)
- **Tóm tắt:** Jiang et al. (2024, Mistral AI) — MoE thưa _thực dụng_ và mở: 8 expert mỗi lớp, mỗi token kích hoạt 2. Tổng ~47B tham số nhưng chi phí suy luận chỉ tương đương ~13B. Bằng chứng thuyết phục rằng MoE mở có thể đua với mô hình dày đặc hàng đầu.

### 5.5. The Llama 3 Herd of Models ⭐

- **arXiv:** https://arxiv.org/abs/2407.21783
- **Hugging Face:** https://huggingface.co/papers/2407.21783
- **Trích dẫn:** ≈ 4.000+ (GS)
- **Tóm tắt:** Meta (2024) — technical report ~90 trang cực kỳ chi tiết. Mô hình lớn nhất là dense Transformer **405B**, cửa sổ ngữ cảnh tới **128K** token, sánh ngang GPT-4 trên nhiều benchmark. Đáng đọc vì minh bạch toàn bộ quy trình _data → pre-training → post-training_ — gần như một "sách giáo khoa" thực hành hiện đại.

### 5.6. Qwen2 Technical Report

- **arXiv:** https://arxiv.org/abs/2407.10671
- **Hugging Face:** https://huggingface.co/papers/2407.10671
- **Trích dẫn:** ≈ 2.000+ (GS)
- **Tóm tắt:** Yang et al. (2024, Alibaba) — dòng mô hình mở mạnh, có cả biến thể dense lẫn MoE, đa ngôn ngữ, ngữ cảnh dài. Hữu ích để thấy hướng tiếp cận song song với Llama trong hệ sinh thái mở.

---

## Giai đoạn 6 — Tiền tuyến và kiến trúc thay thế (2023–2025)

_Bối cảnh: Tối ưu sâu vào cơ chế attention/bộ nhớ (MLA, MTP) và đặt câu hỏi căn bản: liệu attention có thực sự là "tất cả"? — sự trỗi dậy của state-space models._

### 6.1. GPT-4 Technical Report

- **arXiv:** https://arxiv.org/abs/2303.08774
- **Trích dẫn:** ≈ 18.000+ (GS)
- **Tóm tắt:** OpenAI (2023). **Lưu ý quan trọng:** báo cáo này _không_ tiết lộ chi tiết kiến trúc, dữ liệu hay quy mô. Đưa vào đây không phải vì giá trị kỹ thuật mở, mà để đánh dấu **bước ngoặt "đóng"** của các phòng lab thương mại — một chiều hướng của sự tiến hóa đáng đối chiếu với dòng mở (Llama, DeepSeek).

### 6.2. DeepSeek-V3 Technical Report ⭐ NÊN ĐỌC KỸ

- **arXiv:** https://arxiv.org/abs/2412.19437
- **Hugging Face:** https://huggingface.co/papers/2412.19437
- **Trích dẫn:** ≈ 1.500+ (GS, đang tăng nhanh)
- **Tóm tắt:** DeepSeek-AI (2024) — MoE **671B tham số tổng, chỉ 37B kích hoạt mỗi token**. Gói gọn nhiều đổi mới kiến trúc đương đại: **Multi-head Latent Attention (MLA)** (nén key-value để giảm bộ nhớ KV-cache khi suy luận ngữ cảnh dài), **DeepSeekMoE**, cân bằng tải **không cần auxiliary-loss**, và mục tiêu **multi-token prediction (MTP)**. Huấn luyện chỉ tốn ~2,79 triệu giờ GPU H800 — kỳ tích về hiệu quả. Technical report đáng đọc nhất hiện nay nếu muốn hiểu "kiến trúc 2024 trông như thế nào".

### 6.3. Mamba: Linear-Time Sequence Modeling with Selective State Spaces ⭐

- **arXiv:** https://arxiv.org/abs/2312.00752
- **Trích dẫn:** ≈ 3.500+ (GS)
- **Tóm tắt:** Gu & Dao (2023) — đối trọng nghiêm túc nhất với attention. Dựa trên **state-space models (SSM)**, độ phức tạp **tuyến tính** theo độ dài chuỗi (attention là bậc hai). Đột phá: cho tham số SSM trở thành _hàm của đầu vào_ (selective), khắc phục điểm yếu suy luận dựa trên nội dung của SSM cũ. Suy luận nhanh ~5× và xử lý được chuỗi dài tới hàng triệu token. Đọc để có góc nhìn phản biện: attention có thể _không_ phải là "tất cả".

### 6.4. Transformers are SSMs: Generalized Models and Efficient Algorithms (Mamba-2)

- **arXiv:** https://arxiv.org/abs/2405.21060
- **Venue:** ICML 2024
- **Trích dẫn:** ≈ 1.000+ (GS)
- **Tóm tắt:** Dao & Gu (2024) thiết lập "tính đối ngẫu" (duality) lý thuyết giữa attention và SSM — cho thấy hai thế giới tưởng đối lập thật ra liên hệ chặt chẽ. Hữu ích để hiểu nhánh thay thế attention đang hội tụ về đâu.

---

## Lộ trình đọc gợi ý

**Nếu mục tiêu là hiểu _mạch tiến hóa_ (không chỉ sưu tầm),** đọc theo trục dọc 6 bài đủ kể trọn câu chuyện "vì sao kiến trúc hôm nay trông như vậy":

1. **1706.03762** (Transformer) — vì sao bỏ RNN.
2. **1810.04805** (BERT) — nhánh hiểu, hai chiều.
3. **2005.14165** (GPT-3) — nhánh sinh + sức mạnh của scale.
4. **2203.15556** (Chinchilla) — scale _đúng cách_.
5. **2203.02155** (InstructGPT) — biến năng lực thành trợ lý.
6. **2412.19437** (DeepSeek-V3) — tổng hợp đổi mới kiến trúc hiện đại.

**Hai nhánh rẽ mở rộng góc nhìn:** MoE (đọc **2101.03961** Switch → **2401.04088** Mixtral) và state-space (đọc **2312.00752** Mamba).

---

## Bảng tổng hợp nhanh

|#|Bài báo|Năm|arXiv|Trích dẫn (≈, GS)|
|---|---|---|---|---|
|1|Word2Vec|2013|1301.3781|45.000+|
|2|Seq2Seq|2014|1409.3215|30.000+|
|3|Bahdanau Attention|2014|1409.0473|40.000+|
|4|**Transformer**|2017|1706.03762|**200.000+**|
|5|BERT|2018|1810.04805|130.000+|
|6|GPT-1|2018|(OpenAI)|12.000+|
|7|GPT-2|2019|(OpenAI)|15.000+|
|8|GPT-3|2020|2005.14165|45.000+|
|9|Scaling Laws|2020|2001.08361|3.500+|
|10|Chinchilla|2022|2203.15556|4.000+|
|11|PaLM|2022|2204.02311|8.000+|
|12|InstructGPT|2022|2203.02155|15.000+|
|13|Sparsely-Gated MoE|2017|1701.06538|3.000+|
|14|Switch Transformer|2021|2101.03961|3.500+|
|15|LLaMA|2023|2302.13971|18.000+|
|16|Mixtral|2024|2401.04088|2.500+|
|17|Llama 3|2024|2407.21783|4.000+|
|18|Qwen2|2024|2407.10671|2.000+|
|19|GPT-4|2023|2303.08774|18.000+|
|20|DeepSeek-V3|2024|2412.19437|1.500+|
|21|Mamba|2023|2312.00752|3.500+|
|22|Mamba-2|2024|2405.21060|1.000+|

_Số trích dẫn là ước lượng Google Scholar đầu 2026, thay đổi liên tục — bấm link để xem số hiện hành._