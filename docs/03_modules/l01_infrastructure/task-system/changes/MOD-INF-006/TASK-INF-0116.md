---
task_id: "TASK-INF-0116"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #26/#27 + 盲点 #35/#36"

title: "实现紧急热修复快速通道 + 跨任务知识隔离"
description: |
  紧急热修复模式——emergency_mode 启用时绕过非安全门禁直达 G4 完成标准。
  跨任务知识隔离——cross_task_learning 字段记录任务间的共享发现。
  知识条目机制——执行中发现的可复用知识自动登记到知识库。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\pipeline\\pipeline-module-registry.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\maintenance\\emergency_hotfix.py"
    description: "EmergencyHotfix——emergency_mode 快速通道 + 事后补齐"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\knowledge\\cross_task_learning.py"
    description: "CrossTaskLearning——知识隔离 + ke_entries 管理"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\maintenance\\emergency_hotfix.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\knowledge\\cross_task_learning.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #26/#27"
    reason: "紧急热修复 + 跨任务知识隔离"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #26/#27 + 盲点 #35/#36"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
  - "M10"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "emergency_mode=True → G1-G6 门禁降级为可选（G0/G7仍强制）"
  - "事后补齐——紧急任务完成后需补全所有门禁记录"
  - "cross_task_learning 记录任务间的共享发现"
  - "ke_entries 自动登记可复用知识"

rollback_instructions: |
  1. 移除 emergency_hotfix.py 和 cross_task_learning.py

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
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

# 实现紧急热修复 + 跨任务知识隔离

## 目标

1. 紧急热修复快速通道——绕过非安全门禁
2. 跨任务知识隔离——任务间知识共享

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. EmergencyHotfix——emergency_mode 快速通道
2. CrossTaskLearning——知识条目管理

### 产
- emergency_hotfix.py + cross_task_learning.py

### 检
```bash
pytest tests/unit/test_maintenance.py -v -k emergency
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 紧急通道/知识隔离 均有测试 |
| 3 | lint | 0 errors |
