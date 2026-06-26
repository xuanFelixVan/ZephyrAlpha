---
module_id: KE-1346
status: active
title: 10.1 本模块职责完成后
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 10.1 本模块职责完成后

10.1 本模块职责完成后

- 外部 Agent 通过 MCP stdio → 获得生产级质量的任务管理/知识查询/门禁决策/DocGuard/哨兵/蓝图检索能力
- task_manager MCP 作为产物输出方，将 decompose_blueprint 结果交付给 session_handoff → 进入 Agent 执行链路
- knowledge_base MCP 作为知识消费方，为 Agent 提供上下文装配
- gate_engine MCP 作为合规裁决方，输出 G4 契约校验 + G6 蓝图合规判定
- MCP Gateway 作为集中式治理节点，统一审计/降级/限流
