---
name: excavate-knowledge
description: Dùng khi muốn khai quật tri thức trải nghiệm đã mờ trong trí nhớ qua hội thoại, rồi đổ thành ghi chú thô để chưng cất sau. Bổ trợ cho add-knowledge (khâu lấy nguyên liệu, trước khi chưng cất thành node wiki).
---

# Mục đích

Khai quật những vùng tri thức người dùng từng trải qua nhưng đã mờ và không còn nhớ chủ động. Khác với add-knowledge (chưng cất tri thức thành node wiki) và socratic (dạy lại khái niệm), skill này lo khâu *moi ký ức ra* qua phỏng vấn, rồi đổ thành ghi chú thô trong `_source/tmp/` làm nguyên liệu cho add-knowledge.

Nguyên lý nền: recognition mạnh hơn recall. Đặt câu hỏi có mồi cụ thể để kích hoạt nhận diện, thay vì hỏi mở kiểu "kể về X". Phần giá trị nhất là tri thức trải nghiệm — thứ chỉ người dùng có; LLM không được bịa, chỉ được bổ sung kiến thức nền có nguồn và phải đánh dấu rõ.

# Điểm neo của một phiên

- Đơn vị làm việc là leaf nhỏ nhất trong [`_source/track.md`](../../../_source/track.md). Mỗi phiên khai quật một leaf.
- Có thể để người dùng chọn leaf, hoặc đề xuất leaf trông giàu trải nghiệm mà chưa có trong `wiki/`.

# Quy trình một phiên

1. **Định vị**: tra `wiki/` và `.lancedb` xem leaf đã dính node nào, để không hỏi lại thứ đã ghi và để biết điểm nối đồ thị.

2. **Phỏng vấn theo chùm**: hỏi một chùm câu theo khung gợi nhớ (xem dưới). Người dùng trả lời tự do, rời rạc cũng được; câu nào không nhớ thì bỏ qua.

3. **Dẫn dắt thích ứng**: dựa trên câu trả lời, khêu sâu vào vùng lân cận mà người dùng có thể từng trải qua nhưng chưa nhắc. Đây là phần quan trọng nhất — nó khôi phục cả mối nhân quả đã mờ, không chỉ chép lại ký ức. Muốn dẫn trúng cần kiến thức nền về leaf; gặp vùng không rành thì nghiêng về câu hỏi gợi nhớ thuần và để người dùng dẫn.

4. **Phản chiếu và nối đồ thị**: tóm lại điều người dùng vừa nói, chỉ ra liên kết với node wiki đã có.

5. **Đổ thô**: ghi transcript đã chắt lọc vào `_source/tmp/<tên-leaf>.md`, dùng ba marker (xem dưới). Không cần verify nguồn ở bước này — đó là việc của bước tinh.

6. **Cập nhật tiến độ**: đổi trạng thái leaf trong [`_source/track.md`](../../../_source/track.md) (`[ ]` → `[~]` → `[x]`), kèm link node wiki và transcript khi đã xong.

7. **Bàn giao**: khi người dùng muốn tinh, dùng [add-knowledge](../add-knowledge/SKILL.md) để chưng cất ghi chú thô thành node wiki. Một leaf có thể tách thành nhiều node (tách concept tái dùng được ra khỏi node trải nghiệm).

8. **Lưu trữ transcript**: sau khi đã lên wiki, chuyển transcript từ `_source/tmp/` sang [`references/interviews/`](../../../references/interviews/) để giữ vĩnh viễn như nguồn tham khảo gốc (primary source), và cập nhật header transcript trỏ tới node wiki kết quả. Lý do: `_source/` là vùng staging tạm sẽ xoá khi migrate xong, còn transcript là nguồn gốc duy nhất cho tri thức trải nghiệm nên phải nằm trong `references/`. Node wiki nên trích transcript này trong mục nguồn cho phần `[Trí nhớ]`.

# Khung gợi nhớ (cued-recall)

Hỏi theo trục: bối cảnh (khi nào, ở đâu, vì sao phải làm) → vấn đề cụ thể → các phương án đã cân nhắc hoặc đã thử → cái gì chạy, cái gì fail → quyết định cuối và đánh đổi → chỗ bất ngờ hoặc vấp → bài học, nếu làm lại sẽ khác gì.

# Ba marker đánh dấu nguồn

Giữ trong cả ghi chú thô lẫn node wiki để phân biệt ký ức gốc và kiến thức bổ sung:

- **[Trí nhớ]** — do người dùng kể, là tài sản trải nghiệm gốc, không ai thay được.
- **[Bổ sung — nguồn]** — kiến thức nền do trợ lý thêm, bắt buộc kèm nguồn uy tín (verify link ở bước tinh).
- **[Chưa chắc]** — vùng người dùng không nhớ rõ. Giữ trung thực, không suy diễn, không ép nhớ.

Trong node wiki, có thể tách phần trải nghiệm cá nhân thành một mục riêng (vd "Trải nghiệm tại <nơi>") thay vì rải marker inline, miễn ranh giới giữa ký ức và kiến thức nền vẫn rõ.

# Nguyên tắc

- Không bịa trải nghiệm của người dùng. Khi cần làm giàu, chỉ thêm kiến thức nền có nguồn và đánh dấu **[Bổ sung — nguồn]**.
- Mỗi chùm câu không hỏi dồn quá mức; ưu tiên mồi cụ thể hơn câu hỏi mở.
- Tôn trọng nhịp người dùng: họ trả lời từng ý, không cần đủ ngay trong một lượt.
