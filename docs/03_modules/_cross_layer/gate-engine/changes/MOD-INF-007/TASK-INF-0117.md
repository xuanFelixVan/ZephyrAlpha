---
task_id: TASK-INF-0117
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 1
category: implementation
effort_estimated: 2h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §10
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC1: 标准施工流程= load_task→ evaluate task_gates(G0-G7)→if PASS→ execute task→evaluate artifact (G6)→ commit; 若 BLOCKED→stop + reason"
  - "AC2: Add gate = 继承 Gate(base), 实现 check()→ 注册到 gate_chain；不应修改其余代码"
  - "AC3: Modify gate 门槛=只改 gate check()实现；加acceptance_test"
  - "AC4: 每个 Gate 新增后，需更新 Gate 实现依赖索引（已放入 blueprint.md 的施工流水）"
rollback_instructions:
  - "退回施工流程至仅执行task,不调用GateEngine。实施方法删除新增 gate→从注册延续中移除"
created_at: 2026-05-06T23:51:00Z
updated_at: 2026-05-06T23:51:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0102
blocked_by: [TASK-INF-0101, TASK-INF-0102]
blocks: []
tags: [gate-engine, construction-guide, add-gate, modify-gate, workflow]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §10 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§10 施工与演化指南"]
  keywords: [construction, workflow, add-gate, modify-gate, gate-chain, register]
  ai_reads_for_inference: true
---

# TASK-INF-0117: 标准施工流程与演化指南落地

## 背景

blueprint.md §10 定义了添加和修改 gate 的标准施工边界——新增 gate=只加一行注册+实现check()、修改 gate=不改其余模块。

## 实施

1. 在 `GateEngine` 中固化 `gate_chain` 作为注入参数。
2. 标准执行流通用模板：load → evaluate_all → if PASSED: execute → evaluate_g6 → commit；else: reject。
3. 新 Gate 开发只需继承 `Gate` base class，实现 `check()`，实例化后加入 gate_chain 即可。

## 验收

- AC1: 标准流程可自动化执行
- AC2: 新增 gate 无需动 GateEngine 本体
- AC3: 修改 gate 仅改该 gate 的 check()
- AC4: 索引更新记录
