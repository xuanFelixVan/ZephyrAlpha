---
module_id: KE-919
status: active
title: 4.4.1 触发条件
category: governance
ttl: permanent
---

# 4.4.1 触发条件

4.4.1 触发条件

- **KMS 管道显式触发**：`GateEngine.evaluate(task, "G4")`（task 已达 `VERIFIED`；G4 不属状态机转换，属激活动作前的守卫）
- **前置条件**：G3 PASS，task 已解析依赖图 `doc.dependencies`
