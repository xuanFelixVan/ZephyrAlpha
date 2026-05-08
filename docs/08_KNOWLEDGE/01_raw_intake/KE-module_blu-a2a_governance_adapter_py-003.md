---
module_id: KE-module_blu-a2a_governance_adapter_py-003
title: a2a_governance_adapter.py
category: module_blueprint
---

# a2a_governance_adapter.py

a2a_governance_adapter.py
- `A2ASecurityContext` 类（Agent身份 + 操作目标 + 权限级别）
- `Authorizer`：调用 MOD-INF-018 RBAC 检查
- `EscalationBridge`：arbitrator.py escalate 层的契约适配
- `AuditFormatter`：A2A 事件格式化为 MOD-INF-020 兼容格式
