---
task_id: "TASK-INF-0026"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §15.5-15.7 测试检查表 + 集成测试 + 性能基准"

title: "实现 Telemetry 测试检查表：25 项单元测试 + 6 条集成测试链 + 性能基准"
description: |
  1. 单元测试检查表（蓝图 §15.5 25 项）：每项对应一个测试函数，tests/telemetry/ 下
     - 模型校验(MetricPoint/Span/Log/AIBehaviorEvent schema) / 环形缓冲区 flush/overflow /
       JSONL writer rotation / PII脱敏正确性 / TraceContext 传播 / 采样逻辑 / Cardinality 控制 /
       时钟偏差检测 / DLQ事件生命周期 / FQMN冲突检测 / 热更新回调 / FeatureFlag 切换 /
       Watchdog 重启逻辑 / Synthetic 事务执行 / 告警 Pipelines 去重/聚合/静默/路由 / Schema 拒绝逻辑
  2. 集成测试（蓝图 §15.6 6 条）：
     - metrics.e2e: report→buffer→flush→SQLite→FLE query
     - traces.e2e: span→context→W3C→correlate→logs
     - ai_behavior.e2e: event→ErrorContext→self-correction→dashboard
     - alerts.e2e: burn_rate→pipeline→notify→ack→resolve
     - archiving.e2e: metrics→30d→archive→90d→delete
     - shutdown.e2e: flush→close→emergency.jsonl
  3. 性能基准（蓝图 §15.7）：
     - MetricPoint report 吞吐量 >1000/sec
     - JSONL writer 单行延迟 < 2ms
     - Span 创建+flush < 5ms overhead
     - Ring buffer flush 1000 per batch < 100ms
     - DLQ write < 10ms
     - Discovery query < 50ms (1000 metrics)
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_models.py"
    description: "模型 schema 校验——MetricPoint/Span/Log/AIBehaviorEvent"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_ring_buffer.py"
    description: "环形缓冲区 flush/overflow"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_jsonl_writer.py"
    description: "JSONL writer rotation/truncation"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_pii_masker.py"
    description: "PII 脱敏——6 类字段"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_trace_context.py"
    description: "TraceContext 传播——contextvars+W3C"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_sampler.py"
    description: "tail-based 采样策略"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_cardinality.py"
    description: "Cardinality 上限+聚合+zombie"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_clock_guard.py"
    description: "时钟偏差检测"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_dlq.py"
    description: "DLQ 事件生命周期+repair"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_namespace.py"
    description: "FQMN 冲突检测"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_hot_reload.py"
    description: "热更新回调"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_flags.py"
    description: "FeatureFlag 切换"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_watchdog.py"
    description: "Watchdog 重启逻辑"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_synthetic.py"
    description: "Synthetic 事务执行"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_alert_pipeline.py"
    description: "Alert Pipeline 去重/聚合/静默/路由"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\test_schema_reject.py"
    description: "Schema 拒绝逻辑"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\integration\\test_metrics_e2e.py"
    description: "metrics.e2e 集成测试"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\integration\\test_traces_e2e.py"
    description: "traces.e2e 集成测试"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\integration\\test_ai_behavior_e2e.py"
    description: "ai_behavior.e2e 集成测试"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\integration\\test_alerts_e2e.py"
    description: "alerts.e2e 集成测试"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\integration\\test_archiving_e2e.py"
    description: "archiving.e2e 集成测试"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\integration\\test_shutdown_e2e.py"
    description: "shutdown.e2e 集成测试"
  - path: "D:\\ZephyrAlpha\\tests\\telemetry\\benchmarks\\test_performance.py"
    description: "性能基准测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\telemetry\\**\\*.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\**\\*.py"

applicable_rules: []

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§15.5——25项单元测试检查表 + §15.6——6条集成测试 + §15.7——性能基准指标表"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "25 项单元测试全部通过（100%）"
  - "6 条集成测试全部通过"
  - "MetricPoint report >1000/sec"
  - "JSONL latency <2ms"
  - "Span overhead <5ms"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\tests\telemetry\ 下所有本次创建的文件

depends_on:
  - "TASK-INF-0012"
  - "TASK-INF-0013"
  - "TASK-INF-0014"
  - "TASK-INF-0015"
  - "TASK-INF-0016"
  - "TASK-INF-0017"
  - "TASK-INF-0018"
  - "TASK-INF-0019"
  - "TASK-INF-0021"
  - "TASK-INF-0022"
  - "TASK-INF-0023"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
  - "testing"
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

# TASK-INF-0026: 测试检查表 + 集成测试 + 性能基准

## 目标
实现 25 项单元测试 + 6 条集成测试 + 性能基准验证，确保 Telemetry 全链路质量。

## 执行步骤

### 读
- 蓝图 §15.5-§15.7：测试检查表 + 集成测试链 + 性能基准

### 做
1. 创建 16 个单元测试文件覆盖 25 项
2. 创建 6 个集成测试文件
3. 创建性能基准测试

### 检
```bash
pytest tests/telemetry/ -v --cov
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | unit | 25/25 pass |
| 2 | integration | 6/6 pass |
| 3 | metric | >1000/sec |
| 4 | jsonl | <2ms |
| 5 | span | <5ms overhead |
