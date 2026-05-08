---
task_id: TASK-INF-0129
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
source_section: §22
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC1: GateLifecycle = EXPERIMENTAL→SHADOW→ACTIVE→DEPRECATED→RETIRED 状态机——状态变更记录 changelog"
  - "AC2: Gate version 迁移→version=v1→v2 → `migrate_gate()` 继承旧版本violations逻辑、兼容所有旧gate"
  - "AC3: Gate inheritance→子gate继承父gate检查→加新的violations；rollback子→回弹到父"
  - "AC4: 每个gate维护 `gate_version.yaml` 存储其版本历史"
rollback_instructions:
  - "移除生命周期状态机→全部 gates=ACTIVE; `migrate_gate()` -> no-op; inheritance -> flat list"
created_at: 2026-05-07T00:03:00Z
updated_at: 2026-05-07T00:03:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
blocked_by: [TASK-INF-0101]
blocks: []
tags: [gate-engine, versioning, lifecycle, migration, inheritance]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §22 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§22 门控版本化与生命周期"]
  keywords: [versioning, lifecycle, migration, inheritance, gate-version]
  ai_reads_for_inference: true
---

# TASK-INF-0129: 门控版本化与生命周期管理

实现 GateLifecycle 状态机 + migrate_gate() 版本迁移 + gate 继承。
