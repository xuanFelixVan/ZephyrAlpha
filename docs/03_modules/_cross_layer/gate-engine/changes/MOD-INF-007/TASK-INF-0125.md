---
task_id: TASK-INF-0125
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 2
category: implementation
effort_estimated: 3h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §18
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\pipeline\evaluator.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\shadow\shadow_mode.py
acceptance_criteria:
  - "AC1: 3 Level激活: warn/reject/log — `ShadowMode.level` 枚举控制——每个 Level 输出不同 GateResult.ShadowDecision"
  - "AC2: Progressive activation=warn(0-72h)→reject(72h-168h)→fully_enforced(>168h)——由`shadow_activation_schedule.yaml`控制"
  - "AC3: GateSimulator= `DryRunGateEngine` 用shadow 模式对历史任务回放——输出 shadow_decision+delta 分析"
rollback_instructions:
  - "ShadowMode禁用——返回 NO_SHADOW_ACTIVE，GateSimulator 关机→删除 shadow/目录"
created_at: 2026-05-06T23:59:00Z
updated_at: 2026-05-06T23:59:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0112
  - TASK-INF-0124
blocked_by: [TASK-INF-0101, TASK-INF-0112, TASK-INF-0124]
blocks: []
tags: [gate-engine, shadow-mode, progressive-activation, gate-simulator]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §18 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§18 Shadow 模式与渐进激活"]
  keywords: [shadow, progressive, activation, simulator, warn, reject, log]
  ai_reads_for_inference: true
---

# TASK-INF-0125: Shadow 模式与渐进激活实现

## 背景

Shadow Mode（影子模式）允许新gate在不阻塞生产的同时观察其行为（blueprint.md §18）。三阶段渐进激活：warn→reject→hard-enforce。

## 实施

```python
class ShadowMode:
    level: ShadowLevel  # WARN / REJECT / LOG

    def evaluate_shadow(self, gate, context):
        if self.level == ShadowLevel.LOG:
            return ShadowDecision(action="LOG", result=gate.check(context))
        elif self.level == ShadowLevel.WARN:
            return ShadowDecision(action="WARN", result=gate.check(context))
        elif self.level == ShadowLevel.REJECT:
            result = gate.check(context)
            return ShadowDecision(action="REJECT" if result.status==BLOCKED else "PASS", result=result)
```

激活时间表从 `shadow_activation_schedule.yaml` 加载。

GateSimulator 用于回放历史任务，输出影子对比分析。
