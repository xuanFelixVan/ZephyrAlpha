---
task_id: "TASK-INF-0017"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §6b 跨进程 TraceContext 传播 + 采样决策传播 + contextvars→W3C 桥接"

title: "实现跨进程 TraceContext 传播：5 种传播载体 + 采样决策向前传播 + W3C 桥接"
description: |
  解决 contextvars 单进程限制，实现跨进程/跨模块 trace 链路完整性：
  1. 5 种传播载体：
     - MCP Server→Tool：traceparent 写入 MCP Request metadata._meta
     - 主进程→子进程：环境变量 TRACEPARENT + 命令行参数
     - HTTP/gRPC：W3C traceparent + tracestate header
     - 消息队列：AMQP header
     - 文件系统事件：payload 顶层 traceparent
  2. W3C TraceContext 完整格式：traceparent "00-{trace_id(32hex)}-{span_id(16hex)}-{trace_flags(2hex)}" + tracestate
  3. 采样决策传播：root span flags 01(sampled)→下游完整采集 / 00(not)→仅 trace_id+minimal span
  4. contextvars→W3C 桥接：进入跨进程边界序列化 / 退出边界恢复 TraceContext→创建子 Span
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\cross_process.py"
    description: "跨进程 TraceContext 传播——5 种载体 + 序列化/反序列化 + W3C 桥接"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\sampling_propagation.py"
    description: "采样决策传播——trace_flags 的跨进程传播"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\cross_process.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\traces\\sampling_propagation.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§6b——5 种传播载体表 + traceparent/tracestate 格式 + 采样决策传播 + contextvars→W3C 桥接 + AI 施工约束(4 条)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "MCP request metadata._meta 含 traceparent"
  - "子进程从 TRACEPARENT 环境变量恢复 TraceContext"
  - "root span trace_flags=00→下游仅记录 trace_id+duration+status"
  - "contextvars.TraceContext→W3C traceparent 序列化 roundtrip 一致"
  - "下游 创建子 Span 的 parent_span_id = 上游 span_id"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\traces\cross_process.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\traces\sampling_propagation.py

depends_on:
  - "TASK-INF-0016"
blocked_by: []
status: "created"

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

# TASK-INF-0017: 跨进程 TraceContext 传播

## 目标
解决 contextvars 单进程限制，实现 5 种跨进程传播载体 + 采样决策向前传播 + W3C 桥接。

## 执行步骤

### 读
- 蓝图 §6b：传播载体表/traceparent 格式/采样传播/桥接机制/AI 施工约定

### 做
1. cross_process.py：5 载体序列化/反序列化 + W3C 桥接
2. sampling_propagation.py：trace_flags 传播

### 检
```python
# roundtrip: TraceContext → traceparent → TraceContext
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | mcp | traceparent in MCP metadata |
| 2 | subprocess | TRACEPARENT env recovery |
| 3 | sampling | flags propagation |
| 4 | bridge | roundtrip consistency |
