---
title: Giới thiệu về Model Context Protocol
date: "2025-03-30T21:10:00+07:00"
tags:
- ai
- llm
categories:
- AI
description: |
    Ngày nay, AI được ứng dụng rộng rãi trong nhiều lĩnh vực, đặc biệt là trong các công việc hằng ngày của dân văn phòng và dân lập trình. Mặc dù AI rất giỏi trong việc phân tích và hiểu dữ liệu, nhưng chúng vẫn gặp hạn chế về khả năng lưu trữ thông tin, truy xuất dữ liệu bên ngoài và tương tác với môi trường xung quanh.

    Trong bài viết này, mình sẽ giới thiệu một phương pháp giúp các mô hình AI mở rộng khả năng truy cập dữ liệu cũng như tương tác linh hoạt hơn với các đối tượng trong hệ thống.
---


## Bài toán

Các mô hình AI hiện nay có khả năng phân tích thông tin vô cùng hiệu quả, nhưng chúng không thể tự cập nhật kiến thức mới. Lý do là vì thông tin luôn thay đổi từng ngày và đôi khi, AI không có quyền hoặc khả năng truy cập vào nguồn dữ liệu cần thiết. Trên thực tế, con người cũng gặp phải giới hạn tương tự trong việc tiếp cận và xử lý thông tin.

Ví dụ: AI không thể đọc email cá nhân của bạn, cũng như không biết những diễn biến mới nhất trong vụ lùm xùm của streamer ViruSs, đơn giản vì những thông tin này xuất hiện sau khi mô hình AI được huấn luyện.

Một hạn chế khác là khả năng tương tác với môi trường xung quanh. Chẳng hạn, AI không thể tự động gửi tin nhắn hay mở một bài hát trên YouTube từ máy tính của bạn mà không có sự hỗ trợ từ các công cụ bên ngoài.

Tóm lại, hãy hình dung AI như một bộ não con người—có khả năng phân tích mạnh mẽ nhưng cũng tồn tại nhiều giới hạn. Chúng không thể biết mọi thứ, không thể tự mình truy cập hay thao tác với mọi thứ nếu không có __công cụ hỗ trợ__.

## Giải pháp

Cộng đồng AI đã và đang phát triển một công cụ, một giao thức giúp các mô hình AI có thể giao tiếp và sử dụng __công cụ hỗ trợ__ để tìm kiếm, mở rộng thông tin cũng như tương tác với môi trường xung quanh một cách hiệu quả hơn.

Hãy thử ánh xạ điều này sang con người: giao thức giúp chúng ta mở rộng tri thức và tiếp cận thông tin chính là ngôn ngữ. Ngôn ngữ đóng vai trò như một giao thức tự nhiên, cho phép bộ não con người suy luận, phân tích và tiếp thu kiến thức mới mà không cần ghi nhớ mọi thứ.

Tương tự như vậy, các mô hình AI cũng cần một ngôn ngữ để tương tác với các __công cụ hỗ trợ__. Giao thức này được gọi là __Model Context Protocol__ (MCP), cho phép AI kết nối với các công cụ lập trình và mở rộng khả năng của mình ngoài phạm vi dữ liệu ban đầu.

## Model Context Protocol hoạt động như thế nào?

