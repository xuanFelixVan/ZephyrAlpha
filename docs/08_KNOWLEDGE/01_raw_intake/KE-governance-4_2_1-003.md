---
module_id: KE-governance-4_2_1-003
title: 4.2.1 触发条件
category: governance
---

# 4.2.1 触发条件

4.2.1 触发条件

- **状态机触发**（未来扩展）：`IN_PROGRESS→COMPLETED`
- **显式触发**：`GateEngine.evaluate(task, "G2")`
- **前置条件**：G1 PASS，task 已带上 `classification` / `doc_type` / `priority`
