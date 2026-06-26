---
module_id: KE-1627
title: 2. Three-Tier Degradation Strategy (§3)
category: module_blueprint
ttl: permanent
---

# 2. Three-Tier Degradation Strategy (§3)

2. Three-Tier Degradation Strategy (§3)

| 情况 | 降级行为 | 标记 |
|------|------|------|
| **VMS 不可用** | 仅注入 AGENTS.md + 当前模块蓝图 | `session.degraded=true` |
| **LSG 拒绝 ≥3 次** | 移除被拒绝块，注入剩余 | `injection_blocks_removed=N` |
| **CE 10s 超时** | 降级注入—仅硬编码规则 | `CE_timeout_metric += 1` |
