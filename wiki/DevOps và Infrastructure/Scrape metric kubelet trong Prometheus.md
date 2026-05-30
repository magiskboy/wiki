---
tags:
  - infrastructure
date: 2026-05-29
---
# Scrape metric kubelet trong Prometheus

Kubelet là daemon chạy trên mỗi node, expose nhiều endpoint metric ở port 10250 (HTTPS). Trong số đó `/metrics/cadvisor` là endpoint quan trọng nhất cho observability container vì chứa metric CPU/memory/IO per container. Vấn đề là kubelet không phải pod — không có Service ổn định kèm sẵn — nên `ServiceMonitor` mặc định của prometheus-operator không xử lý được out-of-the-box. Lời giải là disable scrape mặc định cho control-plane component và viết tay `additionalScrapeConfigs` discover qua Node object.

Nguồn: [System Metrics — Kubernetes docs](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/), [prometheus-operator/prometheus-operator#926](https://github.com/prometheus-operator/prometheus-operator/issues/926).

## Endpoint kubelet expose

| Endpoint | Nội dung |
|----------|----------|
| `/metrics` | Metric của bản thân kubelet (sync loop, lifecycle pod, runtime operation) |
| `/metrics/cadvisor` | Metric per container do cAdvisor sinh (CPU, memory, IO, network) |
| `/metrics/resource` | Resource usage tóm tắt, dùng cho metrics-server |
| `/metrics/probes` | Trạng thái liveness/readiness probe |

Tất cả endpoint đều ở cùng port 10250 và đều yêu cầu authentication theo cấu hình RBAC. Cert kubelet thường là self-signed do CA của cluster sinh, không có CA chung mà client ngoài tin được mặc định. Đây là nguồn gốc của hai vấn đề kỹ thuật khi scrape.

## Vì sao ServiceMonitor mặc định không hoạt động

`ServiceMonitor` của prometheus-operator được thiết kế cho workload chạy như pod, sau một Service. Operator dựa vào Service để discover endpoint. Kubelet không phải pod — nó là binary chạy trực tiếp trên host và Kubernetes mock một Service ảo `kubernetes.io/kubelet` để workaround. Cách workaround này phụ thuộc vào cấu hình cluster cụ thể (cloud provider, network policy, auth mode), và thường fail với lỗi `401 Unauthorized` khi Prometheus không gửi đúng credential. Đây là vấn đề được report trong [prometheus-operator#926](https://github.com/prometheus-operator/prometheus-operator/issues/926): trên GKE, kubelet target hiện DOWN vì 401.

Cùng họ với kubelet là các control-plane component khác chạy như binary trên host hoặc static pod: `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`, `etcd`, `kube-proxy`, `coredns`. Tất cả đều có vấn đề discover tương tự và `kube-prometheus-stack` mặc định bật ServiceMonitor cho tất cả, dẫn đến nhiều target DOWN. Cách giải an toàn là disable hết và scrape thủ công những target thực sự cần.

## Workaround qua additionalScrapeConfigs

Disable scrape mặc định:

```yaml
kubelet: { enabled: false }
kubeApiServer: { enabled: false }
kubeControllerManager: { enabled: false }
kubeScheduler: { enabled: false }
kubeEtcd: { enabled: false }
kubeProxy: { enabled: false }
kubeDns: { enabled: false }
coreDns: { enabled: false }
```

Thay bằng scrape config tự viết, discover qua Node object thay vì Service:

```yaml
prometheus:
  prometheusSpec:
    additionalScrapeConfigs:
      - job_name: 'kubelet'
        scrape_interval: 10s
        metrics_path: /metrics/cadvisor
        scheme: https
        tls_config:
          insecure_skip_verify: true
        kubernetes_sd_configs:
          - role: node
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
```

Ba điểm cốt lõi:

`kubernetes_sd_configs: role=node` cho Prometheus liệt kê tất cả Node trong cluster qua Kubernetes API và scrape ở address của Node. Khác với `role=endpoints` hay `role=service` (vốn cần Service object), `role=node` chỉ cần đọc danh sách Node — luôn có.

`bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token` cho phép Prometheus tự auth qua ServiceAccount token. Pod Prometheus mount token này tự động khi tạo trong namespace có RBAC phù hợp; không cần generate cert riêng.

`insecure_skip_verify: true` bỏ verify cert vì cert kubelet được CA cluster sign, mà Prometheus không tin CA đó mặc định. Trade-off: nếu trong cluster có MITM thì không phát hiện được. Trong môi trường multi-tenant cao thì nên mount CA bundle thay vì skip.

## Pattern lan sang metrics-server

metrics-server (cho `kubectl top` và HPA) cũng gọi `/metrics/resource` của kubelet và đụng cùng vấn đề. Workaround dùng flag:

```yaml
- --kubelet-insecure-tls
- --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
- --kubelet-use-node-status-port
```

`--kubelet-insecure-tls` cùng lý do với Prometheus. `--kubelet-preferred-address-types` đảo thứ tự ưu tiên: mặc định `Hostname` đầu tiên, on-prem nhiều khi Hostname không resolve được, đảo `InternalIP` lên đầu. `--kubelet-use-node-status-port` đọc port động từ `Node.Status.DaemonEndpoints.KubeletEndpoint` thay vì assume hard-code 10250 — quan trọng khi cluster cấu hình kubelet ở port khác.

## Nguồn tham khảo

- [Kubernetes System Metrics — kubernetes.io](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/)
- [Prometheus kubernetes_sd_configs — prometheus.io](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#kubernetes_sd_config)
- [prometheus-operator issue #926 — github.com](https://github.com/prometheus-operator/prometheus-operator/issues/926)
- [metrics-server configuration — github.com/kubernetes-sigs/metrics-server](https://github.com/kubernetes-sigs/metrics-server#configuration)
- Repo tham chiếu: [references/repos/k8s-obs-module/obs-metric/prometheus-stack.yaml](../../references/repos/k8s-obs-module/obs-metric/prometheus-stack.yaml)
- Transcript khai quật: [k8s-obs-module.md](../../references/interviews/k8s-obs-module.md)

## Liên kết

- [Quan sát hệ thống trong Kubernetes - node neo về kiến trúc observability trên k8s](./Quan%20s%C3%A1t%20h%E1%BB%87%20th%E1%BB%91ng%20trong%20Kubernetes.md)
- [Prometheus hai tầng với Cortex - scrape config trỏ remoteWrite vào Cortex là một bước trong pattern này](./Prometheus%20hai%20t%E1%BA%A7ng%20v%E1%BB%9Bi%20Cortex.md)
- [Hiểu công nghệ trước khi áp dụng - bài học cùng họ về việc default config không hoạt động vì assumption khác môi trường](../Ph%C3%A1t%20tri%E1%BB%83n%20b%E1%BA%A3n%20th%C3%A2n/Hi%E1%BB%83u%20c%C3%B4ng%20ngh%E1%BB%87%20tr%C6%B0%E1%BB%9Bc%20khi%20%C3%A1p%20d%E1%BB%A5ng.md)
