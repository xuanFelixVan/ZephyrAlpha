---
module_id: KE-924
status: active
title: 4.5.1 触发条件
category: governance
---

# 4.5.1 触发条件

4.5.1 触发条件

- **KMS 管道显式触发**：`GateEngine.evaluate(task, "G5")`
- **前置条件**：G4 PASS；`doc.gate_status ∈ {'passed_g4', 'active'}`
