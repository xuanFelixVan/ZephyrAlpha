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
"""
