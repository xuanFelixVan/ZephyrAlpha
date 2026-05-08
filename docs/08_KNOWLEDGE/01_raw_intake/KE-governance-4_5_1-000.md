---
module_id: KE-governance-4_5_1-000
title: 4.5.1 触发条件
category: governance
---

# 4.5.1 触发条件

4.5.1 触发条件

- **KMS 管道显式触发**：`GateEngine.evaluate(task, "G5")`
- **前置条件**：G4 PASS；`doc.gate_status ∈ {'passed_g4', 'active'}`
