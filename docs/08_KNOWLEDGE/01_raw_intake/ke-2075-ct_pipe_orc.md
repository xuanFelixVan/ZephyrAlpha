---
module_id: KE-1984--------ct-pipe-orc-001-003
status: active
title: 3. 路由决策树（CT-PIPE-ORC-001 落地）
category: module_blueprint
---

# 3. 路由决策树（CT-PIPE-ORC-001 落地）

3. 路由决策树（CT-PIPE-ORC-001 落地）

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

  claude_rescue_triggers:
    - "DeepSeek 失败次数 ≥ 3"
    - "GLM 驳回次数 ≥ 2"
    - "Owner 标记 critical/unsafe"
    - "security 标签"
    - "experimental 标签"

  affinity_enforcement:            # §2.5 约束矩阵落地
    - check: "M3.model == M7.model"
      on_violation: "ABORT + escalate: 双盲审查模型冲突——M3{model} 与 M7{model} 必须不同"
    - check: "M8.model != M9.model"
      on_violation: "WARN: 建议 M8/M9 使用不同模型交叉覆盖"
```

---
