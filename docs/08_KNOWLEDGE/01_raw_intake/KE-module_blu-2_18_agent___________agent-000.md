---
module_id: KE-module_blu-2_18_agent___________agent-000
title: 2.18 Agent 创建权与权限遗传——Agent 派生/复制的权限衰减继承（决策 D-018-16）
category: module_blueprint
---

# 2.18 Agent 创建权与权限遗传——Agent 派生/复制的权限衰减继承（决策 D-018-16）

2.18 Agent 创建权与权限遗传——Agent 派生/复制的权限衰减继承（决策 D-018-16）

> **决策 D-018-16**：Agent 能否创建/派生新的 Agent 实例？如果可以，新 Agent 继承什么权限？如果不可以，靠什么阻止？
>
> **可信主体**：Temporal Durable Execution——WorkflowId + RunId 唯一标识一次执行，防止重复。K8s RBAC——ServiceAccount 的 Token 不可被复制。OAuth2——access_token 不可被转让。

```yaml
