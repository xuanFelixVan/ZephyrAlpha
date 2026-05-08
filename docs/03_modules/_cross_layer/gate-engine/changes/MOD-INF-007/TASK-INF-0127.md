---
task_id: TASK-INF-0127
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
source_section: §20
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\pipeline\evaluator.py
acceptance_criteria:
  - "AC1: 每gate SLI=pass_rate、avg_latency_ms、block_reason_distribution、false_positive_rate——收集并推送到 telemetry"
  - "AC2: AuditSchema 扩展={gate_decision_id, gate_name, status, violations, timestamp, hash, model, session_id}  → 存入 audit.db"
  - "AC3: Gate change tracking=任何 gate 配置修改→ 触发 change_event 记录（旧/新/why）
  - "AC4: Per gate dashboard metrics——通过 `gate-health` CLI 呈现"
rollback_instructions:
  - "移除 AuditSchema 扩展→回退到旧版 audit schema; gate SLI metrics → no-op (只是记录上的$$)"
created_at: 2026-05-07T00:01:00Z
updated_at: 2026-05-07T00:01:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0104
blocked_by: [TASK-INF-0101, TASK-INF-0104]
blocks: [TASK-INF-0132]
tags: [gate-engine, observability, SLI, audit, metrics, dashboard]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §20 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§20 门控可观测性与审计完整性"]
  keywords: [observability, SLI, audit, metrics, dashboard, change-tracking]
  ai_reads_for_inference: true
---

# TASK-INF-0127: 门控可观测性与审计完整性

实现 per-gate SLI metrics+AuditSchema 扩展+config change tracking。
