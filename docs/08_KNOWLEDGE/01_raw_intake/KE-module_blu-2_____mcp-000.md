---
module_id: KE-module_blu-2_____mcp-000
title: 2. 七个 MCP 服务端
category: module_blueprint
---

# 2. 七个 MCP 服务端

2. 七个 MCP 服务端

| 服务端 | 文件名 | server_id | 实现状态 | 暴露能力 |
|------|------|------|:---:|------|
| **task_manager** | `task_manager_server.py` | `task_manager` | ✅ 已实现 | 蓝图→任务卡拆解、任务 CRUD |
| **knowledge_base** | `knowledge_base_server.py` | `knowledge_base` | ✅ functional | KE 查询/创建、健康检查（内存存储） |
| **gate_engine** | `gate_engine_server.py` | `gate_engine` | ✅ functional | Gate 判定/熔断状态 |
| **session_handoff** | `doc_guard_server.py` | `session_handoff` | ✅ functional | 文档安全校验（文件名与 server_id 不同！） |
| **intent_router** | `sentinel_server.py` | `intent_router` | ✅ functional | 系统哨兵监控/指标（文件名与 server_id 不同！） |
| **blueprint_search** | `blueprint_search_server.py` | `blueprint_search` | ✅ 已实现 | 蓝图检索（P0-2 experimental） |
| **sandbox** | `sandbox_server.py` | `sandbox` | ✅ 已实现 | 安全代码执行沙箱（subprocess 隔离） |

> ⚠️ **文件命名 vs server_id 不一致**：`doc_guard_server.py` 的 server_id 是 `session_handoff`，`sentinel_server.py` 的 server_id 是 `intent_router`。这是已知差异，不可"修正"文件名——server_id 是 MCP 协议契约中的标识，不能改。

---
