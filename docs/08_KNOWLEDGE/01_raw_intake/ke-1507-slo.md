---
module_id: KE-1417----slo-003
title: 12.1 稳态 SLO
category: module_blueprint
---

# 12.1 稳态 SLO

12.1 稳态 SLO

| 指标 | 目标 | 条件 |
|------|------|------|
| `record_metric()` p50 | ≤ 3 ms | 单条 |
| `record_batch(100)` p95 | ≤ 50 ms | - |
| `detect_anomalies()` p95 | ≤ 200 ms | 单指标 7 天窗口 |
| `get_baseline()` p50 | ≤ 30 ms | 缓存命中 |
| `dispatch_action()` p95 | ≤ 500 ms | 含下游 Protocol 调用 |
| `query_timeseries(1h raw)` p95 | ≤ 100 ms | - |
| 最大吞吐（record） | ≥ 1000 metric/s | WAL 批提 |
