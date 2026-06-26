---
module_id: KE-4059
title: 3.3 输入契约
category: module_blueprint
ttl: permanent
---

# 3.3 输入契约

3.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `decompose()` | `blueprint_path` | ✅ | 绝对路径 + .md + doc_type=blueprint |
| | `output_dir` | ✅ | 必须是 `03_modules/{layer}/{module}/changes/{feature-id}/` |
| `create_task_card()` | `task` | ✅ | TaskCard——G0+G7 门禁通过 + task_repo.create() |
| `transition()` | `task_id` | ✅ | `{NAMESPACE}-{SEQ}`（如 `KBG-001`） |
| | `to_status` | ✅ | TaskStatus 合法值 + 状态机允许路径 |
| `dispatch()` | `task_id` | ✅ | status in {PENDING, READY, RETRY} |
