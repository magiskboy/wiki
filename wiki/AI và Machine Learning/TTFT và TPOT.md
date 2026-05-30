---
tags:
  - ai
date: 2026-05-29
---
# TTFT và TPOT

TTFT và TPOT là hai metric độ trễ chuẩn của LLM serving, mỗi metric ứng với một phase của quá trình inference. Vì inference gồm phase prefill (xử lý toàn bộ prompt) và phase decode (sinh token tuần tự), việc tách riêng hai metric cho phép đo và tối ưu từng phase độc lập.

Time to First Token (TTFT) đo thời gian từ khi request đến tới khi token đầu tiên được sinh ra. TTFT phản ánh chi phí của phase prefill nên tăng theo độ dài prompt, và thường được chia thành ba phần: network latency đưa request tới server, thời gian chờ trong queue, và thời gian prefill. Prefill là compute-heavy, và có thể được tăng tốc khi server đã có sẵn prefix cache cho phần prompt trùng lặp.

Time Per Output Token (TPOT) đo thời gian trung bình giữa hai token liên tiếp trong phase decode. Decode là memory-heavy và scale theo số token được sinh, nên TPOT quyết định độ "mượt" mà người dùng cảm nhận khi token được stream về. TTFT thường là metric ràng buộc hơn TPOT trong thực tế.

Độ trễ end-to-end (E2E) xấp xỉ bằng `TTFT + (số token sinh × TPOT)`. Để so sánh các request có độ dài output khác nhau, người ta dùng NTPOT (Normalized Time Per Output Token) — E2E latency chia cho số token output.

```mermaid
flowchart LR
    A["Request den"] -->|"TTFT: network + queue + prefill"| B["Token dau tien"]
    B -->|"TPOT"| C["Token 2"]
    C -->|"TPOT"| D["..."]
    D -->|"TPOT"| E["Token cuoi"]
```

# Nguồn tham khảo

- [Predicted-Latency Based Scheduling for LLMs - llm-d.ai](<../../references/llm-d.ai-Predicted-Latency Based Scheduling for LLMs.pdf>)
- [DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving](https://arxiv.org/abs/2401.09670)

# Liên kết tri thức

- [Quá trình inference của Large Language Model](./Qu%C3%A1%20tr%C3%ACnh%20inference%20c%E1%BB%A7a%20Large%20Language%20Model.md) - TTFT đo phase prefill, TPOT đo phase decode trong cùng pipeline inference
- [Time to First Byte](../Web%20development/Time%20to%20First%20Byte.md) - TTFT là metric đối ứng của TTFB cho LLM serving thay vì cho web request
- [Lập lịch dựa trên độ trễ dự đoán cho LLM](./L%E1%BA%ADp%20l%E1%BB%8Bch%20d%E1%BB%B1a%20tr%C3%AAn%20%C4%91%E1%BB%99%20tr%E1%BB%85%20d%E1%BB%B1%20%C4%91o%C3%A1n%20cho%20LLM.md) - Scheduler dự đoán TTFT và TPOT để chọn server tối ưu
