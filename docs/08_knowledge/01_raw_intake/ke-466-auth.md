---
module_id: KE-418
status: active
title: 5.3 Auth / 权限注入路径
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 5.3 Auth / 权限注入路径

5.3 Auth / 权限注入路径

```
1. 用户登录 → platform/auth 发起 OIDC → 拿到 JWT
2. JWT 写入 Global Store（只读观察者） + localStorage（可选）
3. data-client 拦截器自动附加 Authorization: Bearer {jwt} 到所有请求
4. WebSocket 连接时把 JWT 作为 subprotocol 或首条消息传给后端
5. JWT 过期 → 静默 refresh → 失败则路由到登录页并清空 Global Store
```

权限模型**当前：单用户单角色**，未来激活 OQ-069 细粒度 RBAC / ABAC 时升级。
