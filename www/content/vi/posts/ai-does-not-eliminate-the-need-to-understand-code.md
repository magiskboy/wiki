---
title: AI không thay thế tư duy kỹ sư phần mềm
date: "2026-10-25T22:29:00+07:00"
score: 1
tags:
  - ai
categories:
  - AI
author: "Nguyễn Khắc Thành"
description: |
  AI đang giúp chúng ta viết code nhanh hơn bao giờ hết. Nhưng liệu tốc độ có phải là lý do để các kỹ sư phần mềm ngừng hiểu những gì mình xây dựng?
  
  Tôi cho rằng việc xem code do AI sinh ra như một black box là một sự đánh đổi nguy hiểm. Compiler và AI tạo sinh không hoạt động theo cùng một cơ chế. Viết được code không đồng nghĩa với việc tạo ra phần mềm đáng tin cậy, và sử dụng AI không có nghĩa là chúng ta có thể chuyển giao trách nhiệm nghề nghiệp cho nó.
  
  Tôi viết bài này để phân tích 4 góc nhìn: bản chất của AI, tư duy hệ thống, rủi ro tích lũy và trách nhiệm của người kỹ sư.
  
  AI nên khuếch đại năng lực của kỹ sư phần mềm, không phải trở thành cái cớ để chúng ta ngừng tư duy.
---

AI không biến code thành một black box. Chỉ có kỹ sư phần mềm mới đang lựa chọn đối xử với nó như vậy.

Tôi nhận thấy một xu hướng đáng suy nghĩ trong cộng đồng phát triển phần mềm hiện nay: một số người đang sẵn sàng chấp nhận những đoạn code do AI sinh ra mà không thực sự hiểu chúng, với lập luận rằng điều đó giúp tăng tốc độ phát triển.

Nhưng tôi cho rằng đây là một sự đánh đổi nguy hiểm, bắt nguồn từ việc hiểu sai bản chất của AI, vai trò của kỹ sư phần mềm và trách nhiệm đi kèm với sản phẩm mà họ tạo ra.

1. AI không phải là compiler chuyển ngôn ngữ của con người thành ngôn ngữ lập trình.

Một compiler truyền thống có thể được xem là một black box ở góc nhìn của người sử dụng. Tuy nhiên, bên trong nó là một hệ thống được xây dựng dựa trên những nguyên tắc xác định, các quy tắc ngôn ngữ, thuật toán và những thuộc tính có thể kiểm chứng.

Compiler không hoàn hảo trong mọi khía cạnh, nhưng tính đúng đắn của nó có thể được nghiên cứu, kiểm thử và xác minh ở những mức độ nhất định. Đầu ra của nó cũng có thể được dự đoán dựa trên đầu vào và các quy tắc đã xác định.

AI tạo sinh hoạt động theo một cơ chế khác. Nó tạo ra kết quả dựa trên các mô hình xác suất được học từ dữ liệu. Một đoạn code trông hợp lý, thậm chí vượt qua một số bài kiểm thử, không đồng nghĩa với việc nó thực sự đúng, an toàn hay phù hợp với kiến trúc hệ thống.

Quan trọng hơn, trước khi viết code, một kỹ sư phần mềm thực thụ phải suy nghĩ về kiến trúc, các bất biến của hệ thống, những ràng buộc nghiệp vụ và các quyết định thiết kế. Code là sự hiện thực hóa những quyết định đó, chứ không phải điểm khởi đầu và kết thúc của quá trình phát triển phần mềm.

Nếu chỉ quan tâm đến việc tạo ra kết quả nhanh nhất có thể mà bỏ qua những nền tảng này, chúng ta có thể tạo ra phần mềm chạy được hôm nay nhưng không thể bảo trì, mở rộng hoặc vận hành an toàn vào ngày mai.

2. Bạn đang nhìn vấn đề từ góc độ của người sử dụng hay người chịu trách nhiệm tạo ra nó?

Một nhạc sĩ có thể lái xe mà không cần hiểu động cơ đốt trong hoạt động như thế nào. Đó không phải vấn đề, bởi trách nhiệm của anh ta không phải là thiết kế hay bảo đảm tính an toàn của chiếc xe.

Nhưng hãy đặt câu hỏi tương tự với một kỹ sư động cơ.

Anh ta có thể thiết kế một động cơ mà không hiểu những gì mình đang làm không? Anh ta có thể bỏ qua một dấu hiệu bất thường vì chiếc xe vẫn đang chạy không?

Tất nhiên là không. Hiểu biết về hệ thống và khả năng nhận diện những bất thường chính là một phần năng lực nghề nghiệp của anh ta.

Kỹ sư phần mềm cũng vậy.

Chúng ta có thể sử dụng những công cụ mà không cần hiểu toàn bộ cơ chế bên trong của chúng. Không ai yêu cầu một kỹ sư phải hiểu mọi dòng code của mọi thư viện mà mình sử dụng. Nhưng có một khác biệt rất lớn giữa việc tin tưởng một thành phần đã được kiểm chứng và việc chấp nhận một đoạn code mới được sinh ra mà không hiểu nó làm gì, tại sao nó hoạt động và khi nào nó có thể thất bại.

Nếu một kỹ sư không thể đánh giá đầu ra của AI, vậy điều gì khiến anh ta đủ năng lực để chịu trách nhiệm cho đầu ra đó?

