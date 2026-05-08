---
task_id: "TASK-INF-0121"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #36 + 盲点 #45"

title: "实现中执行自适应重规划——replan_proposed + 执行策略调整"
description: |
  自适应重规划——执行中发现任务卡定义与实际需求偏差时生成 replan_proposed。
  偏差检测——modified_files_actual/lines_changed_actual 超出预期 → 触发重规划信号。
  重规划提案——生成新的任务步骤建议 + 原任务暂停或拆分。
  AI 批准——replan_proposed 需人工或高级自治 AI 批准后执行。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\adaptation\\adaptive_replanner.py"
    description: "AdaptiveReplanner——偏差检测 + 重规划提案 + AI 批准"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\adaptation\\adaptive_replanner.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #36"
    reason: "中执行自适应重规划"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #36 + 盲点 #45"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "偏差检测——modified_files ≠ allowed_touch 内文件 → 触发检查"
  - "replan_proposed 含新步骤建议 + 拆分方案"
  - "被批准前任务保持 SUSPENDED 状态"
  - "批准后原任务被替换为多个子任务"

rollback_instructions: |
  1. 移除 adaptive_replanner.py

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

# 实现中执行自适应重规划

## 目标

1. 偏差检测——实际 vs 预期差异
2. 重规划提案——新步骤 + 拆分
3. AI 批准流程

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. AdaptiveReplanner 实现：
   - detect_deviation(task)——对比预期 vs 实际
   - propose_replan(task)——生成重规划方案
   - approve(task, proposal)——批准执行

### 产
- adaptive_replanner.py

### 检
```python
replanner = AdaptiveReplanner()
proposal = replanner.propose_replan(task)
replanner.approve(task, proposal)
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 偏差/提案/批准 均有测试 |
| 3 | lint | 0 errors |
