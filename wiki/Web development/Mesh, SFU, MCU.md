---
tags:
  - webrtc
date: 2026-05-29
---
# Mesh, SFU, MCU

Khi số participant của một cuộc gọi WebRTC vượt quá 2, có ba topology truyền media phổ biến, mỗi topology đánh đổi giữa tải client, tải server, latency và linh hoạt layout. Cùng RFC 7667 (RTP Topologies) thống kê chính thức ba mô hình này.

# Mesh — full-mesh P2P

Mỗi participant mở một `RTCPeerConnection` đến tất cả người còn lại; với `n` user có tổng `n*(n-1)/2` cặp connection, mỗi user phải maintain `n-1` connection.

Ưu điểm: không cần media server, latency thấp nhất (đi thẳng), end-to-end encryption tự nhiên vì SRTP nằm giữa hai endpoint. Phù hợp cho 1-1 hoặc 2-3 người.

Nhược điểm: mỗi user phải encode stream của mình một lần nhưng gửi `n-1` lần (upload bandwidth tăng tuyến tính theo số participant). Mobile và mạng yếu thường nghẽn upload ở 3-4 user. CPU cũng tăng vì encoder bị nhiều adaptive bitrate khác nhau với mỗi peer.

# SFU — Selective Forwarding Unit

Mỗi participant chỉ upload một stream lên server; SFU forward các packet RTP đến những peer khác mà không decode hoặc re-encode. Đây là kiến trúc phổ biến nhất hiện nay (Jitsi Videobridge, mediasoup, LiveKit, Janus, Galène, và Kurento ở pattern many-to-many).

Tải server thấp hơn MCU nhiều vì không có transcoding; tải client cao hơn mesh ở chiều download (vẫn nhận `n-1` stream) nhưng upload chỉ một lần — chính việc cố định upload là điểm giải tỏa của SFU. SFU có thể kết hợp **simulcast** (client upload nhiều layer chất lượng khác nhau) hoặc **SVC** (single stream với nhiều lớp scalable) rồi selective forward layer phù hợp bandwidth của từng receiver.

SFU scale tốt đến hàng chục/trăm participant trong một room, là default cho conferencing hiện đại.

# MCU — Multipoint Control Unit

Server decode tất cả stream, mix audio/compose video thành một stream duy nhất rồi encode gửi xuống mỗi client. Client chỉ thấy một incoming stream nên rất nhẹ — phù hợp thiết bị yếu, legacy SIP, telephony bridge.

Đánh đổi rất nặng: server tốn CPU/GPU cực kỳ cao cho transcoding, thêm latency, và layout video bị cố định ở server (client không thể tự sắp lại). Khi cần record cuộc họp thành một file video duy nhất hoặc broadcast composite ra RTMP, MCU lại là lựa chọn tự nhiên.

Trong [Kurento Media Server](./Kurento%20Media%20Server.md), pattern MCU được hiện thực bằng `Composite` hub: mỗi user nối vào một `HubPort`, Composite tự mix/compose, kết quả phát ra qua HubPort khác (xem [MediaPipeline và Endpoint trong Kurento](./MediaPipeline%20v%C3%A0%20Endpoint%20trong%20Kurento.md)).

# Hybrid và quyết định kiến trúc

Một số deployment lai dùng SFU cho room nhỏ và switch sang MCU khi vượt ngưỡng số participant, hoặc dùng MCU chỉ để bridge nhánh SIP/PSTN trong khi SFU lo phần WebRTC.

Quyết định topology phụ thuộc trade-off chính:

- Client yếu, mạng download thấp → MCU.
- Cần layout client-side động → SFU.
- Cần record composite hoặc broadcast → MCU hoặc SFU + recorder riêng.
- 1-1, latency tối thiểu, không muốn maintain server → Mesh.

Khi đã chọn server-mediated (SFU/MCU), cả client vẫn dùng cùng API `RTCPeerConnection` — server side giả lập một peer thông qua server-side endpoint (xem [WebRtcEndpoint](./MediaPipeline%20v%C3%A0%20Endpoint%20trong%20Kurento.md)).

# Nguồn tham khảo

- RFC 7667, *RTP Topologies* — <https://datatracker.ietf.org/doc/html/rfc7667>
- BlogGeek.me, *WebRTC Multiparty Video Alternatives, Explained* — <https://bloggeek.me/webrtc-multiparty-video-alternatives/>
- webrtcHacks, *SFU cascading* — <https://webrtchacks.com/sfu-cascading/>

# Liên kết tri thức

- [WebRTC tổng quan - topology là chọn lựa khi vượt P2P thuần](./WebRTC%20t%E1%BB%95ng%20quan.md)
- [Kurento Media Server - hỗ trợ cả SFU lẫn MCU pattern](./Kurento%20Media%20Server.md)
- [MediaPipeline và Endpoint trong Kurento - hiện thực topology bằng graph media](./MediaPipeline%20v%C3%A0%20Endpoint%20trong%20Kurento.md)
