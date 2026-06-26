---
module_id: KE-4062
title: 3.3 MCP 原语覆盖
category: module_blueprint
ttl: permanent
---

# 3.3 MCP 原语覆盖

3.3 MCP 原语覆盖

| 原语 | 实现状态 | 备注 |
|------|:---:|------|
| `initialize` | ✅ | BaseMCPServer 和 FastMCP 均支持 |
| `ping` | ✅ | BaseMCPServer 支持 |
| `tools/list` | ✅ | 返回所有注册工具 |
| `tools/call` | ✅ | 基础实现，缺 safety_level + timeout |
| `resources/list` | ✅ | resource_provider.py 已实现 |
| `resources/read` | ✅ | resource_provider.py read() 已实现 |
| `prompts/list` | ✅ | prompt_provider.py 已实现 |
| `prompts/get` | ✅ | prompt_provider.py get() 已实现 |
| `notifications/message` | ❌ | 未实现（Server→Client 通知） |
