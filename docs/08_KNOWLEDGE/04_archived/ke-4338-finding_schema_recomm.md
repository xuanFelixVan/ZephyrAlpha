---
module_id: KE-4178------recomm-000
title: 6.5 Finding Schema 新增字段：recommendation
category: module_blueprint
---

# 6.5 Finding Schema 新增字段：recommendation

6.5 Finding Schema 新增字段：recommendation

> 对标 ITIL Level 2（决策辅助自动化）——MEDIUM 及以上 Finding 应包含 `recommendation` 字段，给出修复建议但不自动执行。

| 字段 | 类型 | 说明 |
|------|------|------|
| `recommendation` | string | 修复建议——人类可读的操作指引。仅建议，不执行 |
| `recommendation_type` | enum | `auto_fixable`（可自动化修复）/ `manual_only`（必须人工修复）/ `needs_review`（需进一步分析） |
| `recommended_action` | enum | `modify_file` / `create_task` / `consult_owner` / `ignore` |


---
