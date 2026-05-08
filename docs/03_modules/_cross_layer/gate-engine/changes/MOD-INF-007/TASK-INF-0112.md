---
task_id: TASK-INF-0112
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 2
category: implementation
effort_estimated: 4h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §26.2
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
  - D:\ZephyrAlpha\src\zephyr\gates\pipeline\evaluator.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\pipeline\evaluator.py
  - D:\ZephyrAlpha\src\zephyr\gates\shadow\shadow_mode.py
  - D:\ZephyrAlpha\src\zephyr\gates\override\emergency_override.py
acceptance_criteria:
  - "AC-DD7: 管线5模式 full/strict/permissive/audit_only/shadow_only — evaluator.py mode_switch 枚举"
  - "AC-DD8: ShadowMode 3 级 warn/reject/log — enrichment functions 分级处理"
  - "AC-DD9: OverrideProtocol 24h 有效期 + 2 人签署÷ SHA256 → forensic→database 永存"
  - "AC-DD10: GateContext Pipeline 注入决定上下文=task_id+model+session_id+timestamp"
  - "AC-DD11: MetaCircuitBreaker 全局跨model熔断——count=0 unified failures≥3?→fallback→sequential=plain仅无AI"
  - "AC-DD12: adaptiveThreshold 仅建议不自动变更——threshold_change_request →人工审批流"
rollback_instructions:
  - "移除管线模式切换逻辑→evaluate_all 固定 full mode；ShadowMode 禁用→warn=log、不阻断；Override→30d有效人工签字；MetaCB→回退到按model独立CB"
created_at: 2026-05-06T23:46:00Z
updated_at: 2026-05-06T23:46:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0111
blocked_by: [TASK-INF-0101, TASK-INF-0111]
blocks: [TASK-INF-0124, TASK-INF-0125, TASK-INF-0126]
tags: [gate-engine, DD7, DD8, DD9, DD10, DD11, DD12, pipeline, shadow, override]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §26.2 DD7-DD12 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§26.2 新设计决策 DD7-DD12"]
  keywords: [DD7, DD8, DD9, DD10, DD11, DD12, pipeline, shadow, emergency-override, GateContext, MetaCircuitBreaker, adaptive-threshold]
  ai_reads_for_inference: true
---

# TASK-INF-0112: DD7-DD12 管线与激活性设计决策实现

## 背景

DD7-DD12 是第二阶段（phase 2）的新设计决策（blueprint.md §26.2），关注管线多模式、影子模式渐进激活、拥有者紧急绕过、GateContext上下文、Meta熔断、自适应阈值建议。

## 实施计划

### DD7: 管线 5 模式
`PipelineMode = Enum('FULL','STRICT','PERMISSIVE','AUDIT_ONLY','SHADOW_ONLY')`。`evaluator.py`→mode_switch→影响evaluate_all的行为（STRICT=no SOFT_BLOCKED、PERMISSIVE=仅硬BLOCKED、SHADOW_ONLY=始终PASSED但记录）。

### DD8: ShadowMode 3 级
`WARN/REJECT/LOG` → `shadow_mode.py` 中的 `ShadowActivation` 配置表。

### DD9: Override Protocol
`EmergencyOverride` 24h有效期 + 2 owner 签名 + sha256(hash)→数据永远保留。

### DD10: GateContext
`GateContext(task_id, model, session_id, timestamp)` 在 pipeline 中传递给每个 gate.check()。

### DD11: Meta CircuitBreaker
跨model统一故障计数→≥3→全model 降级到无AI顺序执行。`meta_circuit_breaker.py` 作为 CircuitBreaker 的超集。

### DD12: Adaptive threshold
阈值变更 = suggest_only → `ThresholdChangeRequest` → 人工审批。自动调整禁用。

## 回退

全部功能回退到管线=full、ShadowMode=off、Override=30d人工签、MetaCB=无、adaptive = 仅log。

## 验收

每DD验收标准见frontmatter AC-DD7~AC-DD12。
