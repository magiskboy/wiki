---
tags:
  - infrastructure
date: 2026-05-29
---
# Service mesh làm tầng quan sát

Service mesh (Linkerd, Istio) thường được giới thiệu qua góc bảo mật — mTLS giữa pod — hoặc traffic management — canary, retry, timeout. Nhưng một lợi điểm ít được nói tới mà giá trị thường lớn nhất là observability: proxy sidecar tự export "golden metrics" (RPS, success rate, latency) cho mọi connection HTTP/gRPC nó proxy, không cần code instrument. Với cluster có nhiều service legacy không có metric, lắp service mesh là cách rẻ nhất để có dashboard reliability đầy đủ.

Nguồn: [Linkerd Proxy Metrics — linkerd.io](https://linkerd.io/2.16/reference/proxy-metrics/), [Golden Signals — Google SRE Book](https://sre.google/sre-book/monitoring-distributed-systems/#xref_monitoring_golden-signals).

## Golden metrics tự động

Linkerd proxy expose `/metrics` ở port 4191 theo Prometheus format. Mỗi proxy quan sát mọi request đi qua nó (cả inbound và outbound) và sinh metric:

| Metric | Loại | Nội dung |
|--------|------|----------|
| `request_total` | counter | Số request, label theo direction, target service, status |
| `response_total` | counter | Số response, label theo classification (success/failure) |
| `response_latency_ms` | histogram | Latency time-to-first-byte |
| `tcp_open_connections` | gauge | Connection đang mở |
| `tcp_read_bytes_total` | counter | Byte đọc |
| `tcp_write_bytes_total` | counter | Byte ghi |

Ba metric đầu chính là ba trong bốn "golden signal" của Google SRE (RPS, latency, error rate; cái thứ tư saturation đến từ node-exporter và kube-state-metrics). Không có dòng code instrument nào trong app — chỉ cần inject sidecar.

## Vì sao "miễn phí" với mọi service

Service mesh hoạt động bằng cách inject sidecar proxy vào mỗi pod (Linkerd dùng linkerd2-proxy, Istio dùng Envoy). Mọi traffic vào/ra pod đi qua sidecar trước khi tới container app — thực hiện qua iptables redirect ở mức network namespace. Sidecar thấy toàn bộ payload HTTP/gRPC, parse được method, path, status code, trace ID, từ đó tự sinh metric.

Khác cơ bản với code-level instrumentation:

| Khía cạnh | Service mesh metric | Code instrumentation |
|-----------|--------------------|-----------------------|
| Coverage | Mọi service có sidecar | Chỉ service đã code |
| Effort | Inject 1 lần | Mỗi service tự instrument |
| Granularity | RPS, latency, status code | Business metric, internal state |
| Trace context | Có (nếu app forward header) | Đầy đủ trace tree |
| Latency overhead | 1–3ms per hop | Tuỳ implementation |

Hai cách không loại trừ. Mesh metric là baseline; code instrumentation thêm business metric (số đơn hàng, doanh thu, retry queue depth). Pattern phổ biến: mesh cấp golden metrics cho mọi service, OpenTelemetry SDK cấp trace + custom metric cho service quan trọng.

## Hợp nhất với Prometheus stack

Linkerd publish ServiceMonitor (qua subchart `linkerd-viz`) hoặc PodMonitor để Prometheus tự discover proxy endpoint. Cấu hình values:

```yaml
prometheusUrl: http://cortex-nginx.obs-metric.svc.cluster.local/prometheus

podMonitor:
  enabled: true
  controller: { enabled: true }
  serviceMirror: { enabled: true }
  proxy: { enabled: true }
```

`prometheusUrl` cho Linkerd biết nơi đọc lại metric khi render dashboard built-in. Trỏ vào Cortex (long-term store) thay vì Prometheus local — Linkerd luôn có data đủ dài cho query trend.

`podMonitor.proxy` enable scrape `/metrics` của mọi linkerd proxy trong cluster. Khi pod nào có annotation `linkerd.io/inject: enabled`, sidecar tự xuất hiện và được scrape.

## Trade-off

Tăng latency: mỗi hop thêm 1–3ms cho proxy. Cluster với chain service dài (5–6 hop) cảm nhận được.

Tăng resource: mỗi pod có thêm 1 container proxy (Linkerd ~10–20MB memory, Envoy ~50–100MB). Cluster lớn cộng dồn đáng kể.

Operational complexity: thêm CRD, control plane, cert rotation cho identity, debugging request flow phức tạp hơn (mtail proxy log).

Tradeoff thắng khi: nhiều service không có/không thể instrument, cần thống nhất view reliability cross-team, muốn mTLS đi kèm. Tradeoff thua khi: cluster nhỏ với ít service đã instrument đầy đủ, sensitive về latency p99, team không có capacity vận hành mesh.

Linkerd vs Istio chủ yếu là đánh đổi simplicity (Linkerd nhẹ, ít knob) vs feature breadth (Istio nhiều knob, traffic management phong phú hơn). Cho mục đích observability thuần, Linkerd thường đủ.

## Nguồn tham khảo

- [Linkerd Proxy Metrics — linkerd.io](https://linkerd.io/2.16/reference/proxy-metrics/)
- [Linkerd Monitoring with Prometheus — linkerd.io](https://linkerd.io/2.16/tasks/external-prometheus/)
- [Google SRE Book - Monitoring Distributed Systems (Golden Signals) — sre.google](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Istio Telemetry — istio.io](https://istio.io/latest/docs/concepts/observability/)
- Repo tham chiếu: [references/repos/k8s-obs-module/obs-linkerd](../../references/repos/k8s-obs-module/obs-linkerd/)
- Transcript khai quật: [k8s-obs-module.md](../../references/interviews/k8s-obs-module.md)

## Liên kết

- [Quan sát hệ thống trong Kubernetes - node neo, service mesh là một nguồn metric phụ trợ cho pillar metric](./Quan%20s%C3%A1t%20h%E1%BB%87%20th%E1%BB%91ng%20trong%20Kubernetes.md)
- [Prometheus hai tầng với Cortex - mesh metric được Prometheus scrape rồi remote_write vào Cortex](./Prometheus%20hai%20t%E1%BA%A7ng%20v%E1%BB%9Bi%20Cortex.md)
- [Scrape metric kubelet trong Prometheus - cùng họ về nguồn metric trong cluster, mesh là layer L7 còn kubelet là layer node](./Scrape%20metric%20kubelet%20trong%20Prometheus.md)
- [Time to First Byte - latency time-to-first-byte chính là cái mesh proxy đo](../Web%20development/Time%20to%20First%20Byte.md)
