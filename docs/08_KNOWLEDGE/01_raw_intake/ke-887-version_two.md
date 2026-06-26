---
module_id: KE-809
status: active
title: 2.2 V2 自动化警告
category: governance_rule
ttl: permanent
---

# 2.2 V2 自动化警告

2.2 V2 自动化警告

以下条件触发时，生成**警告但允许继续**：

| 触发条件 | 警告规则 | 来源 |
|---------|---------|------|
| `date` 格式非 YYYY-MM-DD | META-V07 | PS-STD-001 §14 |
| `doc_type` 与存放路径不匹配 | META-V08 | PS-STD-001 §14 |
| `layer` 字段值不在合法列表 | META-V12 | PS-STD-001 §14 |
| `safety_level: H` 且 `review_status: unreviewed` | P1 警告 | PS-STD-001 §10.16 |
| `module_id` 前缀不在注册表中 | — | — |

**V2 警告累计**：同一类型警告在同一文件中出现 3 次以上 → 升格为 V1 阻断。
