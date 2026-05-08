---
task_id: "TASK-INF-0016"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §6 traces 子系统——Span 模型 + W3C TraceContext + 智能采样 + span→metrics connector"

title: "实现 traces 子系统：Span 数据模型 + W3C TraceContext 传播 + 智能采样 + RED 指标"
description: |
  实现 traces 子系统的核心能力：
  1. Span 数据类（Pydantic BaseModel）：trace_id(32hex)/span_id(16hex)/parent_span_id/module/start_time/end_time/status/metadata/trace_state
  2. W3C TraceContext：contextvars 传播 + traceparent header "00-{trace_id}-{span_id}-01" + tracestate "zephyr={module_id};{env};{session_id}"
  3. TaskCard 全链路追踪：Root→M1→Gate→Orc→M6→M8→Script→Complete
  4. 智能 tail-based 采样：error 100% / high-latency 100% / root span 100% / 正常 10% / 自适应 1-10%
  5. span→metrics connector：自动生成 RED 指标（Rate/Errors/Duration）
  6. 兼容 shared/contracts/trace_context.py（CTR-TRACE-001）
  7. 上下文管理器风格 API：with telemetry.traces.span("name") as span:
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\trace_context.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\audit_trail\models.py"
    description: "Span Pydantic 模型 + SpanContext"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\propagation.py"
    description: "W3C TraceContext 传播——contextvars + traceparent/tracestate 序列化"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\sampler.py"
    description: "tail-based 智能采样——error/high-latency/root 100% + 正常 10% + 自适应"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\connector.py"
    description: "span→metrics connector——自动生成 RED 指标"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\collector.py"
    description: "traces 采集器入口 + 上下文管理器 span()"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\**\\*.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§6——Span Schema + W3C 传播机制 + 全链路追踪图 + 采样策略表 + span→metrics connector"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "Span 字段与 CTR-TRACE-001 兼容（UUID hex 格式）"
  - "traceparent header 序列化/反序列化正确"
  - "子 Span 的 parent_span_id = 父 Span 的 span_id"
  - "tail-based sampler：error→100%, 正常→~10%"
  - "span.context_manager 退出时自动 end + flush"
  - "span→metrics connector 生成 Rate/Errors/Duration"
  - "自适应采样：高负载→1%，低负载→10%"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\traces\models.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\traces\propagation.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\traces\sampler.py
  4. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\traces\connector.py
  5. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\traces\collector.py

depends_on:
  - "TASK-INF-0001"
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

# TASK-INF-0016: traces 子系统核心实现

## 目标
实现 Span 数据模型、W3C TraceContext 传播、智能 tail-based 采样、span→metrics 自动生成。

## 执行步骤

### 读
- 蓝图 §6：Span Schema/W3C 传播/全链路追踪图/采样策略表/connector

### 做
1. Span 模型：Pydantic V2，兼容 CTR-TRACE-001
2. propagation：contextvars + traceparent/tracestate
3. sampler：4 策略 tail-based + 自适应
4. connector：自动 RED 指标
5. collector：上下文管理器 span()

### 检
```python
with telemetry.traces.span("test") as span:
    span.set_metadata(task_id="T-001")
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | span | 兼容 CTR-TRACE-001 |
| 2 | propagation | traceparent 正确 |
| 3 | sampler | error=100%, normal≈10% |
| 4 | connector | RED 自动生成 |
| 5 | context | with 退出自动 end |
