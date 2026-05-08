---
task_id: "TASK-INF-0117"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #25/#28 + 盲点 #37/#41"

title: "实现模型快照锁定 + 跨 Session 思考态持久化"
description: |
  模型快照锁定——model_snapshot_pinned 冻结特定模型版本。
  跨 Session 思考态——thinking_state_json 持久化深度推理状态。
  思考态恢复——新会话读取 thinking_state_json 恢复推理上下文。
  模型一致性——依赖任务使用同一模型快照版本确保可重复性。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\quality\\model_snapshot.py"
    description: "ModelSnapshot——模型版本锁定 + 一致性"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\session\\thinking_state.py"
    description: "ThinkingState——thinking_state_json 持久化 + 恢复"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\quality\\model_snapshot.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\session\\thinking_state.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #25/#28"
    reason: "模型快照 + 跨Session思考态"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #25/#28 + 盲点 #37/#41"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
  - "M10"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "模型快照——model_snapshot_pinned 锁定后不自动切换"
  - "思考态写入——task 完成/暂停时 writing_state_json 被序列化"
  - "思考态恢复——新 session 读取后推理上下文恢复"
  - "模型一致性——依赖任务使用同一快照"

rollback_instructions: |
  1. 移除 model_snapshot.py 和 thinking_state.py

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "session"
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

# 实现模型快照锁定 + 跨 Session 思考态

## 目标

1. 模型快照——冻结模型版本
2. 跨 Session 思考态——推理状态持久化与恢复

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. ModelSnapshot 实现
2. ThinkingState 实现

### 产
- model_snapshot.py + thinking_state.py

### 检
```python
snap = ModelSnapshot()
snap.pin(task, "deepseek-2026-05-06")
state = ThinkingState()
state.save(task, thinking_context_dict)
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 快照/思考态 均有测试 |
| 3 | lint | 0 errors |