Mình sẽ không đi vào giải thích một cách máy móc hay quá chi tiết, vì những thông tin đó bạn hoàn toàn có thể tìm hiểu trực tiếp trên trang chủ của Model Context Protocol tại đây [https://modelcontextprotocol.io](https://modelcontextprotocol.io).

Hãy nhìn sơ đồ bên dưới


<figure>
<img src="/images/mcp-1.png">
</figure>


Notes: MCP host có thể là các ứng dụng AI như Claude Desktop hoặc Cursor AI Editor

MCP server chính là các máy chủ giúp mở rộng tri thức và khả năng tương tác của mô hình AI bằng cách cung cấp các công cụ hỗ trợ chuyên biệt.

Ví dụ:
- MCP server for Emails cung cấp các chức năng như:
    - Tìm danh sách email theo từ khóa hoặc khoảng thời gian.
    - Lấy nội dung của một email dựa trên email_id.
- MCP server for Social Networks hỗ trợ:
    - Truy xuất new feeds.
    - Lấy thông tin chi tiết của một bài viết theo post_id.
- MCP server for MacOS cho phép:
    - Gửi tin nhắn với nội dung chỉ định đến một người cụ thể.
    - Tạo ghi chú mới với nội dung tùy chỉnh.

Nhờ các MCP server này, AI có thể mở rộng khả năng của mình và thực hiện nhiều tác vụ ngoài phạm vi dữ liệu có sẵn.

Mỗi MCP server sẽ mô tả các function mà nó cung cấp để mô hình AI có thể sử dụng. Khi người dùng gửi truy vấn đến AI model, mô hình sẽ tự động quyết định:
- Có cần sử dụng một MCP function hay không?
- Nếu có, thì function nào là phù hợp nhất?
- Cách sử dụng function đó như thế nào để đáp ứng yêu cầu của người dùng?

Quá trình này giúp AI không chỉ phân tích thông tin mà còn biết khi nào và cách nào để mở rộng khả năng của mình thông qua các công cụ hỗ trợ.


Ví dụ:

Giả sử mình hỏi AI model: “Tính tổng số tiền đã giao dịch qua Vietcombank trong tháng này”, AI sẽ xử lý như sau:

1️⃣ Dựa trên truy vấn của người dùng và mô tả về các MCP function, AI xác định rằng cần sử dụng function lấy danh sách email.


2️⃣ AI trích xuất khoảng thời gian “trong tháng này” và lọc các email từ Vietcombank để gọi function phù hợp.


3️⃣ AI nhận kết quả là danh sách email giao dịch từ Vietcombank.


4️⃣ AI lần lượt gọi function để lấy nội dung chi tiết từng email, sau đó phân tích và trích xuất số tiền giao dịch.


5️⃣ Cuối cùng, AI tính tổng số tiền và trả kết quả về cho người dùng.


Nhờ cơ chế này, AI không chỉ trả lời dựa trên dữ liệu có sẵn mà còn biết cách tìm kiếm, truy xuất và xử lý thông tin từ môi trường bên ngoài, giúp câu trả lời chính xác và thực tế hơn. 🚀


## Mô tả kĩ thuật

Về bản chất, các MCP server chỉ là những tiến trình bình thường. Chúng giao tiếp với MCP host thông qua một trong hai phương thức sau:

🔹 stdin/stdout: MCP host sẽ khởi chạy MCP server như một tiến trình con và sử dụng stdin/stdout để trao đổi dữ liệu.

🔹 SSE (Server-Sent Events): MCP host và MCP server hoạt động như hai tiến trình độc lập. Chúng giao tiếp với nhau thông qua HTTP, tương tự như cách một web backend truyền thống hoạt động.

Hai phương thức này giúp MCP host linh hoạt trong việc kết nối với MCP server, tùy thuộc vào kiến trúc hệ thống và nhu cầu sử dụng. 🚀

Ví dụ:

Trong Claude Desktop của mình, MCP được mình cấu hình như sau:

<figure>
<img src="/images/mcp-claude-desktop.png">
</figure>


Trong Cursor AI Editor


<figure>
<img src="/images/mcp-cursor.png">
</figure>


Nếu bạn muốn tự tạo MCP cho riêng mình, hãy xem hướng dẫn chi tiết tại đây [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction).

Nếu bạn muốn tăng cường khả năng tìm kiếm và mở rộng mô hình AI, hãy tham khảo bài viết này của mình [Build a RAG system for AI agent](/posts/build-a-rag-system-for-ai-agent).


## Kết luận

Model Context Protocol (MCP) là một bước tiến quan trọng trong việc mở rộng khả năng của các mô hình AI. Thông qua MCP, chúng ta có thể:

- Tăng cường khả năng truy xuất và xử lý thông tin của AI một cách có hệ thống
- Cho phép AI tương tác với các hệ thống bên ngoài một cách an toàn và kiểm soát được
- Tạo ra một chuẩn thống nhất để phát triển các ứng dụng AI

Với sự phát triển nhanh chóng của công nghệ AI, MCP đang dần trở thành một tiêu chuẩn quan trọng trong việc xây dựng các ứng dụng AI thông minh và linh hoạt. Hy vọng qua bài viết này, các bạn đã có cái nhìn tổng quan về MCP và cách áp dụng nó vào các dự án của mình.

Hẹn gặp lại các bạn trong những bài viết tiếp theo! 🚀

