---
module_id: KE-3174
title: 10.2 Logs / 日志
category: documentation
ttl: permanent
---

# 10.2 Logs / 日志

10.2 Logs / 日志

| 级别 | 日志类型 | 保留策略 |
|------|---------|---------|
| **L1 应用日志** | 业务运行事件 | 本地 30 天；Loki 90 天 |
| **L2 审计日志** | 决策与操作记录 | **不可删除（append-only，KBG-0002）**；≥ 1 年 |
| **L3 安全日志** | 认证、API Key 使用 | 本地 90 天；Prod 加密存储 |

日志格式：结构化 JSON（含 `trace_id` / `span_id` / `layer` 字段），便于 OTel Loki 采集。
