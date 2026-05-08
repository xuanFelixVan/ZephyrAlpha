---
task_id: "TASK-INF-0018"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §7 ai_behavior 子系统——AIBehaviorEvent + 7 维度 + Error Taxonomy + 自我修正效能"

title: "实现 ai_behavior 子系统：AIBehaviorEvent 模型 + 7 大监测维度 + Error Taxonomy + 自我修正效能追踪"
description: |
  实现 AI 行为可观测性的完整子系统：
  1. AIBehaviorEvent Pydantic 模型：event_type/trace_id/module/model_id/model_version/prompt_template_id/
     prompt_version/input_tokens/output_tokens/cost_usd/duration_ms/status/labels/tool_calls/decision_path/hallucination_score
  2. 7 大监测维度：模型调用画像 / Token与成本(FinOps) / Gate交互行为 / 输出质量与一致性 / 
     Prompt版本追踪 / 工具调用链追踪 / Agent决策路径
  3. Error Taxonomy（ErrorContext）：persistence(transient/permanent/intermittent) /
     source(client/server/dependency/internal) / expectation(expected/unexpected/unknown) /
     severity(degraded/blocking/fatal)
  4. AI 自我修正效能追踪（AISelfCorrectionEvent）：anomaly_id/anomaly_type/detected_at/
     analysis_duration_s/action_taken/fix_deployed_at/verified_at/success/regression_detected
  5. 告警过滤决策树：基于 ErrorContext 分类的 P0/P1/P2/不告警规则
  6. AI 效能仪表板数据源
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\audit_trail\models.py"
    description: "AIBehaviorEvent + ErrorContext + AISelfCorrectionEvent Pydantic 模型"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\ai_behavior\\tracker.py"
    description: "7 维度追踪器——model/profile/token/gate/quality/prompt/tool/decision"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\ai_behavior\\error_taxonomy.py"
    description: "Error Taxonomy——分类引擎 + 告警过滤决策树"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\ai_behavior\\self_correction.py"
    description: "AI 自我修正效能追踪——AISelfCorrectionEvent 记录 + 效能仪表板"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\ai_behavior\\**\\*.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§7——AIBehaviorEvent Schema + 7 维度定义表(§7.1-§7.7) + Error Taxonomy 4 维度(§7.8) + 自我修正效能 6 维度(§7.9) + 告警决策树"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "AIBehaviorEvent 含 14+ 字段"
  - "7 维度 tracker 全部可采集"
  - "ErrorContext 4 分类维度可注入到任意 Span/Log/Alert"
  - "Error Taxonomy 决策树：internal+blocking→AI自我修正 / dependency+transient→仅记录 / expected→不告警"
  - "AISelfCorrectionEvent 可记录完整修正生命周期"
  - "连续 3 次修正同一 anomaly→标记 HARD_PROBLEM→Escalate"
  - "FeatureFlag enable_ai_behavior_tracking=OFF→停止写入"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\ai_behavior\models.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\ai_behavior\tracker.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\ai_behavior\error_taxonomy.py
  4. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\ai_behavior\self_correction.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0004"
  - "TASK-INF-0005"
blocked_by: []
status: "done"

tags_fn:
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-015"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# TASK-INF-0018: ai_behavior 子系统实现

## 目标
实现 AI 行为可观测性全套能力：AIBehaviorEvent 模型、7 维度追踪、Error Taxonomy、自我修正效能追踪。

## 执行步骤

### 读
- 蓝图 §7：完整设计（§7.1-§7.9）

### 做
1. models：AIBehaviorEvent + ErrorContext + AISelfCorrectionEvent
2. tracker：7 维度采集器
3. error_taxonomy：分类引擎 + 告警过滤
4. self_correction：效能追踪 + 仪表板

### 检
```python
event = AIBehaviorEvent(event_type="model_call", model_id="gpt-4", ...)
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | event | 14+ fields |
| 2 | tracker | 7 dimensions |
| 3 | taxonomy | 4-level classification |
| 4 | correction | full lifecycle tracking |
