---
task_id: "TASK-INF-0131"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §8 项目6 — gates/task_completion_gate.py + §5 依赖项 + §12 源码索引"

title: "同步 gates/task_completion_gate.py — G7 门禁逻辑对齐 §3.1.2 TaskLifecycleManager"
description: |
  更新 `D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py` 的 G7 完成门禁逻辑。
  当前 G7 门禁逻辑部分在 `task_completion_gate.py`（旧独立文件），部分在 `TaskLifecycleManager`（新实现）。
  需确保：downstream_outputs 完整度校验 / rollback_instructions 非空校验 /
  context_assembly_manifest 索引正确 / 蓝图-代码同步一致 / 范围蔓延检测集成。
  本次同步确保两个 G7 实现路径一致且互补（非重复）。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\task_completion_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\task_completion_gate.py"
    description: "G7 门禁逻辑——对齐 TaskLifecycleManager.gate_g7_output()"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\task_completion_gate.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§8 项目6"
    reason: "需要更新的相关内容——同步 task_completion_gate.py 的 G7 逻辑"
  - module_id: "MOD-INF-006"
    section: "§3.1.2"
    reason: "TaskLifecycleManager 是 G7 的主实现路径——task_completion_gate.py 为兼容层"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§8 项目6 + §5 依赖项 task_completion_gate.py——必须同步"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"
    reason: "G7 主实现路径——需确保两个 G7 实现一致"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M9"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "task_completion_gate.py 的 G7 校验与 TaskLifecycleManager.gate_g7_output() 行为一致"
  - "downstream_outputs 完整度校验——所有声明路径存在且可读"
  - "rollback_instructions 非空——空则 FAIL"
  - "context_assembly_manifest 索引正确——每个 file_path 存在"
  - "无重复实现——task_completion_gate.py 委托或路由到 TaskLifecycleManager"
  - "现有测试 test_task_completion_gate.py 继续通过"

rollback_instructions: |
  1. 恢复 `task_completion_gate.py` 到同步前版本
  2. 确认现有 task_completion_gate 测试继续通过

depends_on: ["TASK-INF-0106"]
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

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 同步 gates/task_completion_gate.py — G7 门禁逻辑

## 目标

蓝图 §8 项目6 明确要求同步 `gates/task_completion_gate.py` 的 G7 门禁逻辑。
当前 G7 有两个实现路径：
- 新路径：`TaskLifecycleManager.gate_g7_output()` （TASK-INF-0106 产物）
- 旧路径：`gates/task_completion_gate.py`（独立文件）

本任务卡确保两个 G7 实现一致且互补。

## 触发条件

- TASK-INF-0106 完成

## 执行步骤

### 读
- task_completion_gate.py 现有代码
- task_lifecycle_manager.py G7 门禁实现
- 蓝图 §8 项目6

### 做
1. 对比两个 G7 实现的校验维度
2. 将 task_completion_gate.py 委托到 TaskLifecycleManager 或确保逻辑一致
3. 更新 imports 和类型签名
4. 运行现有测试确认兼容

### 产
- task_completion_gate.py（已同步）

### 检
```bash
pytest tests/unit/test_task_completion_gate.py -v
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | test | 现有 task_completion_gate 测试全部通过 |
| 2 | diff | G7 校验维度与 lifecycle manager 一致 |
| 3 | lint | 0 errors |
