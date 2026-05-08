---
module_id: KE-governance-suspended-000
title: suspended
category: governance
---

# suspended

suspended

模块被 Owner 主动暂停，不进行任何操作。

- 触发条件：外部依赖不可用、业务需求暂停、等待上游条件满足
- 必须有：暂停原因记录在 Session Log 中
- 恢复路径：suspended → active（原因消除后，Owner 审批恢复，不创建新 module_id）
- 禁止：新功能开发、接口变更
- 暂停期间仍须响应安全补丁
