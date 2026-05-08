---
task_id: "TASK-INF-0115"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #24 + 盲点 #34"

title: "实现 SLA 时限与老化升级——sla_deadline + sla_escalation_policy 自动推进"
description: |
  SLA 时限——sla_deadline 字段，超时自动标记过期。
  老化升级——sla_escalation_policy 定义无进展时间阈值与升级动作。
  original_priority 保留——升级后 priority 可提高但 original_priority 不变。
  定时巡检——周期性检查 sla_deadline 并触发升级动作。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\core\sla\sla_monitor.py"
    description: "SLAMonitor——deadline 检查 + escalation + priority 升级"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\quality\\sla_monitor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #24"
    reason: "SLA 时限与老化升级"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #24 + 盲点 #34"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "sla_deadline 过期 → 任务状态升级为 STALE 或触发 escalation"
  - "escalation_policy 定义阈值如 24h/72h/7d"
  - "original_priority 保持初值——priority 可升级"
  - "定时巡检至少每 1h 一次"

rollback_instructions: |
  1. 移除 sla_monitor.py

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

# 实现 SLA 时限与老化升级

## 目标

1. SLA 时限——sla_deadline 自动过期
2. 老化升级——按 escalation_policy 推进
3. Priority 升级——original_priority 保留
4. 定时巡检——周期性触发

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. SLAMonitor 实现：
   - check_deadlines()——扫描过期任务
   - escalate()——按 escalation_policy 升级
   - 保留 original_priority

### 产
- sla_monitor.py

### 检
```python
monitor = SLAMonitor(repo)
monitor.check_deadlines()
assert task.priority > task.original_priority
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 过期/升级/保留优先级 均有测试 |
| 3 | lint | 0 errors |
