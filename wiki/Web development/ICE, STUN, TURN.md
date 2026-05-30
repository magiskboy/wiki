---
tags:
  - webrtc
date: 2026-05-29
---
# ICE, STUN, TURN

Đa số client WebRTC nằm sau NAT hoặc firewall nên không có public address để peer kia kết nối trực tiếp. **ICE** (Interactive Connectivity Establishment, RFC 8445) là framework tự động dò đường khả thi giữa hai endpoint bằng cách gather candidate từ nhiều nguồn rồi kiểm tra connectivity từng pair. **STUN** và **TURN** là hai server hỗ trợ ICE: STUN giúp client tự biết public address của mình, TURN làm relay cuối khi không có cách nào thiết lập đường trực tiếp.

# Bốn loại ICE candidate

**Host** — IP nội bộ của một network interface, lấy được trực tiếp từ OS. Phù hợp khi hai peer ở cùng LAN.

**Server-reflexive (srflx)** — public IP và port mà NAT cấp cho client, phát hiện bằng cách gửi STUN Binding Request đến STUN server và đọc XOR-MAPPED-ADDRESS trong response. Đây là kết quả "ngoài Internet nhìn tôi như thế nào".

**Peer-reflexive (prflx)** — phát sinh khi connectivity check tới một candidate khác, NAT mở port mới, peer kia thấy địa chỉ chưa biết trước đó. Candidate này được học trong quá trình check.

**Relay** — địa chỉ trên TURN server, mọi packet đi qua TURN; được dùng làm fallback khi mọi cách khác thất bại.

# STUN — RFC 8489

STUN là protocol nhẹ, hoạt động trên UDP (cũng có TCP/TLS). Client gửi Binding Request, server phản hồi với địa chỉ nguồn nhìn từ ngoài. STUN không truyền media, chỉ giúp khám phá NAT mapping; bandwidth và state ở STUN server gần như không đáng kể, nên có rất nhiều STUN public free (Google, Cloudflare).

STUN một mình đủ cho trường hợp NAT cone-style cho phép hole-punching: hai bên cùng biết srflx của nhau và cùng gửi packet đồng thời, NAT mở pinhole cho cả hai chiều.

# TURN — RFC 8656

Khi cả hai phía dùng symmetric NAT, mỗi destination IP nhận được mapping khác nhau, hole-punching thất bại. Lúc này TURN phải vào cuộc: TURN server cấp một relay address cho client, mọi packet client gửi đi đều tunnel qua relay rồi mới đến peer; ngược chiều, peer gửi tới relay rồi mới đến client.

TURN tốn bandwidth (mọi byte media phải đi qua server) và chi phí vận hành cao (không thể dùng public free vì bị abuse), nên chỉ làm fallback cuối — thực tế thường 10-20% session phải dùng TURN tùy môi trường mạng.

# Connectivity check và lựa chọn cặp

ICE pair các candidate của hai bên (host-host, srflx-srflx, srflx-relay,...) và sort theo priority. Mỗi pair được test bằng STUN check 4-way (request/response cả hai hướng). Pair thành công đầu tiên với priority cao nhất được nominate làm đường media; các pair khác bị giữ làm dự phòng để có thể chuyển nếu đường hiện tại fail (ICE restart hoặc consent freshness).

# Trickle ICE — RFC 8838

ICE gathering có thể tốn vài trăm ms tới vài giây (phải truy vấn STUN, TURN). Nếu chờ gather xong toàn bộ candidate mới gửi SDP, call setup latency rất cao. **Trickle ICE** giải quyết bằng cách gửi SDP với danh sách candidate ban đầu (thường rỗng hoặc chỉ host), sau đó trickle từng candidate qua [signaling](./Signaling%20trong%20WebRTC.md) ngay khi phát hiện, song song với connectivity check.

Điều này giảm đáng kể call setup latency và là default trong WebRTC hiện đại. Implementation tham khảo trong [webrtc-backend/app/socket.py](../../references/repos/webrtc-backend/app/socket.py) dùng event Socket.IO `icandidate` để broadcast ICE candidate cho cả phòng trừ sender, đúng tinh thần trickle.

# Cấu hình cho server-side endpoint

Khi media chạy qua server (xem [Kurento Media Server](./Kurento%20Media%20Server.md)), bản thân server cũng cần ICE để xuyên NAT. Kurento config STUN/TURN trong `/etc/kurento/WebRtcEndpoint.conf.ini` để WebRtcEndpoint có thể gather srflx/relay candidate phía server, sau đó gửi xuống client qua signaling.

# Nguồn tham khảo

- RFC 8445, *Interactive Connectivity Establishment (ICE)* — <https://datatracker.ietf.org/doc/html/rfc8445>
- RFC 8489, *Session Traversal Utilities for NAT (STUN)* — <https://datatracker.ietf.org/doc/html/rfc8489>
- RFC 8656, *Traversal Using Relays around NAT (TURN)* — <https://datatracker.ietf.org/doc/html/rfc8656>
- RFC 8838, *Trickle ICE* — <https://datatracker.ietf.org/doc/html/rfc8838>

# Liên kết tri thức

- [WebRTC tổng quan - ICE là một mảnh ghép của media plane](./WebRTC%20t%E1%BB%95ng%20quan.md)
- [Signaling trong WebRTC - candidate được trickle qua signaling](./Signaling%20trong%20WebRTC.md)
- [SDP và JSEP - SDP chứa ICE ufrag/pwd làm credentials](./SDP%20v%C3%A0%20JSEP.md)
- [Kurento Media Server - cấu hình STUN/TURN cho server endpoint](./Kurento%20Media%20Server.md)
