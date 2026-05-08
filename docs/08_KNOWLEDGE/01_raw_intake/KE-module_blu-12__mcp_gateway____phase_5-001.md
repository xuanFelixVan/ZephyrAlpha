---
module_id: KE-module_blu-12__mcp_gateway____phase_5-001
title: 12. MCP Gateway 架构（Phase 5）
category: module_blueprint
---

# 12. MCP Gateway 架构（Phase 5）

12. MCP Gateway 架构（Phase 5）

```
外部 IDE/Agent
  │
  ├─ Trae IDE ──────────┐
  ├─ Cursor IDE ────────┤
  └─ Claude Code ───────┘
           │
           ▼
    ┌──────────────┐
    │  MCP Gateway  │ ← 集中式入口
    │  ┌──────────┐ │
    │  │ Auth/ACL │ │ ← 认证+授权（MOD-INF-018）
    │  ├──────────┤ │
    │  │ RateLimit│ │ ← 限流（10 req/s per client）
    │  ├──────────┤ │
    │  │  Route   │ │ ← 7 Server 路由分发
    │  ├──────────┤ │
    │  │  Audit   │ │ ← 全量工具调用审计日志
    │  ├──────────┤ │
    │  │Degrade   │ │ ← 降级策略（Circuit Breaker）
    │  └──────────┘ │
    └──────┬─────────┘
           │
    ┌──────┼──────────────────────────┐
    ▼      ▼      ▼      ▼      ▼     ▼
  task_  knowl-  gate_  sess-  inte-  blue-
  mgr    edge    eng    ion    nt     print
```

---
