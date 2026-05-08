---
module_id: KE-governance-aud-004-003
title: AUD-004：审计记录格式
category: governance
---

# AUD-004：审计记录格式

AUD-004：审计记录格式

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 所有审计记录 | 每条审计记录必须包含以下字段：`timestamp`（ISO 8601 格式 `YYYY-MM-DDTHH:MM:SSZ`，UTC 时区）、`operator_id`、`operation_type`、`operation_detail`、`result`。字段名使用 snake_case | 格式不合规的记录需补录 |

---
