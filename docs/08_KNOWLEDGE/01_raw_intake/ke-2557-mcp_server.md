---
module_id: KE-2462------mcp-server-000
status: active
title: 8.1 部署位置：MCP Server 前端拦截
category: module_blueprint
ttl: permanent
---

# 8.1 部署位置：MCP Server 前端拦截

8.1 部署位置：MCP Server 前端拦截

```
   IDE (Cursor/Trae/Claude-Desktop)
        │ MCP request
        ↓
   ┌──────────────────┐
   │ MCP Server       │
   │   ├─ LSG.validate_input(req)   ← 前置拦截
   │   ├─ 真实 MCP 处理              │
   │   └─ LSG.validate_output(resp) ← 后置拦截
   └──────────────────┘
        │
        ↓ （allow=False 时拒绝）
   响应给 IDE
```
