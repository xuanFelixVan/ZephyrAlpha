---
task_id: "TASK-INF-0012"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §4 metrics 子系统——MetricPoint + RingBuffer + flush"

title: "实现 metrics 子系统核心：MetricPoint 数据模型 + 环形缓冲区 + SQLite 批量 flush"
description: |
  实现 metrics 子系统的核心数据流：
  1. MetricPoint 数据类（Pydantic BaseModel）：name/value/timestamp/labels/type/exemplar
  2. 环形缓冲区（collections.deque, maxlen=10000）
  3. 每 60s 批量 flush 到 SQLite metrics 表（原子事务）
  4. 指标类型：gauge(最后值)/counter(增量rate)/histogram(P50/P90/P95/P99)/summary(客户端分位数)
  5. 集成 snippet validator：report() 前校验
  6. FLE 消费接口：查询 metrics 表
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\audit_trail\models.py"
    description: "MetricPoint Pydantic 模型——gauge/counter/histogram/summary + exemplar"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\ring_buffer.py"
    description: "环形缓冲区——enqueue/flush/drain 操作"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\collector.py"
    description: "metrics 采集器入口——report(MetricPoint) + flush to SQLite"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\ring_buffer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\collector.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——MetricPoint 使用 BaseModel，禁止 dataclass"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§4——MetricPoint Schema + 4 指标类型 + 采集流程图"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "MetricPoint BaseModel 含全部 6 字段"
  - "report() 写入 ring buffer 成功"
  - "flush() 批量写入 SQLite 原子性——全部成功或全部回滚"
  - "gauge/counter/histogram/summary 4 种类型均可上报"
  - "schema validator 拒绝未注册指标名"
  - "ring buffer 10000 条 full → 丢弃最旧 + buffer_overflow 事件"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\models.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\ring_buffer.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\collector.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0011"
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

# TASK-INF-0012: metrics 子系统核心实现

## 目标
实现 MetricPoint 数据模型、10000 容量环形缓冲区、60s 批量 SQLite flush 的核心数据流。

## 执行步骤

### 读
- 蓝图 §4：采集流程/MetricPoint Schema/4 指标类型/Cardinality 控制

### 做
1. MetricPoint：Pydantic BaseModel，含 exemplar 关联 trace
2. RingBuffer：deque maxlen=10000，backpressure 水位线（80%/95%/100%）
3. Collector：report()→ring buffer→flush()→SQLite

### 检
```python
from zephyr.l12_system_telemetry.metrics.models import MetricPoint
mp = MetricPoint(name="test", value=1.0, timestamp=0.0, labels={}, type="counter")
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | model | MetricPoint 6 字段 Pydantic V2 |
| 2 | buffer | ring buffer 10000 capacity |
| 3 | flush | SQLite 批量写入原子性 |
| 4 | types | gauge/counter/histogram/summary 全覆盖 |
