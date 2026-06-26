---
module_id: KE-1383----slo-experimental-vms-003
title: 11.1 稳态 SLO（experimental，VMS 健康前提下）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 11.1 稳态 SLO（experimental，VMS 健康前提下）

11.1 稳态 SLO（experimental，VMS 健康前提下）

| 指标 | 目标 | 测试条件 |
|------|------|---------|
| `build()` p50 | ≤ 1500 ms | token_budget=16000，4 个 Collection 各 top_k=5 |
| `build()` p95 | ≤ 3000 ms | 同上 |
| `compress()` LLM p50 | ≤ 800 ms | 输入 24k 压到 16k |
| `compress()` LLM p95 | ≤ 2000 ms | 同上 |
| `compress()` 规则降级 p95 | ≤ 100 ms | 纯规则压缩 |
| `validate()` p95 | ≤ 50 ms | 缓存内源解析 |
| `inject()` p95 | ≤ 300 ms | 多通道并发 |
| `adjust_strategy()` p95 | ≤ 20 ms | 本地状态写入 |
| 端到端（build+compress+validate+inject） p50 | ≤ 2500 ms | - |
| 端到端 p95 | ≤ 5000 ms | - |
