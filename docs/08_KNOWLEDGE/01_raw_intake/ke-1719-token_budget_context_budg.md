---
module_id: KE-1629---context-budg-003
status: active
title: 2. Token Budget — context_budget_tracker.py (§2.2 + DD2 + DD6)
category: module_blueprint
ttl: permanent
---

# 2. Token Budget — context_budget_tracker.py (§2.2 + DD2 + DD6)

2. Token Budget — context_budget_tracker.py (§2.2 + DD2 + DD6)

三级预算管理：

| 级别 | 阈值 | 行为 |
|:---:|:---:|------|
| L1_WARNING | 80% (6400/8000) | 预警——有余量做最后 compress |
| L2_CRITICAL | 90% (7200/8000) | 触发 DocCompressor.compress() → max_chars=4000, preserve_structure=true |
| L3_HARD_STOP | 95% (7600/8000) | 硬截断——不追加 context，仅保留 Always-on |

Token 预算分配表：

| 类型 | Token 预算 | 优先级 |
|------|:---:|:---:|
| KE 条目 | 0-3000 | 最高 |
| 规则/策略 | 0-2000 | 高 |
| 蓝图 | 0-2000 | 中 |
| 运行时日志 | 0-1000 | 低 |
| **总计** | **8000** | — |
