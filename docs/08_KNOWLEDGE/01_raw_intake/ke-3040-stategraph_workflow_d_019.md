---
module_id: KE-2940
status: active
title: StateGraph Workflow (D-019-31)
category: module_blueprint
ttl: permanent
---

# StateGraph Workflow (D-019-31)

StateGraph Workflow (D-019-31)
- StateGraph 强制编排: 图中不存在跳过 gate 的边
- Durable Execution: per-gate Checkpoint → 中断恢复 < 5s
- Supervisor Pattern: Governor 全局监督
