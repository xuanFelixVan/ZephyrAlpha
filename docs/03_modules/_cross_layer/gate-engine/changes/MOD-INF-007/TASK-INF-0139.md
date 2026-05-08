---
task_id: TASK-INF-0139
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 3
category: implementation
effort_estimated: 3h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §32
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC1: key_management=私钥90d rotation→签名验证(public key verify)→过期key记录持久化"
  - "AC2: snapshot_lifecycle=决策快照(DecisionSnapshot)→>30d archive→压缩±Ⅱ encrypt→ commit storage policy"
  - "AC3: cross_gate_consistency=Gate X output→check 与 Gate Y input contract(CT)-consistentOn mismatch→add violation+type_mismatch_warning"
  - "AC4: self_upgrade_protocol=gate_version upgrade→canary deploy 10% first→ observe→ постепен rollout"
rollback_instructions:
  - "key_mgmt assessment→ no rotate；snapshot lifecycle→ unlimited retention+ no archive； cross_gate →no_consistency； self_upgrade → upgrade does-1-hop"
created_at: 2026-05-07T00:13:00Z
updated_at: 2026-05-07T00:13:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0134
  - TASK-INF-0138
blocked_by: [TASK-INF-0101, TASK-INF-0134, TASK-INF-0138]
blocks: []
tags: [gate-engine, edge-convergence, key-management, snapshot-lifecycle, cross-gate, self-upgrade]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §32 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§32 边缘收敛——末段细节全部收敛"]
  keywords: [edge-convergence, key-management, rotation, snapshot-lifecycle, consistency, self-upgrade, canary]
  ai_reads_for_inference: true
---

# TASK-INF-0139: 边缘收敛实现

Key Management(90d轮转)、Snapshot Lifecycle(>30d archive+encrypt)、Cross-gate Consistency(type contract校验)、Self-upgrade Protocol(canary 10% first)。
