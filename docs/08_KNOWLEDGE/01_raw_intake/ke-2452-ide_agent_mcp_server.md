---
module_id: KE-2357---mcp-server-000
status: active
title: 6.1 IDE/Agent → MCP Server 典型交互
category: module_blueprint
---

# 6.1 IDE/Agent → MCP Server 典型交互

6.1 IDE/Agent → MCP Server 典型交互

```
IDE (Trae/Cursor/Claude Code)
  │
  ├─ stdio connect ──→ MCP Server Process
  │                      │
  │  initialize ───────→│ 返回 capabilities + serverInfo
  │  tools/list ───────→│ 返回注册的全部工具
  │  tools/call ───────→│ 执行工具 → 返回结果
  │                      │
  └─ session end ──────→│ stdin EOF → server 退出
```
