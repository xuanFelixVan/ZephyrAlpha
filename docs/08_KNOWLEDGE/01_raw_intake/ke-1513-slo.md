---
module_id: KE-1423-----slo-000
title: 12.2 冷启动 SLO
category: module_blueprint
ttl: permanent
---

# 12.2 冷启动 SLO

12.2 冷启动 SLO

| 指标 | 目标 | 说明 |
|------|------|------|
| 进程 import | ≤ 1 s | 仅 import feedback-loop |
| SQLite 连接 + schema check | ≤ 300 ms | WAL |
| 基线缓存加载 | ≤ 500 ms | 从 baseline_cache.json |
| pending_actions.ndjson 回放 | ≤ 1 s | < 1000 条 |
| 首次 `record_metric()` | ≤ 50 ms | - |
| **总冷启动到可用** | **≤ 3 s** | - |

---
