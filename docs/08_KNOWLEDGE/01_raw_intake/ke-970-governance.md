---
module_id: KE-892
status: active
title: 4.1.1 触发条件
category: governance
ttl: permanent
---

# 4.1.1 触发条件

4.1.1 触发条件

- **状态机触发**：`TaskRepository.transition(task_id, IN_PROGRESS)` 调用时（已实现于 `task_repo.py:461`）
- **显式触发**：`GateEngine.evaluate(task, "G1")` 直接调用
- **前置条件**：task 的 `deliverables` 字段非空
