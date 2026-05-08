---
task_id: "TASK-INF-0011"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §3e 指标命名空间与冲突预防 + §3f 批量上报 API"

title: "实现 FQMN 指标命名空间防冲突 + 批量上报 API"
description: |
  1. FQMN 命名空间：{module_id}::{metric_name} 全限定名，Schema Registry 按 FQMN 唯一存储，
     同一 module_id 内 metric_name 唯一，跨 module_id 自动解歧。
     冲突检测：新注册时自动检测同 module_id 冲突，返回 CONFLICT 错误码。
     MetricPoint 自动注入 module_id，无需手动传递。
     Metric Discovery API 支持按 module 过滤 + 全项目搜索。
  2. 批量 API：report_batch(MetricPoint[]) 一次 lock + 批量写 ring buffer；
     log_batch(LogEntry[]) 一次 JSONL write；
     start_batch_spans(SpanContext[]) 并行 span 管理。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\namespace.py"
    description: "FQMN 命名空间管理器——FQMN 生成/解析/冲突检测/自动注入"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\batch.py"
    description: "批量上报 API——report_batch / 批量 lock / 逐条验证 / 结果汇总"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\namespace.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\batch.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§3e——FQMN 策略/冲突检测/MetricPoint 自动注入/Discovery 过滤 + §3f——批量 API Python 代码/施工约定"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 7000
timeout_minutes: 30

acceptance_criteria:
  - "MOD-INF-008::llm_calls_total 和 MOD-INF-012::llm_calls_total 被识别为不同指标"
  - "同 module_id 内重复 metric_name → 返回 CONFLICT 错误"
  - "report_batch(10个 MetricPoint) 一次 lock acquire"
  - "批量上报失败 → 逐条降级为独立调用"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\namespace.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\batch.py

depends_on:
  - "TASK-INF-0001"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
  - "infra"
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

# TASK-INF-0011: 实现 FQMN 命名空间 + 批量上报 API

## 目标
实现 FQMN（module_id::metric_name）全限定名机制防止跨模块指标冲突，以及批量上报 API 消除逐个上报的锁竞争。

## 触发条件
- TASK-INF-0001 通过

## 执行步骤

### 读
- 蓝图 §3e：FQMN 策略/冲突检测/MetricPoint 自动注入/Discovery API 过滤
- 蓝图 §3f：批量 API Python 代码示例/施工约定（3 条）

### 做
1. 实现 namespace.py：FQMN 生成/解析/冲突检测/MetricPoint module_id 自动注入
2. 实现 batch.py：report_batch/log_batch/start_batch_spans + 一次 lock acquire

### 产
- namespace.py + batch.py

### 检
```python
from zephyr.l12_system_telemetry.metrics.namespace import FQMN
fqmn = FQMN.make("MOD-INF-008", "llm_calls_total")
assert str(fqmn) == "MOD-INF-008::llm_calls_total"
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | fqmn | 不同 module 同指标名 = 不同 FQMN |
| 2 | conflict | 同 module 同指标名 → CONFLICT |
| 3 | batch | report_batch 一次 lock |
