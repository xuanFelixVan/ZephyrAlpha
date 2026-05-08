---
task_id: "TASK-INF-0114"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #23 + 盲点 #33"

title: "实现模型质量退化检测——输出质量下滑自动告警"
description: |
  模型质量退化检测——监控模型输出质量指标（成功率/代码有效性/一致性）。
  LLM 输出质量评分——对每次 LLM 调用的输出计算质量分。
  退化趋势检测——连续 N 次低于阈值触发告警。
  质量报告——定期生成质量趋势报告。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\quality\\quality_monitor.py"
    description: "QualityMonitor——质量评分 + 退化检测 + 告警"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\quality\\quality_monitor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #23"
    reason: "质量退化检测"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #23 + 盲点 #33"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "LLM 输出质量分数 0.0-1.0 范围内计算"
  - "连续 5 次低于阈值 → 告警通知发送"
  - "质量退化趋势图按周/月汇总"

rollback_instructions: |
  1. 移除 quality_monitor.py

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

# 实现模型质量退化检测

## 目标

1. LLM 输出质量评分
2. 退化趋势检测
3. 自动告警与报告

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. QualityMonitor 实现：
   - score()——对 LLM 输出质量打分
   - check_degradation()——趋势检测
   - report()——质量报告生成

### 产
- quality_monitor.py

### 检
```python
monitor = QualityMonitor(threshold=0.6)
score = monitor.score(llm_output)
monitor.check_degradation([0.9, 0.8, 0.5, 0.4, 0.3])
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 评分/退化检测/报告 均有测试 |
| 3 | lint | 0 errors |
