---
module_id: KE-1533-----ai-002
status: active
title: 15.1 AGENTS.md 硬约束（AI 冷启动零次理解成本）
category: module_blueprint
ttl: permanent
---

# 15.1 AGENTS.md 硬约束（AI 冷启动零次理解成本）

15.1 AGENTS.md 硬约束（AI 冷启动零次理解成本）

1. MCP 模块的 canonical 真源是 `b_mcp.yaml` + `tool_contracts.yaml`
2. MCP Server 的 server_id 不可改——它是 MCP 协议契约
3. 新增 MCP tool 必须先改 `tool_contracts.yaml` 再写代码
4. MCP Server 日志强制走 `structlog` + `sys.stderr`（禁止 `print()` 到 stdout）
5. IDE 配置由 `config/mcp.json` SSoT 生成，不手写各 IDE 目录下的 mcp.json
6. blueprint_search 是 vibe coding 场景的「上下文导航器」——新增蓝图后更新 `config/blueprint_routing.yaml`
