---
name: export-knowledge
description: Dùng khi muốn bổ sung tri thức vào kho tri thức
---

# Phương pháp nghiên cứu

1. Xác định các đối tượng cần phải nghiên cứu trong yêu cầu của người dùng

2. Nếu các đối tượng đã có trong kho tri thức, hãy liên kết tới nó bằng link [Tên tri thức](<link tới tri thức>) khi nhắc tới chúng. Nếu đối tượng đó chưa có trong kho tri thức, thực hiện tìm kiếm thông tin về nó từ các nguồn tham khảo.

3. Liên kết tri thức với các kiến thức đã biết để tìm điểm cốt lõi và có thể bổ sung vào kho tri thức (đồ thị tri thức).
   - Tri thức mới có thể cùng pattern, là một kiến thức được kết thừa từ kiến thức đã biết,... hoặc bất kì một các liên kết gì có thể có.   


# Quy tắc chọn nguồn tham khảo

- thông tin học thuật (về khoa học máy tính,...) có thể tìm từ các nguồn như arxiv, google schoolar,... hoặc blog và website của các chuyên gia đầu ngành trong lĩnh vực đó.
- các công nghệ, thư viện, phần mềm và giải pháp cần tìm từ các nguồn như trang chủ của công nghệ đó, blog của các tác giả, contributor hoặc các diễn đàn, cộng đồng
- về coding, luôn tìm kiếm source code từ github, gitlab hoặc trang chủ của các thư viện


# Quy tắc đặt tên tri thức
- tên phản ánh đúng thực thể, khái niệm của tri thức
- tên của tri thức phải ngắn gọn và súc tích, không chứa những từ mang nghĩa phủ định
- không bao gồm số đếm hoặc số thứ tự trong tên


# Quy tắc viết nội dung tri thức 
- không sử dụng những từ ẩn ý như cái này, cái kia,.. hoặc giải thích khái niệm bằng một đối tượng ẩn như cái này, cái kia,...
- sử dụng thuật ngữ đồng nhất trong tài liệu, ví dụ không sử dụng tri thức và kiến thức trong cùng 1 tài liệu.
- một số thuật ngữ phổ biến hơn khi là Tiếng Anh, với những thuật ngữ này, hãy sử dụng phiên bản Tiếng Anh thay vì dịch sang Tiếng Việt
- sử dụng tối đa thuật ngữ chuyên ngành của tri thức
- hạn chế phân cấp nội dung trong tri thức, chỉ sử dụng tối đa 3 level khi cấu trúc nội dung tri thức
- tri thức cần được chia nhỏ để mỗi phần của tri thức có thể hiểu độc lập một cách dễ dàng
- mọi luận điểm cần có dẫn chứng từ nguồn uy tín, không được suy luận ngoài những nguồn thông tin tìm được.
- chỉ sử dụng gạch đầu dòng khi nội dung của từng phần tử đã rất rõ ràng
- những tri thức quá nhỏ mà có liên quan rất gần với những tri thức đẫ có thì nên bổ sung tri thức đó vào những tri thức đã biết
- có thể sử dụng các rich component để hỗ trợ giải thích tri thức như code block, mermaid, hình ảnh,...

# Quy tắc liên kết tri thức
- tri thức được tổ chức dưới dạng đồ thị vô hướng
- các đỉnh của đồ thị là các tri thức, các cạnh phản ánh tư duy liên kết các mảnh tri thức lại với nhau
- hai đỉnh có thể có nhiều cạnh, điều đó thể hiện hai tri thức có nhiều khía cạnh của việc tư duy để liên kết chúng


# Quy tắc viết tri thức ra Markdown file
- không sử dụng ASCII để vẽ hình họa, sử dụng mermaid để vẽ sơ đồ (nếu cần). Sơ đồ không quá lớn để tránh quá tải khi đọc hiểu.
- cấu trúc file markdown gồm 2 phần:
    - title: là tên của tri thức
    - phần nội dung
    - phần danh sách liên kết: sử dụng `[]()` của markdown để liên kết các tài liệu tri thức trong kho tri thức với nhau. Label của liên kết có cấu trúc `<Tên tri thức> - <Cách tư duy>`
    - tags: đánh tag phục vụ cho phân loại và thống kê tri thức, tham khảo danh sách tags của kho tri thức trong [wiki/_tags.md](../wiki/_tags.md). Nếu là tag mới, hãy bổ sung vào [wiki/_tags.md](../wiki/_tags.md).
    - bổ sung tri thức vào [wiki/_index.md](../wiki/_index.md) với dạng `[<tên tri thức>](<liên kết tới tri thức>)`
- Đây là template markdown của file tri thức
```markdown
# Tên của tri thức (sử dụng heading 1)

# Các phần triển khai nội dung của tri thức

# Nguồn tham khảo
<danh sách các nguồn đã tham khảo>

# Liên kết tri thức
<danh sách các liên kết trong kho tri thức>

# Tags
<danh sách tag>
```


# Quy tắc trả lời người hỏi
- không giải thích phức tạp vào tri thức đã được viết trong file.
- sau khi viết tri thức ra file, hãy báo caó lại cho người dùng vị trí của tri thức vừa bổ sung vào kho tri thức có vị trí như thế nào trong kho tri thức.