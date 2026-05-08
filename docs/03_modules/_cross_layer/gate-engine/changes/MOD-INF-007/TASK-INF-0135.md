---
task_id: TASK-INF-0135
status: planned
priority: P0
severity: critical
module_id: MOD-INF-007
phase: 3
category: implementation
effort_estimated: 3h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §28
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC1: GateEngineIntegrityGuard → check_gate_engine (self)->验证 gate_engine源码快照hash—hash mismatched → 触发 ALERT(proceeds_blocked)"
  - "AC2: trust_root_hierarchy 护={ TrustRoot. GATE_1(engine gui的线)=  zeph_origin (lowest verifiable root)}→ hash chain追溯完整性"
  - "AC3: GATE-18 linkage→Rule chain applied→ self-check clustered → GATE_18 Active= True in evaluator"
rollback_instructions:
  - "IntegrityGuard → disable: 无check；trust_root התע Dereference = 断开级hash履"
created_at: 2026-05-07T00:09:00Z
updated_at: 2026-05-07T00:09:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0113
  - TASK-INF-0134
blocked_by: [TASK-INF-0101, TASK-INF-0113]
blocks: []
tags: [gate-engine, self-referential, hardening, integrity-guard, trust-root]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §28 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§28 自我指涉硬化"]
  keywords: [self-referential, hardening, integrity, trust-root, GATE-18]
  ai_reads_for_inference: true
---

# TASK-INF-0135: 自我指涉硬化实现

GateEngineIntegrityGuard(self-hash)、trust_root_hierarchy(多层校验，最低orig可root)、GATE-18 linkage。
