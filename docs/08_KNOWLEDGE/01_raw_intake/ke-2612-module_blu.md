---
module_id: KE-2517
status: active
title: 9.3 与已有实现的关系
category: module_blueprint
ttl: permanent
---

# 9.3 与已有实现的关系

9.3 与已有实现的关系

- `context_budget_tracker.py`（L1/L2/L3 三级阈值）→ Level 2 的 session 级实现，由 context-engine 管理
- `tool_contracts.yaml`（rate_limit_qps）→ Level 1 的 MCP 工具维度，由 mcp-servers 管理
- 本蓝图 M-21 新增 Level 3/4 的 org/global 级限流 + Pre-flight Estimation

---
