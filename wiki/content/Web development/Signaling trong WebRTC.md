---
tags:
  - webrtc
  - web
date: 2026-05-29
---
# Signaling trong WebRTC

Signaling là kênh trao đổi metadata (SDP và ICE candidate) giữa hai peer trước và trong khi thiết lập kết nối WebRTC. Spec WebRTC cố ý không chuẩn hóa signaling — developer được tự do chọn transport và protocol — vì mỗi ứng dụng có nhu cầu khác nhau (web chat, telephony, IoT, gaming) và việc fix một protocol sẽ giới hạn use case, đồng thời khó tương thích với các hệ thống cũ như SIP/XMPP.

# Vai trò của signaling server

Signaling server hoạt động như trung gian "mù": chỉ relay message giữa các peer mà không cần hiểu nội dung media. Hai nội dung chính được relay là **SDP offer/answer** (xem [SDP và JSEP](./SDP%20v%C3%A0%20JSEP.md)) và **ICE candidate** trickle (xem [ICE, STUN, TURN](./ICE%2C%20STUN%2C%20TURN.md)).

Ngoài relay, signaling layer thường đảm nhiệm presence và discovery (ai online), room/session management (ai thuộc cuộc gọi nào), authentication, và lifecycle event như join/leave/hang-up. Khi có media server làm trung gian (xem [Kurento Media Server](./Kurento%20Media%20Server.md)), signaling còn cầu nối giữa client và media server: chuyển offer/answer giữa client và server-side endpoint.

# Pattern transport phổ biến

**WebSocket** là lựa chọn phổ biến nhất nhờ tính persistent, bidirectional, low-latency, mở được từ browser sang server không qua HTTP polling. Đây là transport chuẩn cho cả Kurento Protocol khi server ↔ media server.

**Socket.IO** là abstraction trên WebSocket với fallback long-polling, room, namespace, broadcast và auto-reconnect — phù hợp khi cần room semantics nhanh để gom các peer cùng cuộc gọi. Trong [webrtc-backend](../../references/repos/webrtc-backend/app/socket.py), `ControllerNamespace` dùng Socket.IO room `data['name']` để gom các participant của một cuộc gọi và relay event `icandidate` cho cả phòng trừ chính sender (`include_self=False`).

**SIP** dùng cho VoIP doanh nghiệp và interop với PSTN; WebRTC client có thể "gọi" lên hạ tầng SIP qua signaling gateway.

# Thứ tự message ràng buộc state machine

MDN khuyến cáo: `addIceCandidate()` chỉ nên gọi sau khi `setRemoteDescription()` đã thành công, nếu không peer connection sẽ lỗi state machine. Tương tự, không gửi answer trước khi processOffer hoàn tất ở phía nhận. Khi thiết kế signaling, cần buffer các candidate đến sớm hoặc đảm bảo thứ tự event qua một single channel ordered.

Đây cũng là lý do trickle ICE chuẩn (RFC 8838) tách candidate khỏi SDP gốc và stream từng cái qua signaling: rút ngắn call setup latency mà vẫn tôn trọng thứ tự.

# Pattern phòng họp trong webrtc-backend

Implementation tham khảo trong [socket.py](../../references/repos/webrtc-backend/app/socket.py):

`on_connect` đặt mỗi user vào một `join_room(sid)` riêng để có kênh unicast trực tiếp tới user đó qua session id của Socket.IO.

`on_create_room` lưu room với `name`, `author`, và mảng `sdp` (lưu offer của người tạo). Mọi user khác emit `create_room` đều nhận lại danh sách phòng qua event `room`.

`on_join_room` tìm room theo tên, `join_room(name)` rồi emit `join_room` chỉ cho các thành viên khác (`include_self=False`) kèm theo `sdp` đã lưu — đây là cách backend đẩy offer của presenter xuống cho viewer mới vào.

`on_icandidate` broadcast ICE candidate cho cả phòng trừ sender — đây là trickle ICE qua Socket.IO.

# Nguồn tham khảo

- MDN, *Signaling and video calling* — <https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling>
- RFC 8825 §2.3, *Signaling* — <https://datatracker.ietf.org/doc/html/rfc8825>
- Source code tham khảo: [app/socket.py](../../references/repos/webrtc-backend/app/socket.py)

# Liên kết tri thức

- [WebRTC tổng quan - signaling là một trong hai mặt phẳng cốt lõi](./WebRTC%20t%E1%BB%95ng%20quan.md)
- [SDP và JSEP - nội dung được signaling vận chuyển](./SDP%20v%C3%A0%20JSEP.md)
- [ICE, STUN, TURN - candidate được trickle qua signaling](./ICE%2C%20STUN%2C%20TURN.md)
- [Kurento Protocol - kênh signaling thứ hai giữa backend và media server](./Kurento%20Protocol.md)
