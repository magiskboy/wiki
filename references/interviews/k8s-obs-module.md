# Phỏng vấn khai quật: k8s-obs-module

- **Leaf**: Observability services (Prometheus, Jaeger, Loki, Kafka, Grafana stack, on-call...) (`_source/track.md` > Teko > SRE) — đồng thời phản chiếu vào leaf Personal > K8s observability demo (repo public `demo-k8s-obs-modules`).
- **Repo**: private `magiskboy/k8s-obs-module` — mirror local: `references/repos/k8s-obs-module/`.
- **Blog song hành**: [Xây dựng hệ thống monitor đơn giản trong Kubernetes](../../references/www/xay-dung-he-thong-monitor-don-gian-trong-k8s.mdx) (2025-02-18) — bản giản lược công khai.
- **Phiên phỏng vấn**: 2026-05-24.

## Bối cảnh

- [Trí nhớ] Dự án **cá nhân**, mục đích duy nhất là **củng cố kiến thức đã học khi làm SRE ở Teko** về k8s on-premise. Không phải sản phẩm production, không bắt nguồn từ một incident nào.
- [Trí nhớ] Repo private `k8s-obs-module` là phiên bản đầy đủ; repo công khai `demo-k8s-obs-modules` + blog là bản giản lược cho người đọc dễ tiếp cận.
- [Trí nhớ] Lý do thêm Linkerd: là service mesh hỗ trợ giám sát và quản lý policy networking, bao gồm cả thông lượng vào ra của pod. Không phải vì có incident cần xử lý.

## Lãnh thổ tri thức trong repo

### Cluster

