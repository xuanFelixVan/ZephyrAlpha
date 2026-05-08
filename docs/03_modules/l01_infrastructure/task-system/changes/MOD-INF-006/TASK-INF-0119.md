---
task_id: "TASK-INF-0119"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #34 + 盲点 #43"

title: "实现执行时前置漂移校验——upstream_files_hash 比对"
description: |
  前置漂移校验——执行开始前计算 upstream_files 哈希值。
  哈希比对——与上游任务输出时刻的哈希值对比。
  漂移告警——不一致时通知 AI——可选择接受风险继续或暂停等待协调。
  upstream_files_content_hash 字段记录。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\precondition_drift.py"
    description: "PreconditionDrift——hash 计算 + 比对 + 告警"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\precondition_drift.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #34"
    reason: "前置漂移校验"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #34 + 盲点 #43"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 6000
timeout_minutes: 20

acceptance_criteria:
  - "计算 upstream_files 各文件 SHA256 哈希"
  - "与 upstream_files_content_hash 比对——不一致时返回 DriftWarning"
  - "告警含漂移文件列表 + 差异摘要"
  - "AI 可选择 accept_drift 继续执行"

rollback_instructions: |
  1. 移除 precondition_drift.py

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

ai_autonomy_level: "semi_autonomous"
autonomy_checklist: []
---

# 实现前置漂移校验

## 目标

1. upstream_files 哈希计算
2. 执行前哈希比对
3. 漂移告警 + AI 风险接受

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. PreconditionDrift 实现：
   - calc_hashes()——SHA256 计算
   - check(task)——比对 + 返回 DriftResult
   - accept_drift(task)——AI确认接受

### 产
- precondition_drift.py

### 检
```python
drift = PreconditionDrift()
result = drift.check(task)
if result.has_drift:
    drift.accept_drift(task)
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | hash/比对/告警 均有测试 |
| 3 | lint | 0 errors |
