---
task_id: TASK-INF-0132
status: planned
priority: P2
severity: medium
module_id: MOD-INF-007
phase: 2
category: implementation
effort_estimated: 3h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §25
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\pipeline\evaluator.py
acceptance_criteria:
  - "AC1: GateHealthDashboard=per gate UI显示 pass_rate/avg_latency/block_top_3_reasons/current_state/adaptive_threshold"
  - "AC2: `gate-health` CLI 输出可读 table+JSON(供AI自动消费)"
  - "AC3: Dashboard 数据来源于 evaluator stats(§17) 和 adaptive state(§24)"
rollback_instructions:
  - "Dashboard→返回空.json; CLI→不主动安装"
created_at: 2026-05-07T00:06:00Z
updated_at: 2026-05-07T00:06:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0124
  - TASK-INF-0127
  - TASK-INF-0131
blocked_by: [TASK-INF-0101, TASK-INF-0124, TASK-INF-0127, TASK-INF-0131]
blocks: []
tags: [gate-engine, dashboard, health, CLI, JSON]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §25 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§25 门控健康仪表板"]
  keywords: [dashboard, health, CLI, JSON, AI-consumable]
  ai_reads_for_inference: true
---

# TASK-INF-0132: 门控健康仪表板实现

GateHealthDashboard: per_gate UI + `gate-health` CLI (table+JSON)。
