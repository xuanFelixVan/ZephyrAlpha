---
task_id: "TASK-INF-0122"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #37 + 盲点 #46"

title: "实现输出范围蔓延检测——modified_files_actual + lines_changed_actual 合规检查"
description: |
  范围蔓延检测——执行完成后记录 modified_files_actual 和 lines_changed_actual。
  合规检查——与 allowed_touch 和预期变更范围对比。
  蔓延告警——超出范围时生成告警 + 要求 AI 解释或回退。
  与 G7 门禁联动——蔓延检测不通过阻止 transition 到 completed。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\core\lifecycle\scope_guard.py"
    description: "ScopeGuard——modified_files 记录 + 范围蔓延检测 + G7 联动"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\scope_guard.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #37"
    reason: "范围蔓延检测"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #37 + 盲点 #46"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
  - "M9"
estimated_tokens: 6000
timeout_minutes: 20

acceptance_criteria:
  - "modified_files_actual 记录实际修改文件列表"
  - "lines_changed_actual 记录实际行数变化"
  - "蔓延检测——modified_files_actual ⊈ allowed_touch → ScopeCreepWarning"
  - "G7 联动——蔓延检测失败则 G7 门禁不通过"

rollback_instructions: |
  1. 移除 scope_guard.py

depends_on: ["TASK-INF-0102", "TASK-INF-0106"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "gate"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "semi_autonomous"
autonomy_checklist: []
---

# 实现输出范围蔓延检测

## 目标

1. 修改范围记录——modified_files_actual + lines_changed_actual
2. 蔓延检测——与 allowed_touch 对比
3. G7 门禁联动

## 触发条件

- TASK-INF-0102 / TASK-INF-0106 完成

## 执行步骤

### 做
1. ScopeGuard 实现：
   - record(task, modified_files, lines)——记录实际变更
   - check(task)——蔓延检测
   - 与 G7 门禁联动

### 产
- scope_guard.py

### 检
```python
guard = ScopeGuard()
guard.record(task, ["src/zephyr/core/models.py"], 200)
result = guard.check(task)
assert result.is_clean
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 记录/蔓延/G7联动 均有测试 |
| 3 | lint | 0 errors |