- [Phân tích] kind cluster on-prem style: 1 control-plane + 2–3 worker (file `kind-cluster.yaml` hiện 1 cp + 2 worker; blog mô tả 3 worker).
- [Phân tích] Calico CNI thay kindnet. Lý do: kindnet không hỗ trợ NetworkPolicy. Cài qua `tigera-operator.yaml` + `custom-resources.yaml`.
- [Phân tích] `cloud-provider-kind` container với cờ `-enable-lb-port-mapping` để dùng được Service type `LoadBalancer` trên macOS/Windows (kind chạy trong VM nên LB IP không reach được từ host). [Bổ sung — nguồn] Cờ này được mô tả trong [README cloud-provider-kind](https://github.com/kubernetes-sigs/cloud-provider-kind#enabling-load-balancer-port-mapping).

### Storage layer (`obs-storage`)

- [Phân tích] Hai chart trong cùng namespace `obs-storage`:
  - **MinIO** (S3-compatible) — chứa chunk của Cortex và Loki.
  - **Cassandra** — backend cho Jaeger trace.
- [Phân tích] Pattern: MinIO làm S3-compat trên on-prem khi không có S3 thật. Phải tạo access key + 4 bucket bằng tay: `cortex`, `loki-chunks`, `loki-admin`, `loki-ruler`. Credentials điền vào `values.yaml` root.

### Metric stack (`obs-metric`)

- [Phân tích] 3 release chính:
  - **kube-prometheus-stack** (`prometheus-community/kube-prometheus-stack` v69.2.4) — Prometheus + Operator + node-exporter + kube-state-metrics + CRDs.
  - **Cortex** (`cortex-helm/cortex` v2.5.0) — long-term storage cho metric.
  - **metrics-server** (`kubernetes-sigs/metrics-server` v3.12.2) — cho HPA / `kubectl top`.

- [Phân tích] **Pattern Prometheus 2 tầng**:
  - Prometheus local: `retention: 1d`, `retentionSize: 2GB`, `persistentVolume.enabled: false` → hoàn toàn stateless, restart mất sạch.
  - `remoteWrite: http://cortex-nginx.obs-metric.svc.cluster.local/api/v1/push` → đẩy mọi sample lên Cortex.
  - Cortex là nơi giữ data dài hạn, scale ngang theo từng component (distributor/ingester/querier/store-gateway). Sample được lưu chunk → MinIO.
  - Bằng cách này Prometheus chỉ làm scraping engine, không phải database.

- [Trí nhớ → đã verify] **Insight kubelet metrics scraping**: trong `obs-metric/prometheus-stack.yaml`:
  - Tắt scrape kubelet mặc định: `kubelet.enabled: false` (và tắt luôn kubeApiServer/kubeControllerManager/coreDns/kubeEtcd/kubeScheduler/kubeProxy/kubeDns — disable hết các ServiceMonitor mặc định cho control-plane component).
  - Thay bằng `additionalScrapeConfigs` tự viết:
    ```yaml
    - job_name: 'kubelet'
      scrape_interval: 10s
      metrics_path: /metrics/cadvisor
      scheme: https
      tls_config: { insecure_skip_verify: true }
      kubernetes_sd_configs:
        - role: node
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    ```
  - Comment trong repo trỏ tới [prometheus-operator/prometheus-operator#926 comment 374781066](https://github.com/prometheus-operator/prometheus-operator/issues/926#issuecomment-374781066).
  - **Insight cốt lõi**: kubelet không phải pod, không có Service ổn định kèm sẵn → ServiceMonitor pattern của operator không xử lý out-of-the-box; phải dùng `kubernetes_sd_configs: role=node` để discover qua Node object. Auth dùng serviceaccount token (Prometheus chạy như pod nên tự có), TLS phải `insecure_skip_verify` vì cert kubelet self-signed. Endpoint `/metrics/cadvisor` cho metric container-level (CPU/mem từng container).
  - [Bổ sung — nguồn] Kubelet expose 2 endpoint metric: `/metrics` (kubelet itself) và `/metrics/cadvisor` (container resource), theo [Kubernetes docs - System Metrics](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/).

- [Phân tích] metric-server cũng đụng cùng vấn đề TLS+address với kubelet, có 3 flag override:
  - `--kubelet-insecure-tls` — bỏ verify cert (cùng lý do với Prometheus).
  - `--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname` — đảo thứ tự ưu tiên. Mặc định là Hostname → trên on-prem nhiều khi Hostname không resolve được, đảo lên InternalIP trước.
  - `--kubelet-use-node-status-port` — dùng port lấy từ `Node.Status.DaemonEndpoints.KubeletEndpoint` thay vì assume hard-code 10250. [Bổ sung — nguồn] Mô tả ở [metrics-server README](https://github.com/kubernetes-sigs/metrics-server#configuration).

### Log stack (`obs-log`)

- [Phân tích] 3 release:
  - **Loki** (`grafana/loki` v6.25.1) — store + query log, chunk lưu MinIO bucket `loki-chunks`.
  - **fluent-bit-collector** (`fluent/fluent-bit`) — chạy như DaemonSet, đẩy log vào Kafka topic `logging`.
  - **fluent-bit-processor** (`fluent/fluent-bit`, `replicaCount: 2`) — Deployment, đọc Kafka, transform, gửi vào Loki gateway.

- [Phân tích + Trí nhớ] **Pattern Kafka làm buffer cho log pipeline**:
  - Collector chỉ làm 1 việc: đọc log từ node và ghi vào Kafka thật nhanh.
  - Processor đọc Kafka, lift payload (filter `nest` với `Operation: lift`), gắn label k8s (`namespace`, `pod`, `container`, `app`, `component`, `instance`), gửi vào Loki qua gateway.
  - Lợi ích: tách hot path khỏi backend pressure. Khi Loki chậm/down, log không mất vì còn nằm trong Kafka. Processor có thể scale độc lập với collector. Collector luôn nhẹ.
  - [Bổ sung — nguồn] [Fluent Bit Kafka input plugin](https://docs.fluentbit.io/manual/pipeline/inputs/kafka) và [Loki output plugin](https://docs.fluentbit.io/manual/pipeline/outputs/loki) đều có sẵn — pattern này được Fluent ủng hộ chính thức.
  - [Phân tích] Khác với blog công khai (Promtail → Loki trực tiếp). Đây là một trong các "Cải tiến" được liệt kê cuối blog.

### Trace stack (`obs-tracing`)

- [Phân tích] **Jaeger** (`jaegertracing/jaeger` v3.4.0) với backend Cassandra. Có jaeger-collector (nhận trace từ app) và jaeger-query (cho Grafana datasource).
- [Phân tích] Cassandra cho Jaeger là một trong các backend được support chính thức (cùng với Elasticsearch và Badger). [Bổ sung — nguồn] [Jaeger docs - Storage backends](https://www.jaegertracing.io/docs/1.65/deployment/#storage-backends).

### Service mesh (`obs-linkerd`)

- [Phân tích] 2 chart:
  - **linkerd-crds** v1.8.0 — CRDs phải cài trước.
  - **linkerd-control-plane** v1.16.11 — identityTrustAnchorsPEM + issuer cert/key mount từ file `ca.crt`, `issuer.crt`, `issuer.key` (chưa thấy trong repo, cần generate khi deploy).

- [Phân tích] `linkerd-control-plane.yaml` values:
  - `prometheusUrl` trỏ thẳng vào Cortex (`http://cortex-nginx.obs-metric.svc.cluster.local/prometheus`) — Linkerd query metric từ long-term store thay vì Prometheus local.
  - `podMonitor.enabled: true` với 3 sub-monitor: `controller`, `serviceMirror`, `proxy` (`namespaceSelector: matchNames: []` = empty list để chấp nhận discovery toàn cluster).

- [Trí nhớ] Vai trò Linkerd trong repo: giám sát + network policy + thông lượng pod. Là observability L7.
- [Bổ sung — nguồn] Linkerd proxy tự động export "golden metrics" (request rate, success rate, latency p50/p95/p99) cho mọi connection mà nó proxy, theo [Linkerd docs - Proxy Metrics](https://linkerd.io/2.16/reference/proxy-metrics/). Đây là lợi điểm key của service mesh làm observability layer.

### Dashboard (`obs-dashboard`)

- [Phân tích] **Grafana** trong namespace `obs-grafana`, 4 datasource:
  - Cortex (type: prometheus) → cho metric dài hạn.
  - Prometheus local (type: prometheus) → fallback hoặc cho query gần đây.
  - Loki → cho log.
  - Jaeger → cho trace.

### Kafka stack (`obs-kafka`)

- [Phân tích] 3 release:
  - **Kafka** (bitnamicharts) v31.3.1 — broker.
  - **kafka-connect** (`licenseware/kafka-connect`) v0.4.0 — chưa rõ kết nối gì; config trỏ Schema Registry + broker.
  - **AKHQ** v0.25.1 — UI cho Kafka.
- [Phân tích] Kafka phục vụ ít nhất 2 vai trò: (1) buffer cho log pipeline (đã mô tả), (2) có Kafka Connect và schema-registry config → để mở rộng cho ingestion pattern khác (CDC, sink connector...). Chưa thấy connector cụ thể nào trong repo, có thể là phần WIP.

## Quyết định kiến trúc nổi bật

1. **Tách namespace theo layer**: `obs-storage`, `obs-metric`, `obs-log`, `obs-tracing`, `obs-linkerd`, `obs-grafana`, `obs-kafka`. Mỗi layer redeploy/clean độc lập. Helmfile label `module=metric|log|tracing|service-mesh|dashboard|kafka|storage` cho phép `helmfile apply -l module=metric` để re-apply 1 layer.

2. **Prometheus 2 tầng**: local stateless + Cortex long-term qua remoteWrite. Cortex chunk → MinIO.

3. **Kafka làm buffer cho log pipeline**: tách collector (hot, nhẹ) khỏi processor (transform + sink).

4. **Service mesh làm observability L7**: Linkerd proxy tự export golden metrics, query từ Cortex.

5. **MinIO làm S3-compat backend chung**: cùng MinIO host Cortex chunk + Loki chunk + Loki admin + Loki ruler. Pattern điển hình cho on-prem.

6. **Calico thay kindnet**: chấp nhận đổi CNI ngay từ đầu chỉ để có NetworkPolicy. Phù hợp với mô hình tách namespace theo layer (có thể policy-based isolate).

## Gaps / WIP

- README ghi rõ "Have some configuration what I haven't set up yet".
- File `kind-cluster.yaml` ghi 1 cp + 2 worker, không khớp blog (1 cp + 3 worker).
- Linkerd CA files (`ca.crt`, `issuer.crt`, `issuer.key`) chưa có trong repo — cần generate khi deploy.
- Cortex và Loki + Kafka đều có file `.gotmpl` (`cortex.yaml.gotmpl`, `loki.yaml.gotmpl`, `kafka.yaml.gotmpl`, `fluent-bit-collector.yaml.gotmpl`, `jaegertracing.yaml.gotmpl`, `cassandra.yaml.gotmpl`, `minio.yaml.gotmpl`, `grafana.yaml.gotmpl`, `akhq.yaml.gotmpl`) — chưa được đọc ở phỏng vấn này vì git ignore hoặc không tracked; có thể chứa thêm config.
- Kafka Connect có config nhưng chưa có connector cụ thể nào trong repo.
- Blog kết bài có list cải tiến: mTLS (đã làm — Linkerd), HA log với Kafka (đã làm), Kubernetes events analysis (chưa thấy), Kafka cho trace HA (chưa thấy), alert system (alertmanager đang `enabled: false`).

## Đường nối đồ thị

- Liên kết với leaf gần nhất trong wiki: hiện wiki chưa có node observability nào — đây là vùng tri thức mới hoàn toàn.
- Có thể nối tới [dynamo-overview-on-k8s](../../wiki/AI%20v%C3%A0%20Machine%20Learning/NVIDIA%20Dynamo.md) khi node mới đề cập tới pattern deploy stack lên k8s.
- Node wiki đã chưng cất từ transcript này:
  1. [Quan sát hệ thống trong Kubernetes](../../wiki/DevOps%20v%C3%A0%20Infrastructure/Quan%20s%C3%A1t%20h%E1%BB%87%20th%E1%BB%91ng%20trong%20Kubernetes.md) — hub (3 pillar + layer)
  2. [Scrape metric kubelet trong Prometheus](../../wiki/DevOps%20v%C3%A0%20Infrastructure/Scrape%20metric%20kubelet%20trong%20Prometheus.md) — insight cụ thể về kubelet metric
  3. [Prometheus hai tầng với Cortex](../../wiki/DevOps%20v%C3%A0%20Infrastructure/Prometheus%20hai%20t%E1%BA%A7ng%20v%E1%BB%9Bi%20Cortex.md) — pattern stateless + long-term
  4. [Kafka làm buffer cho log pipeline](../../wiki/DevOps%20v%C3%A0%20Infrastructure/Kafka%20l%C3%A0m%20buffer%20cho%20log%20pipeline.md) — pattern tách hot path
  5. [Service mesh làm tầng quan sát](../../wiki/DevOps%20v%C3%A0%20Infrastructure/Service%20mesh%20l%C3%A0m%20t%E1%BA%A7ng%20quan%20s%C3%A1t.md) — Linkerd golden metrics
