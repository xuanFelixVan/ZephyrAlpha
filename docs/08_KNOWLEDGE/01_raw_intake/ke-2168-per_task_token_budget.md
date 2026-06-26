---
module_id: KE-2076
status: active
title: 3.2 #18: PerTaskTokenBudget
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.2 #18: PerTaskTokenBudget

3.2 #18: PerTaskTokenBudget

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\per_task_token_budget.py`

实现 `PerTaskTokenBudget` 类（蓝图 L2039-2106）：
- `allocate(task_id, estimated_reasoning_steps) -> TaskBudget`
- `check_and_consume(task_id, actual_tokens) -> ConsumptionResult`
- 超出预算时触发 `task_split`（自动拆分为子任务）
- 蓝图 L2058-2078 YAML 完整实现
