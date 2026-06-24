---
module_id: KE-1571
status: active
title: 17.1 评估管线模型
category: module_blueprint
---

# 17.1 评估管线模型

17.1 评估管线模型

当前`evaluate(task, gate_id)`是点对点调用——Orchestrator每次调一个门禁。16+门禁需管线化：

```
                    Gate Pipeline
TaskCard.status  →  [G0] ──→ [G1,G2,G3] ──→ [G4,G5,G6] ──→ [G7]
 transition        准入      施工前并行       执行中并行      交付前

PipelineMode: single | parallel_and | parallel_or | sequential | weighted
```

```yaml
gate_pipeline:
  stages:
    - stage: entry
      mode: single
      gates: [G0]
      on_fail: "任务留在DRAFT"
    - stage: pre_exec
      mode: parallel_and
      gates: [G1, G2, G3]
      on_fail: "任务→BLOCKED，有fix_hint的进入deferred_queue"
    - stage: during_exec
      mode: parallel_and
      gates: [G4, G5, G6]
      on_fail: "中断执行 + status→FAILED"
    - stage: delivery
      mode: single
      gates: [G7]
      on_fail: "任务→BLOCKED，修复后重新触发G7判定"
  inter_gate_dependencies:
    - {prerequisite: G6, dependent: G7, rule: "G6 must PASS before G7 evaluation"}
    - {prerequisite: G1, dependent: G2, rule: "G1 rejected → skip G2"}
```
