---
tags:
  - webrtc
date: 2026-05-29
---
# Kurento Media Server

Kurento Media Server (KMS) là WebRTC media server mã nguồn mở (Apache License 2.0) xây dựng trên nền GStreamer, chuyên truyền tải, xử lý, transcode và record media stream. Khác với các pure SFU như Jitsi Videobridge, Janus hay mediasoup vốn tối ưu cho forward stream không xử lý, Kurento là media server đa năng: vừa làm SFU, vừa làm MCU (qua `Composite` hub), vừa hỗ trợ computer vision và AR filter (OpenCV-based), recording WebM/MP4, transcoding tự động giữa VP8/H.264/Opus, và làm gateway giữa WebRTC với RTP/SIP/RTSP.

# Lịch sử và quan hệ với OpenVidu

Project khởi xướng tại Universidad Rey Juan Carlos (URJC, Madrid), thương mại hóa qua spin-off Kurento Technologies/Tikal Technologies, được Twilio mua năm 2016. Twilio giữ core team nhưng dừng phát triển open-source phiên bản đó nên project trải qua giai đoạn đình trệ. Sau đó team OpenVidu (công ty Naevatec, cũng do các founder gốc của Kurento sáng lập) tiếp quản và tiếp tục maintain; phiên bản stable hiện tại là Kurento 7.x.

OpenVidu là một layer high-level hơn xây trên Kurento, cung cấp room management, SDK client, và một số tính năng video-conferencing sẵn dùng; còn Kurento vẫn là media engine bên dưới.

# Vị trí trong stack WebRTC

Kurento đóng vai trò một peer phía server: client mở `RTCPeerConnection` tới Kurento qua [signaling](./Signaling%20trong%20WebRTC.md) của application backend, trao đổi [SDP và ICE](./SDP%20v%C3%A0%20JSEP.md) như với một peer thường. Khác biệt là Kurento có khả năng xử lý media giữa các peer thay vì chỉ truyền thụ động, nhờ vậy hỗ trợ cả các topology [SFU và MCU](./Mesh%2C%20SFU%2C%20MCU.md) cũng như pipeline filter trung gian.

Application backend giao tiếp với Kurento qua [Kurento Protocol](./Kurento%20Protocol.md) (JSON-RPC 2.0 trên WebSocket) để tạo và điều khiển các [MediaPipeline và endpoint](./MediaPipeline%20v%C3%A0%20Endpoint%20trong%20Kurento.md).

# So sánh với các media server khác

Các SFU thuần (Jitsi Videobridge, mediasoup, LiveKit) chỉ làm nhiệm vụ forward RTP nên tối ưu hơn về CPU và scale tốt hơn cho conferencing thuần. Kurento đánh đổi performance để có flexibility: cùng một deployment có thể xử lý vision (FaceOverlayFilter, ZBarFilter cho QR), record ra disk, hoặc bridge sang nhánh SIP — không cần đứng thêm component khác.

Khi nhu cầu chỉ là conferencing scale lớn, các SFU thuần thường hợp hơn. Khi nhu cầu là media processing đa dạng (camera AI, computer vision, recording composite, telephony gateway), Kurento là lựa chọn tự nhiên.

# Cấu hình mạng

Khi triển khai sau NAT, Kurento phải biết public IP và có thể truy cập STUN/TURN để gather [ICE candidate](./ICE%2C%20STUN%2C%20TURN.md) cho server-side `WebRtcEndpoint`. Cấu hình nằm ở `/etc/kurento/WebRtcEndpoint.conf.ini` (STUN address/port, TURN URL với credentials, network interface).

Trong [webrtc-backend](../../references/repos/webrtc-backend/app/kurento_client.py), `KurentoClient` mặc định kết nối `ws://localhost:8888/kurento`, ngụ ý Kurento chạy cùng host với application backend qua loopback; deployment production thường tách host và đổi sang `wss://` với TLS.

# Nguồn tham khảo

- Kurento Documentation — <https://doc-kurento.readthedocs.io/en/latest/>
- Kurento và OpenVidu — <https://doc-kurento.readthedocs.io/en/latest/user/openvidu.html>
- GitHub Kurento/kurento — <https://github.com/Kurento/kurento>
- Source code tham khảo: [app/kurento_client.py](../../references/repos/webrtc-backend/app/kurento_client.py)

# Liên kết tri thức

- [WebRTC tổng quan - Kurento là peer phía server trong WebRTC](./WebRTC%20t%E1%BB%95ng%20quan.md)
- [Kurento Protocol - kênh điều khiển Kurento từ backend](./Kurento%20Protocol.md)
- [MediaPipeline và Endpoint trong Kurento - graph media của Kurento](./MediaPipeline%20v%C3%A0%20Endpoint%20trong%20Kurento.md)
- [Mesh, SFU, MCU - Kurento hiện thực cả hai pattern SFU và MCU](./Mesh%2C%20SFU%2C%20MCU.md)
- [ICE, STUN, TURN - server-side endpoint cũng cần NAT traversal](./ICE%2C%20STUN%2C%20TURN.md)
