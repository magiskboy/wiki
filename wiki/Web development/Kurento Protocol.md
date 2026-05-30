---
tags:
  - webrtc
  - web
date: 2026-05-29
---
# Kurento Protocol

Kurento Protocol (KMP) là JSON-RPC 2.0 chạy trên WebSocket, dùng để điều khiển [Kurento Media Server](./Kurento%20Media%20Server.md) từ application backend. Endpoint mặc định là `ws://hostname:port/kurento` (port 8888 trong cấu hình mặc định, đổi sang `wss://` khi triển khai có TLS).

# Format request và response

Mọi request có 4 field bắt buộc: `jsonrpc: "2.0"`, `id` (số tự tăng để correlate response), `method`, `params`. Response thành công trả `jsonrpc`, `id` khớp request, và `result` (chứa `value` và thường kèm `sessionId`). Response lỗi trả object `error` với `code`, `message`, `data`.

Server gán `sessionId` ở response đầu tiên; client phải kèm `sessionId` này vào mọi request tiếp theo để Kurento biết MediaObject thuộc về session nào. Mất kết nối quá lâu mà không reconnect, các MediaObject của session đó sẽ bị garbage collect.

Ví dụ payload create MediaPipeline từ [app/kurento_client.py](../../references/repos/webrtc-backend/app/kurento_client.py:88) đúng spec:

```json
{
  "id": 2,
  "method": "create",
  "params": {
    "type": "MediaPipeline",
    "constructorParams": {},
    "properties": {}
  },
  "jsonrpc": "2.0"
}
```

Sau khi nhận response chứa `sessionId`, mọi request tiếp theo (như `create WebRtcEndpoint`) phải kèm cùng `sessionId`.

# Sáu method client gửi server

`ping` — heartbeat giữ session sống. Params `{interval}` tính bằng millisecond, default 240000 (4 phút). Server trả `{"value": "pong"}`. Kurento sẽ GC resource nếu không nhận ping/request trong khoảng interval đó.

`create` — tạo MediaObject mới. Params gồm `type` (tên class như `MediaPipeline`, `WebRtcEndpoint`, `RecorderEndpoint`,...), `constructorParams` (tham số constructor, thường có `mediaPipeline` reference tới pipeline cha với các MediaElement), `properties`, và `sessionId` (trừ lần `create MediaPipeline` đầu tiên có thể chưa có).

`invoke` — gọi method trên một MediaObject đã có. Params gồm `object` (id của MediaObject), `operation` (tên method, ví dụ `processOffer`, `addIceCandidate`, `gatherCandidates`, `connect`), `operationParams` (tham số), và `sessionId`. Đây là method quan trọng nhất khi vận hành WebRtcEndpoint.

`subscribe` — đăng ký nhận event từ một MediaObject. Params gồm `object`, `type` (loại event, ví dụ `IceCandidateFound`, `MediaStateChanged`), và `sessionId`. Server trả `subscription` id để dùng khi unsubscribe.

`unsubscribe` — hủy đăng ký event. Params gồm `subscription` id và `sessionId`.

`release` — giải phóng một MediaObject, dọn resource. Params gồm `object` và `sessionId`. Khi giải phóng MediaPipeline, mọi element bên trong cũng tự release theo. Cài đặt trong [kurento_client.py:125](../../references/repos/webrtc-backend/app/kurento_client.py:125) đúng spec.

# Event server gửi client

Server gửi notification `onEvent` (JSON-RPC notification, không có `id` vì là one-way) khi event subscribed bắn ra. Body chứa `params` với `value` mô tả event và `subscription` để client biết event thuộc subscription nào.

Event `IceCandidateFound` là điển hình: mỗi khi Kurento gather được candidate ICE phía server, sự kiện được bắn về backend; backend forward candidate cho client qua [signaling WebRTC](./Signaling%20trong%20WebRTC.md) để client `addIceCandidate()`.

# So sánh với signaling WebRTC application

KMP và signaling client ↔ application là hai kênh khác nhau:

- Signaling client ↔ application (thường WebSocket/Socket.IO) vận chuyển SDP và ICE giữa browser và backend.
- KMP application ↔ Kurento (WebSocket JSON-RPC) điều khiển media server.

Backend đóng vai trò bridge giữa hai kênh: nhận SDP offer từ client, gọi `invoke processOffer` lên Kurento, lấy answer trả về client; nhận ICE candidate client gửi lên, gọi `invoke addIceCandidate`; subscribe `IceCandidateFound` để forward candidate server xuống client.

Implementation [KurentoClient](../../references/repos/webrtc-backend/app/kurento_client.py) mới có `ping`, `create`, `release`; còn thiếu `invoke` (processOffer/addIceCandidate/gatherCandidates) và `subscribe` (IceCandidateFound) — đây là các method bắt buộc để hoàn thành SDP/ICE flow thực tế, không chỉ tạo endpoint là đủ.

# Nguồn tham khảo

- Kurento Protocol — <https://doc-kurento.readthedocs.io/en/latest/features/kurento_protocol.html>
- JSON-RPC 2.0 Specification — <https://www.jsonrpc.org/specification>
- Source code tham khảo: [app/kurento_client.py](../../references/repos/webrtc-backend/app/kurento_client.py)

# Liên kết tri thức

- [Kurento Media Server - tổng quan media server mà KMP điều khiển](./Kurento%20Media%20Server.md)
- [MediaPipeline và Endpoint trong Kurento - các MediaObject mà KMP create/invoke](./MediaPipeline%20v%C3%A0%20Endpoint%20trong%20Kurento.md)
- [Signaling trong WebRTC - kênh signaling client phối hợp với KMP qua backend](./Signaling%20trong%20WebRTC.md)
