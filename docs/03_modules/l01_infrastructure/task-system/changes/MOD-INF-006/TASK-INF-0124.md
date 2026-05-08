---
task_id: "TASK-INF-0124"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #33 + 盲点 #48"

title: "实现任务取消安全协议——cancelled_artifacts 记录 + 安全删除"
description: |
  取消安全协议——cancelled 状态时记录 cancelled_artifacts（废弃的产出物）。
  取消审批——优先确认下游消费者节点未执行完毕——不破坏已完成的依赖。
  数据库状态保护——任务状态变为 CANCELLED → 历史不可删除。
  恢复支持——CANCELLED 可 DEFERRED（推迟不取消）但不能回到 IN_PROGRESS。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-closure-standard.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\cancel_protocol.py"
    description: "CancelProtocol——artifacts 记录 + 消费者安全 + 恢复 + 超72h状态保护"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\cancel_protocol.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #33"
    reason: "取消安全——cancelled_artifacts + 消费者安全"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #33 + 盲点 #48"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
  - "M9"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "取消时 cancelled_artifacts 记录所有已产出文件路径"
  - "消费者检查——依赖任务 completd → 拒绝取消"
  - "超 72h completed → 取消路径关闭——only force_cancel 可选"
  - "恢复——CANCELLED → DEFERRED 时恢复任务卡到推迟状态"
  - "CANCELLED 不可变回 IN_PROGRESS"

rollback_instructions: |
  1. 移除 cancel_protocol.py

depends_on: ["TASK-INF-0102", "TASK-INF-0106"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "lifecycle"
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

# 实现任务取消安全协议

## 目标

1. cancelled_artifacts 记录
2. 消费者安全检查
3. 超 72h completed 的取消路径关闭
4. 恢复——CANCELLED→DEFERRED

## 触发条件

- TASK-INF-0102 / TASK-INF-0106 完成

## 执行步骤

### 做
1. CancelProtocol 实现：
   - cancel(task)——取消 + recorded artifacts
   - can_cancel(task)——检查消费者安全
   - restore(task)——CANCELLED→DEFERRED
   - 超72h状态保护

### 产
- cancel_protocol.py

### 检
```python
proto = CancelProtocol()
assert proto.can_cancel(task)  # 无consumer已完成
proto.cancel(task)
assert task.status == TaskStatus.CANCELLED
assert len(task.cancelled_artifacts) > 0
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 取消/消费者安全/恢复 均有测试 |
| 3 | lint | 0 errors |
