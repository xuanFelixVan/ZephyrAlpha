---
task_id: "TASK-INF-0113"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #22 + 盲点 #32"

title: "实现 Saga 补偿事务——失败 → compensation_steps 执行修复"
description: |
  Saga 补偿事务——任务失败时按 compensation_steps 顺序执行逆操作修复。
  compensation_steps 字段——list[dict] 格式定义每个步骤的逆向操作。
  部分成功场景——记录 checkpoint_path 确定哪些步骤已完成。
  补偿验证——补偿步骤执行后验证系统状态恢复。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\core\compensation\saga_compensator.py"
    description: "SagaCompensator——compensation_steps 执行 + 验证"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\quality\\saga_compensator.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #22"
    reason: "补偿——失败自动触发逆操作"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #22 + 盲点 #32"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 10000
timeout_minutes: 30

acceptance_criteria:
  - "任务失败 → SagaCompensator.execute(task) 自动触发"
  - "compensation_steps 按序执行逆操作"
  - "部分成功——从 checkpoint_path 确定起始位置"
  - "补偿后验证——确保系统状态恢复到任务前"

rollback_instructions: |
  1. 移除 saga_compensator.py

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "quality"
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

# 实现 Saga 补偿事务

## 目标

1. 失败自动补偿——compensation_steps 逆操作执行
2. 部分成功处理——checkpoint_path 定位
3. 补偿后验证——状态恢复检查

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. SagaCompensator 实现：
   - execute(task)——按 compensation_steps 执行逆操作
   - 从 checkpoint_path 读取已完成的步骤
   - 补偿验证

### 产
- saga_compensator.py

### 检
```python
comp = SagaCompensator()
comp.execute(task)  # task 状态 = FAILED
assert task.status == TaskStatus.ROLLED_BACK
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 补偿/部分成功/验证 均有测试 |
| 3 | lint | 0 errors |
