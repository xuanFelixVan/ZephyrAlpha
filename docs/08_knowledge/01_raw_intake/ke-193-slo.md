---
module_id: KE-173----------slo-000
title: 2.2 三平面的量化指标（SLO）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 三平面的量化指标（SLO）

2.2 三平面的量化指标（SLO）

| 平面 | 延迟 SLO | 吞吐 SLO | 可用性 SLO | 故障影响域 |
|---|---|---|---|---|
| **Hot Path** | P50 < 1 ms / P99 < 10 ms | ≥ 100k msg/s | 99.99% | **资金直接损失**（订单错过 / 风控失守）|
| **Warm Path** | P50 < 50 ms / P95 < 1 s | ≥ 1k req/s | 99.9% | **决策质量下降**（信号延迟 / AI 响应慢）|
| **Cold Path** | Job 完成时间 < SLA 窗口 | 按数据量定 | 95%（允许重跑）| **分析报表延迟**（次日补救即可）|
