---
task_id: "TASK-INF-0014"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §4——入站速率限制 & Backpressure 对接 + Exemplar 关联 + DLQ 完整实现"

title: "实现 metrics 速率限制 + Backpressure + Exemplar + DLQ 死信队列"
description: |
  1. per-module 速率限制：100 MetricPoint/sec → 50% 丢弃 + rate_limit_hit
  2. ring buffer 三级水位线 Backpressure：80%→Throttle / 95%→Pause / 100%→丢弃+overflow+
    恢复<60%→Resume（严格顺序：Throttle→Pause→丢弃）
  3. Exemplar→trace 下钻：MetricPoint(trace_id, span_id)→Span→Log 三击链路
  4. DLQ 完整实现：
     - 存储：JSONL format, data/telemetry/{env}/dlq/{date}.jsonl, TTL 30 天, 100MB 轮转
     - 自动修复：每60min/event-driven 扫描→SCHEMA_ERROR/TYPE_ERROR/WRITE_FAILED 分类修复
     - 监控：dlq_size_bytes/dlq_growth_rate/dlq_repair_success_rate/dlq_dead_event_count/dlq_age_oldest_event
     - AI 消费 MCP 接口：get_dlq_summary() / get_dlq_samples()
     - DLQ 事件生命周期：正常→SQLite✅ / 软拒绝→DLQ+rejection log✅ / 硬拒绝→DLQ+P2⚠️ / DLQ写失败→stderr→丢弃❌
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\backpressure\\"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\mcp\rate_limiter.py"
    description: "per-module 速率限制 + Backpressure 水位线集成"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\dlq.py"
    description: "DLQ 完整实现：JSONL 存储 + 自动修复引擎 + 监控指标 + AI MCP 接口"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\rate_limiter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\dlq.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§4——速率限制+Backpressure 水位线表 + Exemplar 三击链路 + DLQ 完整设计（事件生命周期/存储/修复/监控/MCP）"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "per-module >100/sec MetricPoint → 50% drop + rate_limit_hit counter"
  - "ring buffer 80%→Throttle 信号发出, 95%→Pause, 100%→丢弃 + overflow event"
  - "ring buffer <60%→Resume 信号发出"
  - "MetricPoint exemplar 含 trace_id + span_id"
  - "schema 校验失败 → DLQ 写入 (no silent drop)"
  - "DLQ 自动修复 >50% success rate"
  - "get_dlq_summary() 返回各 reason 分类统计"
  - "DLQ dead events >1000 → P1 alert"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\rate_limiter.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\dlq.py

depends_on:
  - "TASK-INF-0012"
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

# TASK-INF-0014: metrics 速率限制 + Backpressure + DLQ

## 目标
实现 per-module 速率限制、三级 Backpressure 水位线管控、Exemplar 关联追踪、DLQ 死信队列全生命周期。

## 执行步骤

### 读
- 蓝图 §4：速率限制表/Backpressure 水位线/Exemplar 关联/DLQ 完整设计

### 做
1. rate_limiter.py：per-module 限流 + ring buffer 水位线 Backpressure 信号
2. dlq.py：JSONL storage + 自动修复引擎 + 监控指标 + MCP 接口

### 产
- rate_limiter.py + dlq.py

### 检
```python
# DLQ 写入+查询+修复端到端测试
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | limit | per-module 100/sec |
| 2 | backpressure | 3-level + Resume |
| 3 | exemplar | metric→trace→log chain |
| 4 | dlq | no silent drop |
| 5 | repair | >50% auto-repair rate |
