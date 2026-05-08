---
module_id: KE-documentat-10_4_otel_integration-000
title: 10.4 OTel Integration 概要
category: documentation
---

# 10.4 OTel Integration 概要

10.4 OTel Integration 概要

| 组件 | 用途 | 后端 |
|------|------|------|
| `opentelemetry-sdk` (Python) | Metrics + Traces | OTLP gRPC → Collector |
| OTel Collector (Agent) | 接收 + 路由 | 本地进程/ 独立 Gateway（Post-Activation） |
| Prometheus | Metrics 存储 | `:9090` |
| Grafana Tempo | Traces 存储 | `:3200` |
| Loki | Logs 聚合 | `:3100` |
| Grafana Dashboard | 统一看板 | `:3000` |

---
