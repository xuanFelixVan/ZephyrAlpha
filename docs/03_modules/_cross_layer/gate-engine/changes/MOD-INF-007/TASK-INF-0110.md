---
task_id: TASK-INF-0110
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
source_section: §5.4
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  - D:\ZephyrAlpha\docs\01_policies_and_standards\governance\task\task-closure-standard.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_result.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g7_delivery.py
acceptance_criteria:
  - "AC1: G7_DELIVERY_YAML gate_name='Task-G7: Delivery Gate'、gate_level='G7'、required_context=['acceptance_criteria','zalp_errors','task_card_md','task_repo_mm']、check_method='verify_delivery_completeness'"
  - "AC2: 三步验证：1→所有AC全部通过（acceptance_criteria 无'SKIPPED'/'FAILED'）、2→ZALP-error count=0、3→task_repo SQLite 与 .md 双轨字段一致（task_id/status/priority/severity/effort_estimated/closed_at一致）"
  - "AC3: 任何一步不通过→BLOCKED，violations 精确指出是第几步失败"
rollback_instructions:
  - "g7_delivery.py→空桩→check_all() 返回 GateResult.PASSED"
created_at: 2026-05-06T23:44:00Z
updated_at: 2026-05-06T23:44:00Z
closed_at: null
dependencies:
  - TASK-INF-0102
  - TASK-INF-0104
blocked_by: [TASK-INF-0102, TASK-INF-0104]
blocks: []
tags: [gate-engine, G7, delivery-gate, AC-validation, dual-track]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 初始创建，基于 blueprint.md §5.4 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§5.4 G7 交付门控"]
  keywords: [G7, delivery, acceptance-criteria, ZALP, dual-track, consistency]
  ai_reads_for_inference: true
---

# TASK-INF-0110: G7 交付门控结构化 YAML 规则落地

## 背景与动机

G7 Delivery Gate 是任务生命周期的最终门——确保任务在关闭前 AC 全部通过、ZALP 错误清零、task_repo 与 .md 双轨一致（blueprint.md §5.4）。G7 不通过的任务不允許进入 archived 状态。

## 实施计划

### G7 YAML 规则

```yaml
gate_name: "Task-G7: Delivery Gate"
gate_level: "G7"
required_context: ["acceptance_criteria", "zalp_errors", "task_card_md", "task_repo_mm"]
check_method: "verify_delivery_completeness"
checks:
  step1_ac_pass: "所有AC status=passed"
  step2_zalp_clean: "zalp_error_count==0"
  step3_dual_track: "task_repo与.md字段一致"
```

### Python 实现

```python
class G7DeliveryGate(Gate):
    def check_all(self, task_dict: dict) -> GateResult:
        violations = []
        # Step 1: AC 全部通过
        ac_list = task_dict.get("acceptance_criteria", [])
        if any("FAILED" in str(ac) or "SKIPPED" in str(ac) for ac in ac_list):
            violations.append("G7-STEP1: Not all AC passed")
        # Step 2: ZALP 零错误
        if task_dict.get("zalp_error_count", 0) != 0:
            violations.append("G7-STEP2: ZALP errors remain")
        # Step 3: 双轨一致
        md_fields = {k: task_dict.get(k) for k in ["task_id","status","priority","severity","effort_estimated","closed_at"]}
        repo_fields = task_dict.get("task_repo_fields", {})
        if md_fields != repo_fields:
            violations.append(f"G7-STEP3: Dual-track mismatch: md={md_fields}, repo={repo_fields}")
        if violations:
            return GateResult(status=GateStatus.BLOCKED, gate_level="G7", violations=violations)
        return GateResult(status=GateStatus.PASSED, gate_level="G7")
```

## 回退方案

空桩即可——`g7_delivery.py` 的 `check_all()` 返回 `GateResult.PASSED`。

## 验收标准

| # | 标准 |
|---|------|
| AC1 | YAML 含 gate_name/level/context/method + 三步 check |
| AC2 | AC 含 FAILED→BLOCKED(STEP1)；ZALP>0→BLOCKED(STEP2)；双轨不一致→BLOCKED(STEP3) |
| AC3 | violations 精确指出步骤编号 |
