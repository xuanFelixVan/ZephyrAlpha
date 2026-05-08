---
task_id: TASK-INF-0107
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
source_section: §5.1
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_result.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g0_entry.py
acceptance_criteria:
  - "AC1: G0EntryGate YAML 规则定义 gate_name='Task-G0: Entry Validation'、gate_level='G0'、required_context=['task_card_dict']"
  - "AC2: check_all(task_dict) 验证 task_id 非空、priority∈{P0,P1,P2,P3,P4}、status∈[planned,in_progress,completed,blocked,failed,archived]、21必填字段全存在"
  - "AC3: 缺失字段→BLOCKED，violations=['MISSING_FIELD: xxx']；priority 无效→violations=['INVALID_PRIORITY: xxx']"
  - "AC4: 规则以结构化 dict/Enum 定义——#{field: required=True|False, valid_values=[...]|None}——禁止硬编码字符串列表"
rollback_instructions:
  - "g0_entry.py→空桩 check_all() 返回 GateResult.PASSED"
created_at: 2026-05-06T23:41:00Z
updated_at: 2026-05-06T23:41:00Z
closed_at: null
dependencies:
  - TASK-INF-0102
  - TASK-INF-0104
blocked_by: [TASK-INF-0102, TASK-INF-0104]
blocks: []
tags: [gate-engine, G0, entry-gate, TaskCard-validation]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 初始创建，基于 blueprint.md §5.1 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§5.1 G0 任务入口门控"]
  keywords: [G0, entry-gate, TaskCard, field-validation, required-fields]
  ai_reads_for_inference: true
---

# TASK-INF-0107: G0 入口门控结构化 YAML 规则落地

## 背景与动机

G0 Entry Gate 是任务进入系统的第一道门——必须在任务卡生成/提交前确保 TaskCard 结构完整（blueprint.md §5.1）。21 必填字段缺一不可，priority 必须在有效集合内。

## 实施计划

在 `g0_entry.py` 中以结构化配置驱动校验：

```python
G0_RULES = {
    "fields": {
        "task_id": {"required": True, "type": str, "allow_empty": False},
        "status": {"required": True, "type": str, "valid_values": ["planned","in_progress","completed","blocked","failed","archived"]},
        "priority": {"required": True, "type": str, "valid_values": ["P0","P1","P2","P3","P4"]},
        # ... 其余 18 必填字段同定义
    }
}

class G0EntryGate(Gate):
    def check_all(self, task_dict: dict) -> GateResult:
        violations = []
        for field_name, rule in G0_RULES["fields"].items():
            if rule["required"] and (field_name not in task_dict or (rule.get("allow_empty", True) is False and not task_dict[field_name])):
                violations.append(f"MISSING_FIELD: {field_name}")
            if field_name in task_dict and "valid_values" in rule:
                if task_dict[field_name] not in rule["valid_values"]:
                    violations.append(f"INVALID_{field_name.upper()}: {task_dict[field_name]}")
        if violations:
            return GateResult(status=GateStatus.BLOCKED, gate_level="G0", violations=violations)
        return GateResult(status=GateStatus.PASSED, gate_level="G0")
```

## 回退方案

空桩即可——`g0_entry.py` 的 `check_all()` 返回 `GateResult.PASSED`。

## 验收标准

| # | 标准 |
|---|------|
| AC1 | YAML规则含 gate_name/gate_level/required_context |
| AC2 | 缺task_id→BLOCKED，priority=P5→BLOCKED |
| AC3 | violations 格式：MISSING_FIELD:xxx 或 INVALID_PRIORITY:xxx |
| AC4 | G0_RULES dict 可被下游工具消费（非散落的if列表） |
