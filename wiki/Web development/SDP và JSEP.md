---
tags:
  - webrtc
date: 2026-05-29
---
# SDP và JSEP

Session Description Protocol (SDP) là định dạng text mô tả một multimedia session, được WebRTC dùng để trao đổi thông số kết nối media giữa hai peer trước khi thiết lập đường truyền. JSEP (JavaScript Session Establishment Protocol, RFC 8829) là mô hình WebRTC áp dụng SDP từ JavaScript, định nghĩa state machine và API để application layer điều khiển negotiation mà không bị spec ép.

# Nội dung một SDP của WebRTC

Một SDP WebRTC điển hình chứa:

- Danh sách codec và **payload type** cùng các thuộc tính (sample rate, channel) trong các attribute `a=rtpmap`.
- IP/port transport được mô tả ở connection và media line, dù thực tế WebRTC dùng ICE candidate riêng nên giá trị này có thể là placeholder.
- **DTLS fingerprint** (`a=fingerprint`) để bên kia verify identity khi thực hiện DTLS handshake, chống Man-in-the-Middle vì signaling không nhất thiết tin cậy.
- **ICE ufrag và pwd** (`a=ice-ufrag`, `a=ice-pwd`) làm credentials cho ICE connectivity check.
- Các **m-line** (media section) mô tả từng audio/video/data stream cùng direction `sendrecv`, `sendonly`, `recvonly`, `inactive`.

Khi dùng [Kurento Media Server](./Kurento%20Media%20Server.md), SDP do client tạo được gửi server side qua signaling, server gọi `processOffer` trên WebRtcEndpoint để Kurento sinh answer SDP tương ứng.

# Offer/Answer model

Mô hình nền tảng là RFC 3264: một bên là offerer đề xuất các media stream với khả năng của mình, bên còn lại là answerer chọn subset chấp nhận được. JSEP bổ sung cho WebRTC khả năng **rollback** (hủy half-applied description khi negotiation chéo) và **provisional answer** (PRAnswer) cho các tình huống cần thiết lập tạm.

Flow chuẩn cho một cuộc gọi:

1. Caller `createOffer()` → `setLocalDescription(offer)`.
2. Gửi offer qua [signaling](./Signaling%20trong%20WebRTC.md).
3. Callee `setRemoteDescription(offer)` → `createAnswer()` → `setLocalDescription(answer)`.
4. Gửi answer ngược lại qua signaling.
5. Caller `setRemoteDescription(answer)`.

Sau bước 5, cả hai phía đã đồng ý codec và transport; ICE bắt đầu connectivity check để chọn đường media thực (xem [ICE, STUN, TURN](./ICE%2C%20STUN%2C%20TURN.md)).

# Vì sao tách SDP control ra application layer

JSEP cố ý đặt mọi quyết định negotiation ở JavaScript thay vì để browser tự động. Lợi ích: ứng dụng có thể manipulate SDP (gọi là "SDP munging") để bật/tắt codec cụ thể, ép bitrate, đổi simulcast layer, hoặc xen tham số thử nghiệm. Spec khuyến nghị hạn chế munging và dùng RTCRtpSender/Transceiver API thay thế, nhưng cho đến nay munging vẫn là practice phổ biến để work-around browser limitations.

Tách như vậy cũng cho phép server-side endpoint như WebRtcEndpoint của Kurento tham gia negotiation: server hành xử như một peer, sinh ra SDP answer thật sự thay vì phải tin tưởng client tự chọn — quan trọng khi media phải đi qua server thay vì P2P.

# Quan hệ với SIP và VoIP

SDP có nguồn gốc từ thế giới VoIP (dùng cùng SIP từ RFC 3261). WebRTC kế thừa SDP để dễ interop với hạ tầng SIP cũ qua gateway: media server có thể có một endpoint WebRTC (kết nối browser) và một endpoint SIP/RTP (kết nối PBX), nối hai endpoint qua một MediaPipeline (xem [MediaPipeline và Endpoint trong Kurento](./MediaPipeline%20v%C3%A0%20Endpoint%20trong%20Kurento.md)).

# Nguồn tham khảo

- RFC 8829, *JSEP: JavaScript Session Establishment Protocol* — <https://datatracker.ietf.org/doc/html/rfc8829>
- RFC 3264, *An Offer/Answer Model with SDP* — <https://datatracker.ietf.org/doc/html/rfc3264>
- RFC 8866, *SDP: Session Description Protocol* — <https://datatracker.ietf.org/doc/html/rfc8866>

# Liên kết tri thức

- [WebRTC tổng quan - SDP là contract giữa hai peer](./WebRTC%20t%E1%BB%95ng%20quan.md)
- [Signaling trong WebRTC - SDP được vận chuyển qua signaling](./Signaling%20trong%20WebRTC.md)
- [ICE, STUN, TURN - candidate được trao đổi song song SDP](./ICE%2C%20STUN%2C%20TURN.md)
- [WebRtcEndpoint xử lý SDP và ICE qua Kurento](./MediaPipeline%20v%C3%A0%20Endpoint%20trong%20Kurento.md)
