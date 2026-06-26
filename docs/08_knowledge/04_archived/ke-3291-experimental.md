---
module_id: KE-3179---14-------experimental-000
title: 11.1 按 14 层资源预算（experimental 单机）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 11.1 按 14 层资源预算（experimental 单机）

11.1 按 14 层资源预算（experimental 单机）

| 层 | CPU (core·h/日) | Memory 峰值 (GB) | Storage 年增 (GB) | IOPS 峰值 |
|----|:-----:|:------:|:------:|:----:|
| L00 Data Source | 2 | 1.5 | 20 | 300 |
| L01 Infrastructure | 0.5 | 0.5 | 1 | 50 |
| L02 Alpha Factor | 6 | 3 | 15 | 500 |
| L03 Signal Generation | 3 | 1 | 5 | 100 |
| L04 Risk Management | 1 | 0.5 | 2 | 150 |
| L05 Portfolio Construction | 4 | 2 | 3 | 80 |
| L06 Trade Execution | 2 | 0.8 | 8 | 200 |
| L07 Post-Trade | 2 | 1 | 5 | 60 |
| L08 Human-AI | 1 | 0.5 | 1 | 30 |
| L09 Sandbox | 8 | 4 | 30 | 400 |
| L10 Compliance | 0.5 | 0.3 | 1 | 40 |
| L11 ML Platform | 3 | 4 | 10 | 200 |
| L12 Telemetry | 1 | 0.8 | 20 | 150 |
| L13 Experiment | 2 | 1.5 | 8 | 100 |
| L2 Audit Log | 0.3 | 0.2 | 25 | 50 |
| **合计峰值** | **~20-25** | **~12 / ~24 含 OS** | **~155** | **~1500** |

**experimental 单机建议**：16-core / 32 GB / 500 GB SSD。GPU 当前不需要，Post-Activation 触发时 1× RTX 4090 class 足够。
