---
tags:
  - webrtc
date: 2026-05-29
---
# MediaPipeline và Endpoint trong Kurento

Kiến trúc media của [Kurento Media Server](./Kurento%20Media%20Server.md) tổ chức theo một directed graph các MediaObject. `MediaObject` là base class, `MediaPipeline` là container chứa toàn bộ element của một phiên xử lý media (mỗi pipeline cô lập về resource và threading), và `MediaElement` là các node xử lý cụ thể nằm trong pipeline.

# Ba nhóm MediaElement

**Endpoint** — input/output ra ngoài pipeline: `WebRtcEndpoint` (nối browser qua WebRTC), `RtpEndpoint` (RTP/SDP cho SIP/legacy), `RecorderEndpoint` (ghi ra file WebM/MP4), `PlayerEndpoint` (đọc từ file hoặc URL làm nguồn), `HttpPostEndpoint` (nhận POST HTTP).

**Filter** — xử lý nội dung media: `FaceOverlayFilter` (overlay khuôn mặt phát hiện được), `ZBarFilter` (đọc QR/barcode), `GStreamerFilter` (chèn pipeline GStreamer tùy ý).

**Hub** — multiplexing nhiều stream: `Composite` (mix audio và compose video grid theo pattern MCU), `Dispatcher` (chuyển active stream), `DispatcherOneToMany` (broadcast 1 → N).

# Source pad, sink pad và connect

Mỗi element có **source pad** (cổng phát stream ra) và **sink pad** (cổng nhận stream vào). Method `connect()` nối source pad của element A vào sink pad của element B, tạo luồng media một chiều. Để có giao tiếp 2 chiều giữa hai `WebRtcEndpoint`, phải connect chéo cả hai hướng: `A.connect(B)` và `B.connect(A)`.

Có thể chèn filter ở giữa, ví dụ chuỗi `webRtc.connect(faceOverlay); faceOverlay.connect(webRtc)` thực hiện loopback đồng thời overlay khuôn mặt: client thấy chính mình với mặt được phủ icon.

# Pattern multi-party qua MediaPipeline

Tất cả các pattern đều dùng chung primitive: tạo một MediaPipeline, tạo N WebRtcEndpoint trong pipeline đó, rồi `connect()` chéo theo topology mong muốn.

**One-to-one (videocall)** — 1 MediaPipeline, 2 WebRtcEndpoint A và B, connect chéo `A.connect(B)` và `B.connect(A)`. Đơn giản nhất, không transcode nếu codec match.

**One-to-many (broadcast)** — 1 presenter WebRtcEndpoint, N viewer WebRtcEndpoint; chỉ connect một chiều `presenter.connect(viewer_i)` cho từng viewer. Kurento forward cùng một stream của presenter ra N nhánh, viewer không phát ngược lại. Scale tốt vì viewer chỉ recv.

**Many-to-many (group call, SFU-style)** — N user, mỗi user một WebRtcEndpoint riêng, các endpoint connect chéo nhau. Đây là kiến trúc [SFU](./Mesh%2C%20SFU%2C%20MCU.md) thuần: Kurento forward không transcode, mỗi client decode `N-1` stream. Tutorial `kurento-group-call` minh họa pattern này.

**Composite (MCU)** — dùng `Composite` hub, mỗi user nối vào một `HubPort` của Composite (`webRtc.connect(hubPort)` và `hubPort.connect(webRtc)`). Composite tự mix audio và compose video grid, encode lại thành một stream duy nhất gửi xuống mỗi client. Tốn CPU server, tiết kiệm bandwidth client, phù hợp endpoint yếu hoặc gateway SIP.

# Flow xử lý một WebRtcEndpoint

`WebRtcEndpoint` là MediaElement đại diện cho một WebRTC peer phía server, tự động xử lý DTLS-SRTP, ICE (qua libnice), và codec negotiation. Flow chuẩn cho mỗi client:

1. Client tạo SDP offer bằng `RTCPeerConnection.createOffer()`, gửi qua [signaling](./Signaling%20trong%20WebRTC.md) lên backend.
2. Backend gọi `invoke processOffer` qua [Kurento Protocol](./Kurento%20Protocol.md) trên WebRtcEndpoint id, nhận SDP answer trong `result.value`, forward về client; client `setRemoteDescription()`.
3. Backend `subscribe IceCandidateFound` trên endpoint — mỗi khi Kurento gather được candidate nội bộ sẽ bắn `onEvent` về backend, backend forward cho client.
4. Backend gọi `invoke gatherCandidates` (không có operationParams) để Kurento bắt đầu ICE gathering. Bước này phải gọi **sau** `processOffer` để session đã được khởi tạo.
5. Khi client tìm ra ICE candidate của nó, gửi qua signaling; backend gọi `invoke addIceCandidate` với `operationParams: {candidate: {candidate, sdpMid, sdpMLineIndex}}`.

Khi cả hai phía đã trao đổi xong SDP và đủ candidate, ICE thiết lập DTLS-SRTP và media bắt đầu chảy. Implementation trong [webrtc-backend](../../references/repos/webrtc-backend/app/kurento_client.py) mới hiện thực bước tạo MediaPipeline và WebRtcEndpoint qua `create`; các bước `invoke` và `subscribe` chưa có, cần bổ sung mới chạy được flow đầy đủ.

# Cô lập resource theo pipeline

Mỗi MediaPipeline có thread riêng và resource riêng. Hai cuộc gọi khác nhau nên đặt trong hai pipeline khác nhau để cô lập sự cố (một pipeline crash không ảnh hưởng pipeline khác) và để garbage collection chính xác — `release` MediaPipeline tự release mọi MediaElement bên trong.

Đây là một cài đặt cụ thể của nguyên tắc [cấp resource ở đâu, giải phóng ở đó](../System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md): pipeline đóng vai trò cấp resource ngoài cùng, mọi element bên trong sống và chết theo pipeline.

# Nguồn tham khảo

- Kurento Modules — MediaPipeline, MediaElement, Endpoint, Filter, Hub — <https://doc-kurento.readthedocs.io/en/latest/features/kurento_modules.html>
- Kurento Tutorials — <https://doc-kurento.readthedocs.io/en/latest/user/tutorials.html>
- GitHub Kurento/kurento-tutorial-node — <https://github.com/Kurento/kurento-tutorial-node>
- Source code tham khảo: [app/kurento_client.py](../../references/repos/webrtc-backend/app/kurento_client.py)

# Liên kết tri thức

- [Kurento Media Server - tổng quan media server và vị trí trong stack](./Kurento%20Media%20Server.md)
- [Kurento Protocol - kênh điều khiển tạo và invoke các MediaObject](./Kurento%20Protocol.md)
- [Mesh, SFU, MCU - các topology được hiện thực qua connect và Composite](./Mesh%2C%20SFU%2C%20MCU.md)
- [SDP và JSEP - WebRtcEndpoint sinh SDP answer qua processOffer](./SDP%20v%C3%A0%20JSEP.md)
- [ICE, STUN, TURN - server-side gather candidate qua gatherCandidates](./ICE%2C%20STUN%2C%20TURN.md)
- [Cấp resource ở đâu, giải phóng ở đó - pipeline là unit cô lập resource](../System%20level/C%E1%BA%A5p%20resource%20%E1%BB%9F%20%C4%91%C3%A2u%2C%20gi%E1%BA%A3i%20ph%C3%B3ng%20%E1%BB%9F%20%C4%91%C3%B3.md)
