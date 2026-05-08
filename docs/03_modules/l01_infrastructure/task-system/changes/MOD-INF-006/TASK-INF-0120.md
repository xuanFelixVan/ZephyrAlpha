---
task_id: "TASK-INF-0120"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #35 + 盲点 #44"

title: "实现向后兼容冲击分析——consumer_impact_report + run_consumer_tests"
description: |
  向后兼容冲击分析——变更完成后生成 consumer_impact_report。
  消费者发现——通过模块依赖关系图找出所有引用当前产出物的模块。
  自动化测试触发——run_consumer_tests 标志触发消费者测试集。
  冲击报告——列出受影响模块 + 预估冲击等级。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\impact\\consumer_impact.py"
    description: "ConsumerImpact——消费者发现 + 冲击报告 + 消费者测试触发"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\impact\\consumer_impact.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #35"
    reason: "向后兼容——消费者测试触发"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #35 + 盲点 #44"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
  - "M7"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "consumer_impact_report 列出受影响模块 + 冲击等级"
  - "run_consumer_tests=True 时触发下游模块测试"
  - "消费者发现基于模块依赖图表"

rollback_instructions: |
  1. 移除 consumer_impact.py

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

# 实现向后兼容冲击分析

## 目标

1. 消费者发现——引用链分析
2. 冲击报告——受影响模块 + 等级
3. 消费者测试触发——run_consumer_tests

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. ConsumerImpact 实现：
   - find_consumers(task)——依赖图逆向查找
   - generate_report(task)——冲击报告
   - trigger_tests(task)——消费者测试

### 产
- consumer_impact.py

### 检
```python
impact = ConsumerImpact(dep_graph)
report = impact.generate_report(task)
assert len(report.affected_modules) >= 0
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 消费者发现/报告/测试触发 均有测试 |
| 3 | lint | 0 errors |
