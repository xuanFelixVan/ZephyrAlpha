"""ZephyrAlpha MCP (Model Context Protocol) 子包。

当前已完成：
- task_manager_server.py — decompose_blueprint Tool（蓝图→任务卡拆解）
  其余 3 Tools（create_task / list_tasks / update_status）为 stub——
  依赖 TaskLifecycleManager（步骤 5-6）。
- knowledge_base_server.py — search Tool（知识检索，骨架层）
- gate_engine_server.py — validate Tool（门禁引擎调用，骨架层）
- doc_guard_server.py — audit Tool（文档安全性校验）
- sentinel_server.py — intent_router.map_intent Tool（意图路由哨兵，骨架层）

设计基线：MOD-INF-006 §3.5 MCP 接口 + ADR-0040 Pydantic V2。

**双栈 MCP（病根说明）**：历史 ADR-0033 采用自研 JSON-RPC（``BaseMCPServer``）以便无 SDK
依赖地跑 tools；任务管理 MCP 后因多工具注册冲突与 SDK 成熟度，改用官方 ``FastMCP``。
两条路径均 speak MCP over stdio——属**有意的渐进迁移**，而非实现漏做；新 server 如无强
约束可优先 FastMCP，旧 server 保持稳定即可。
"""
