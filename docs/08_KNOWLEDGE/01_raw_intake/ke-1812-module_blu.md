---
module_id: KE-1721---------------------------000
status: active
title: 2.16 冷启动锁——启动时全局拒绝直到权限配置加载（决策 D-018-14）
category: module_blueprint
ttl: permanent
---

# 2.16 冷启动锁——启动时全局拒绝直到权限配置加载（决策 D-018-14）

2.16 冷启动锁——启动时全局拒绝直到权限配置加载（决策 D-018-14）

> **决策 D-018-14**：蓝图 §6 R15 提出了"崩=blocked"原则，但关键空白是——rbac_roles.yaml 在加载之前的状态是什么？如果在 `immutable_core.py` 等组件就绪前面已经有 Agent 在操作，等于裸奔窗口。
>
> **可信主体**：Flyway/Liquibase——migration 执行前先 validate preconditions。K8s RBAC——Pod 启动前先校验 ServiceAccount。Claude Code——配置加载完成前不执行任何操作。

```python
