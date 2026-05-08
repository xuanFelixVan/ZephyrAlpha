---
task_id: TASK-INF-0126
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 2
category: implementation
effort_estimated: 2h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §19
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_result.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\override\emergency_override.py
acceptance_criteria:
  - "AC1: EmergencyOverrideGate 24h有效期+双人签署（owner_1+owner_2）→SHA256签名永存数据库"
  - "AC2: 覆写条件严格：仅 emergency_level≥P0、override_window 内活动→其余拒绝"
  - "AC3: `emergency_override_log` SQLite 持久化——地址 id+timestamp+signed_by+hash+reason 不可删"
  - "AC4: `evaluate_override(gate_blocked_list)` 需 GateEngine 预检原 BLOCKED 结果→对照覆写签名"
rollback_instructions:
  - "禁用 EmergencyOverrideGate 所有路径→GateEngine 不调用 override gate→ 原 BLOCKED 永远不被覆写"
created_at: 2026-05-07T00:00:00Z
updated_at: 2026-05-07T00:00:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0112
blocked_by: [TASK-INF-0101, TASK-INF-0112]
blocks: []
tags: [gate-engine, emergency-override, bypass, forensic]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §19 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§19 业主紧急绕过（Owner Emergency Bypass）"]
  keywords: [emergency, override, bypass, double-sign, 24h, forensic]
  ai_reads_for_inference: true
---

# TASK-INF-0126: 业主紧急绕过协议实现

实现 EmergencyOverrideGate：24h 时效窗口 + 双人签署 + 永久审计日志。
