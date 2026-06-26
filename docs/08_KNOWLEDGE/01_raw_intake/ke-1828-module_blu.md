---
module_id: KE-1737---------------------------002
status: active
title: 2.19 缓存一致性——权限变更推送失效 + 降级攻击防护（决策 D-018-17）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.19 缓存一致性——权限变更推送失效 + 降级攻击防护（决策 D-018-17）

2.19 缓存一致性——权限变更推送失效 + 降级攻击防护（决策 D-018-17）

> **决策 D-018-17**：蓝图 §6 R3 提到权限结果缓存（TTL=5min）。如果权限在5分钟内紧急收紧，缓存旧值作为ALLOW放行了——这5分钟是裸奔窗口。改为**推送驱动的缓存失效**。
>
> **可信主体**：Claude Code——权限配置文件变更后强制刷新。K8s RBAC——RBAC变更后API Server cache立即刷新。Redis pub/sub——变更事件 → 所有subscriber立即收到invalidation。

```python