Và nếu đổi vai, liệu chúng ta có chấp nhận một nhạc sĩ sáng tác bằng AI mà không nghe lại, không đánh giá và không hiểu những gì mình đang đưa đến khán giả?

3. Sai số không biến mất chỉ vì chúng ta phát triển nhanh hơn.

Giả sử một hệ thống AI có xác suất tạo ra một lỗi nghiêm trọng là (p) trong mỗi lần sử dụng.

Nếu 1.000 kỹ sư sử dụng AI một cách cẩu thả, chúng ta nên kỳ vọng điều gì?

Trong một mô hình đơn giản, nếu mỗi lần sử dụng có xác suất phát sinh lỗi độc lập là (p), xác suất có ít nhất một lỗi trong (n) lần sử dụng là:

(P(\text{ít nhất một lỗi}) = 1-(1-p)^n)

Khi số lần sử dụng tăng lên, xác suất xuất hiện ít nhất một lỗi cũng tăng lên. Trong thực tế, rủi ro còn phụ thuộc vào mức độ phức tạp của hệ thống, khả năng phát hiện lỗi, quy trình kiểm thử và mức độ ảnh hưởng của từng lỗi.

Nhưng câu hỏi quan trọng hơn không chỉ là: AI có thể tạo ra bao nhiêu lỗi?

Mà là: Ai sẽ phát hiện chúng? Ai sẽ chịu trách nhiệm khi chúng lọt vào production? Và thiệt hại sẽ là bao nhiêu khi một lỗi ảnh hưởng đến dữ liệu khách hàng, giao dịch tài chính hoặc một hệ thống trọng yếu?

Tốc độ tạo code không đồng nghĩa với tốc độ tạo ra phần mềm đáng tin cậy.

Nếu AI giúp chúng ta viết code nhanh gấp đôi nhưng đồng thời khiến việc xác minh, bảo trì và xử lý sự cố trở nên khó khăn hơn, liệu chúng ta thực sự đã tăng năng suất?

4. AI không xóa bỏ trách nhiệm nghề nghiệp.

Mỗi nghề nghiệp đều có những tiêu chuẩn tương ứng với vai trò và trách nhiệm của nó.

Một kỹ sư không được đánh giá chỉ bằng việc anh ta tạo ra bao nhiêu dòng code, hoàn thành bao nhiêu ticket hay giao sản phẩm nhanh đến mức nào. Giá trị của anh ta còn nằm ở khả năng đưa ra quyết định đúng đắn, hiểu những đánh đổi kỹ thuật, nhận diện rủi ro và bảo đảm rằng sản phẩm có thể vận hành đáng tin cậy trong những điều kiện thực tế.

AI có thể giúp chúng ta làm việc nhanh hơn. Nó có thể giảm bớt những công việc lặp lại, hỗ trợ khám phá giải pháp và mở rộng năng lực của một kỹ sư.

Nhưng sử dụng AI không có nghĩa là chuyển giao trách nhiệm cho AI.

Khi một kỹ sư nhận tiền để xây dựng phần mềm cho khách hàng, khách hàng không chỉ trả tiền cho những dòng code được tạo ra. Họ trả tiền cho năng lực kỹ thuật, những quyết định có cơ sở và trách nhiệm nghề nghiệp đứng sau sản phẩm đó.

Nếu chúng ta lấy tốc độ làm lý do để biện minh cho việc không hiểu những gì mình xây dựng, không kiểm chứng những gì mình triển khai và không chịu trách nhiệm cho những gì mình bàn giao, thì giá trị thực sự của hai chữ kỹ sư nằm ở đâu?

Nếu toàn bộ giá trị được tạo ra bởi các nhà cung cấp AI, còn người đứng giữa chỉ đơn thuần chuyển đầu ra của AI thành hóa đơn gửi khách hàng, vậy đóng góp thực sự của người kỹ sư là gì?

Tôi không cho rằng kỹ sư phần mềm phải hiểu mọi thứ đến tận cùng. Điều đó bất khả thi.

Tôi cho rằng chúng ta cần phân biệt rõ giữa việc không hiểu toàn bộ một hệ thống và việc không hiểu những gì mình đang chịu trách nhiệm.

AI nên là công cụ khuếch đại năng lực của kỹ sư phần mềm, không phải công cụ giúp chúng ta hợp thức hóa sự thiếu hiểu biết.

Bởi cuối cùng, phần mềm không được đánh giá bằng tốc độ mà nó được viết ra. Nó được đánh giá bằng việc nó giải quyết đúng vấn đề, vận hành đáng tin cậy và tiếp tục phục vụ con người trong bao lâu.

Và trách nhiệm bảo đảm những điều đó vẫn thuộc về chúng ta.

> Như Linus Torvalds từng nhấn mạnh, những kỹ sư hiểu hệ thống sẽ biết cách sử dụng AI để tạo ra code tốt; những người không hiểu độ phức tạp của hệ thống vẫn có thể tạo ra code, nhưng kết quả có thể thất “People who know what they’re doing, who understand systems, will be able to prompt tools to write good code. People who don’t understand the complexity of systems will also prompt systems and write code, and it will fail.” ￼

[Xem video đó ở đây](https://youtu.be/fi29pfLcW4I?si=tENi_A9Ihy8K47ko)
