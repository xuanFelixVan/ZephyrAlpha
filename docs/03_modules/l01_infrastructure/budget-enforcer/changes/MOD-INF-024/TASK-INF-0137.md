---
task_id: "TASK-INF-0137"
module_id: "MOD-INF-024"
title: "Construction Phase Gate & Pipeline — 6 Phase: scaffold→experimental→sandbox→beta→v0_7_0→self_calibrating 全生命周期门禁与 CI/CD 集成（§5 + 全局）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§5"
estimated_tokens: 5000
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101~0136"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\.trae\\rules\\project_rules.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\phase_manifest.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\phase_gate_check.py"
acceptance_criteria:
  - "AC-01: scaffold phase——12 task cards (TASK-INF-0101,0102,0103,0106,0112,0113,0119,0120,0121,0135,0137,0138) 全部完成 → gate open to experimental"
  - "AC-02: experimental phase——10 task cards (TASK-INF-0104,0105,0107,0111,0114,0122,0123,0128,0132,0133) 全部完成 → gate open to sandbox"
  - "AC-03: sandbox phase——2 task cards (TASK-INF-0115,0129) 全部完成 → gate open to beta"
  - "AC-04: beta phase——7 task cards (TASK-INF-0108,0109,0110,0116,0117,0118,0124) 全部完成 → gate open to v0_7_0"
  - "AC-05: v0_7_0 phase——3 task cards (TASK-INF-0125,0126,0127) 全部完成 → gate open to self_calibrating"
  - "AC-06: self_calibrating phase——4 task cards (TASK-INF-0130,0131,0134,0136) 全部完成 → ALL PHASES COMPLETE"
  - "AC-07: phase_manifest.yaml——phase_gates 定义 6 个 Phase 的 task_ids 列表"
  - "AC-08: phase_gate_check.py——可执行脚本验证当前 phase 内所有 task.status=Done"
  - "AC-09: CI/CD pipeline (MOD-INF-009) 集成 phase gate check——next phase disabled until current phase complete"
  - "AC-10: weekly gate audit——生成 construction_progress.md 展示各 phase 完成百分比"
  - "AC-11: rollback_phase——阶段级回滚：rollback to previous phase if current phase gate fails × 3+"
rollback_instructions: "删除 phase_manifest.yaml + phase_gate_check.py。系统退化为无 Phase 结构化——所有 task 平等 Backlog 无严格顺序"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1457-L1458 (§5 Construction Phase planning)"
  fallback:
    - "D:\\ZephyrAlpha\\.trae\\rules\\project_rules.md"
assigned_agent: any
tags: [phase-gate, pipeline, ci-cd, gate-check, six-phases, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0137: Construction Phase Gate & Pipeline

## 1. 任务目标

实现 Budget Enforcer 六个施工 Phase 的生命周期门禁：scaffold → experimental → sandbox → beta → v0_7_0 → self_calibrating。每个 Phase 有明确的 task_id 列表，gate check 验证全部通过后才允许晋级下一 Phase。同步集成 CI/CD Pipeline。

## 2. 背景

蓝图 §5 定义两阶段施工（scaffold + v2.0）。蓝图各接口定义 selftest_gate 和 rollback_gate 验证各 Phase。Phase 完工后附带 completion report 与 handover artifacts。

## 3. 实施步骤

### phase_manifest.yaml 结构
```yaml
phases:
  scaffold:
    order: 1
    tasks: [TASK-INF-0101,0102,0103,0106,0112,0113,0119,0120,0121,0135,0137,0138]
    downstream_consumers: [experimental]
  experimental:
    order: 2
    tasks: [TASK-INF-0104,0105,0107,0111,0114,0122,0123,0128,0132,0133]
    downstream_consumers: [sandbox]
  sandbox:
    order: 3
    tasks: [TASK-INF-0115,0129]
    downstream_consumers: [beta]
  beta:
    order: 4
    tasks: [TASK-INF-0108,0109,0110,0116,0117,0118,0124]
    downstream_consumers: [v0_7_0]
  v0_7_0:
    order: 5
    tasks: [TASK-INF-0125,0126,0127]
    downstream_consumers: [self_calibrating]
  self_calibrating:
    order: 6
    tasks: [TASK-INF-0130,0131,0134,0136]
    downstream_consumers: []
```

### phase_gate_check.py 逻辑
```python
class PhaseGateChecker:
    def __init__(self, manifest_path: str):
        self.manifest = yaml.safe_load(open(manifest_path))

    def check_phase(self, phase: str) -> GateStatus:
        required_tasks = self.manifest["phases"][phase]["tasks"]
        statuses = {tid: self._get_status(tid) for tid in required_tasks}
        all_done = all(s == "Done" for s in statuses.values())
        return GateStatus(phase, all_done, statuses)

    def next_phase_allowed(self, current_phase: str) -> bool:
        # Check all current Phase tasks Done
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/phase_manifest.yaml` | 新建 |
| 2 | `src/zephyr/budget_enforcer/phase_gate_check.py` | 新建 |
