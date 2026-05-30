---
tags:
  - webrtc
date: 2026-05-29
---
# WebRTC tổng quan

WebRTC là bộ giao thức và API cho phép real-time communication audio, video, data trực tiếp giữa hai endpoint (thường là browser) mà không cần plugin. Kiến trúc WebRTC tách rõ hai mặt phẳng: **signaling plane** đi qua application server do developer tự chọn cơ chế (xem [Signaling trong WebRTC](./Signaling%20trong%20WebRTC.md)) và **media plane** đi trực tiếp giữa các peer, bắt buộc tuân thủ chuẩn WebRTC để đảm bảo interoperability cross-browser.

# Ba API JavaScript chính

`RTCPeerConnection` quản lý lifecycle của một kết nối peer-to-peer: negotiation SDP, gather ICE candidate, gửi/nhận track media, theo dõi connection state. Đây là object trung tâm mà mọi ứng dụng WebRTC tương tác.

`MediaStream` và `MediaStreamTrack` đại diện cho stream media gồm nhiều track audio/video. Stream lấy được từ thiết bị qua `getUserMedia()`, từ màn hình qua `getDisplayMedia()`, hoặc từ một peer connection từ xa qua sự kiện `ontrack`.

`RTCDataChannel` truyền dữ liệu tùy ý song song với media trên cùng peer connection, hoạt động trên SCTP-over-DTLS, hỗ trợ cả reliable/ordered và unreliable/unordered tương tự UDP — phù hợp game, file transfer, telemetry.

# Stack giao thức trên media plane

UDP làm transport layer vì độ trễ thấp và chịu được packet loss tốt hơn TCP cho audio/video. Trên UDP có ICE (xem [ICE, STUN, TURN](./ICE%2C%20STUN%2C%20TURN.md)) chịu trách nhiệm NAT traversal, DTLS thực hiện key exchange và bảo mật transport, SRTP mã hóa media RTP packet, và SCTP-over-DTLS cho data channel.

Cả ba lớp DTLS, SRTP, SCTP là bắt buộc trong WebRTC — mọi traffic phải được mã hóa, không có chế độ plaintext. Fingerprint của DTLS certificate được trao đổi qua SDP để chống MitM, vì signaling không nhất thiết tin cậy.

# Codec bắt buộc

RFC 8825 yêu cầu baseline codec để tránh negotiation failure giữa hai endpoint không biết nhau từ trước:

Audio bắt buộc Opus (interactive, wideband, dải bitrate rộng) và G.711 PCMU/PCMA (legacy, interop với PSTN/SIP). Video bắt buộc VP8 và H.264 Constrained Baseline. Browser được phép thêm codec khác (VP9, AV1, H.265) nhưng phải support được baseline.

# Mục tiêu thiết kế

WebRTC ưu tiên low-latency real-time, secure-by-default (encryption bắt buộc), và cross-browser interoperability. Spec cố ý để mở phần signaling và room management vì các tổ chức có nhu cầu khác nhau — từ web meeting đến VoIP doanh nghiệp tới IoT — fix một protocol sẽ giới hạn use case.

Khi số participant tăng, mô hình P2P thuần không scale; lúc này cần đến media server đứng giữa để forward hoặc mix (xem [Mesh, SFU, MCU](./Mesh%2C%20SFU%2C%20MCU.md), [Kurento Media Server](./Kurento%20Media%20Server.md)).

# Nguồn tham khảo

- RFC 8825, *Overview: Real-Time Protocols for Browser-Based Applications* — <https://datatracker.ietf.org/doc/html/rfc8825>
- W3C, *WebRTC: Real-Time Communication in Browsers* — <https://www.w3.org/TR/webrtc/>
- MDN, *WebRTC API* — <https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API>

# Liên kết tri thức

- [Signaling trong WebRTC - kênh trao đổi metadata để thiết lập peer connection](./Signaling%20trong%20WebRTC.md)
- [SDP và JSEP - định dạng mô tả session media trong WebRTC](./SDP%20v%C3%A0%20JSEP.md)
- [ICE, STUN, TURN - NAT traversal cho media plane](./ICE%2C%20STUN%2C%20TURN.md)
- [Mesh, SFU, MCU - các topology multi-party](./Mesh%2C%20SFU%2C%20MCU.md)
- [Kurento Media Server - media server xử lý WebRTC phía server](./Kurento%20Media%20Server.md)
