---
module_id: KE-1277--------7-003
status: active
title: 1. 路由决策树（7条规则）
category: module_blueprint
ttl: permanent
---

# 1. 路由决策树（7条规则）

1. 路由决策树（7条规则）

```yaml
routing_decision_tree:
  input: "TaskCard { task_type, priority, target_layer, estimated_complexity }"
  output: "PipelineNode { node_id, execution_model, sandbox_profile, gate_profile }"

  rules:
    - condition: "task_type == MODEL_BUILD AND estimated_complexity == HIGH"
      route: "M1 (DeepSeek V4 Pro + full sandbox + full_g0_g7)"

    - condition: "task_type == MODEL_BUILD"
      route: "M2 (DeepSeek V4 Pro + standard sandbox + pre_commit_only)"

    - condition: "task_type == AUDIT AND priority == P0"
      route: "M3 (DeepSeek V4 Pro 复审 + audit sandbox + full_g0_g7)"

    - condition: "task_type == AUDIT"
      route: "M4 (DeepSeek V4 Pro + audit sandbox + post_exec_only)"

    - condition: "task_type ∈ {DOC_WRITE, REFACTOR} AND target_layer ∈ {L00,L01,L10}"
      route: "M5 (GLM-5.1 + standard sandbox + post_exec_only)"

    - condition: "task_type ∈ {DOC_WRITE, REFACTOR}"
      route: "M6 (DeepSeek V4 Pro + standard sandbox + pre_commit_only)"

    - condition: "task_type == AUTO_FIX"
      route: "M11 (DeepSeek V4 Pro + restricted + none)"
```
