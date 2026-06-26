---
module_id: KE-1938---003
status: active
title: 2.7 CT-PIPE-ORC-001：Pipeline ↔ Orchestrator
category: module_blueprint
ttl: permanent
---

# 2.7 CT-PIPE-ORC-001：Pipeline ↔ Orchestrator

2.7 CT-PIPE-ORC-001：Pipeline ↔ Orchestrator

```yaml
contract: CT-PIPE-ORC-001
title: "任务 → 管线节点路由"
systems:
  - role: router
    name: pipeline
    path: "src/zephyr/pipeline/"
    blueprint: "MOD-INF-009"
  - role: consumer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-INF-006"

routing:
  input: "TaskCard { task_type, priority, target_layer, estimated_complexity }"
  output: "PipelineNode { node_id: M1-M11, execution_model, sandbox_profile, gate_profile }"

  decision_tree: |
    if task_type == MODEL_BUILD:
      if estimated_complexity == HIGH → M1 (Opus 4.5, full sandbox)
      else → M2 (GPT-5.2, standard sandbox)
    if task_type == AUDIT:
      if priority == P0 → M3 (Opus 4.5 复审, audit sandbox)
      else → M4 (Claude 4.5 Sonnet, audit sandbox)
    if task_type ∈ {DOC_WRITE, REFACTOR}:
      if target_layer ∈ {L00,L01,L10} → M5 (GPT-5.2, full sandbox)
      else → M6 (Claude 4.5 Sonnet, standard sandbox)

pipeline_output:
  node_id: "M1-M11"
  execution_model: "enum[opus-4.5, gpt-5.2, claude-4.5-sonnet, claude-4.5-haiku, gemini-3.0-pro, qwen-3-max, glm-5.1]"
  sandbox_profile: "enum[full, standard, audit, restricted]"
  gate_profile: "enum[full_g0_g7, pre_commit_only, post_exec_only, none]"

ai_prompt: >
  你是CT-PIPE-ORC-001的AI agent。当你需要为TaskCard选择管线路由时：
  (1) 输入TaskCard的task_type+priority+target_layer+estimated_complexity→输出M1-M11节点；
  (2) MODEL_BUILD+高复杂度→M1(Opus 4.5)，AUDIT→M3/M4，OPS→M2——严格按照decision_tree路由；
  (3) 路由输出必须包含完整的PipelineNode：node_id + execution_model + sandbox_profile + gate_profile；
  (4) A-zone(M1-M5)产出物不得直接流入B-zone(M6-M11)——必须经过M6边界标记（AP2）；
  (5) 不要因为"某模型当前不可用"而私自改变路由——模型不可用应触发FLE而非静默改路由。

telemetry:
  metrics:
    - {name: "pipe_routing_decision_count", type: counter, labels: [task_type, node_id]}
    - {name: "pipe_routing_latency_ms", type: histogram, buckets: [1,5,10,50]}
    - {name: "pipe_zone_crossing_count", type: counter, labels: [from_zone, to_zone]}
  traces:
    required_spans: ["pipe_receive_taskcard", "pipe_route_decision", "pipe_emit_node"]
```
