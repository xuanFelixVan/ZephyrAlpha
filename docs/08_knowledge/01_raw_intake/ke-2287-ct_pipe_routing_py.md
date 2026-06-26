---
module_id: KE-2193
status: active
title: 4. ct_pipe_routing.py 核心函数
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4. ct_pipe_routing.py 核心函数

4. ct_pipe_routing.py 核心函数

- `resolve_route(task_card: TaskCard) -> PipelineRouteDecision`：根据路由决策树选择 M 节点
- `check_claude_rescue(context: RescueContext) -> bool`：判断是否需要 Claude 救援
- `extract_target_layer(task_card: TaskCard) -> str`：从 TaskCard hints 提取 target_layer
- `enforce_affinity(decision: PipelineRouteDecision, active_nodes: dict) -> list[str]`：校验 affinity 约束
