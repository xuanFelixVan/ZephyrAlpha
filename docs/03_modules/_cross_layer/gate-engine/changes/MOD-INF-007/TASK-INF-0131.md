---
task_id: TASK-INF-0131
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
source_section: §24
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC1: AdaptiveThreshold=根据最近N次通过率动态推荐阈值（suggest only, DD12）→ThresholdChangeRequest→人工审批"
  - "AC2: gate_state表={gate_id, current_threshold, n_passed_last_hour, n_blocked_last_hour, last_heatmap, trend}→SQLite持久"
  - "AC3: feedback_loop→每次BLOCKED→检查是否为false_positive→feedback到adaptive threshold实现(P-R)曲线修正"
  - "AC4: temporal_scoping→区分时间窗口(last_hour/last_day/last_week)→不同窗口不同threshold weight"
  - "AC5: 冷启动protect→新gate first 72h auto 的 relaxed threshold→渐进收紧"
rollback_instructions:
  - "AdaptiveThreshold→hardcode固定阈值；gate_state 表→ drop；feedback_loop→no-op；temporal_scoping→single window"
created_at: 2026-05-07T00:05:00Z
updated_at: 2026-05-07T00:05:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0112
blocked_by: [TASK-INF-0101, TASK-INF-0112]
blocks: []
tags: [gate-engine, adaptive, threshold, stateful, feedback, temporal]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §24 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§24 自适应门控与状态记忆"]
  keywords: [adaptive, threshold, stateful, feedback, temporal, cold-start]
  ai_reads_for_inference: true
---

# TASK-INF-0131: 自适应门控与状态记忆实现

AdaptiveThreshold(suggest only)、gate_state持久化、feedback_loop(False Positive修正)、temporal_scoping(时间窗口)、cold_start protection(72h宽松)。
