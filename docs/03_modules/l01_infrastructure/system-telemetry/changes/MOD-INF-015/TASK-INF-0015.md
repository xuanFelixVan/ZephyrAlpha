---
task_id: "TASK-INF-0015"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §5 logs 子系统"

title: "实现 logs 子系统：基于 shared/logging 的结构化日志 + JSONLFileWriter + PII 脱敏"
description: |
  基于 shared/logging.py（TraceContext + get_logger + _StructuredFormatter）构建 logs 子系统的持久化层：
  1. JSONLFileWriter——按日轮转，文件名 {date}.jsonl，路径 data/telemetry/{env}/logs/
  2. 自动注入 trace_id/span_id（从 shared.logging.TraceContext 提取）
  3. 日志分级：DEBUG/INFO/WARNING/ERROR/FATAL
  4. PII 脱敏 filter processor：API Key/Token/密码/email/IP/路径脱敏
  5. fail-closed 降级链：JSONL write fail → stderr fallback → 内存环形区缓冲(1000条) → 丢弃+告警
  6. 数据分级 sensitivity_level：public/internal/confidential/secret
  7. 日志与 Trace 关联：每条 JSONL line 含 trace_id + span_id
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\audit_trail\writer.py"
    description: "JSONLFileWriter——按日轮转 + trace_id 自动注入"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\logs\\pii_masker.py"
    description: "PII 脱敏 filter——6 类敏感字段检测与脱敏"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\logs\\writer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\logs\\pii_masker.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§5——采集流程 + 日志分级 + 与 Trace 关联 JSON 格式 + 安全性控制（脱敏/分级/降级链）"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging.py"
    reason: "shared/logging TraceContext + get_logger——logs 子系统的基底"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "JSONL 文件按日轮转——{date}.jsonl"
  - "每条 log line 自动注入 trace_id + span_id"
  - "API Key sk-abc123 → sk-****"
  - "email user@domain.com → u***@domain.com"
  - "IP 192.168.1.1 → 192.168.*.*"
  - "JSONL write fail → stderr fallback"
  - "内存环形区 full → 丢弃+告警"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\logs\writer.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\logs\pii_masker.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0006"
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

# TASK-INF-0015: logs 子系统实现

## 目标
基于 shared/logging 构建 logs 子系统的持久化层，实现按日轮转 JSONL 存储 + 自动 trace 关联 + PII 脱敏 + fail-closed 降级。

## 执行步骤

### 读
- 蓝图 §5：完整设计
- shared/logging.py：TraceContext/JSON Formatter

### 做
1. JSONLFileWriter：按日轮转、trace_id/span_id 自动注入
2. PIIMasker：6 类脱敏规则
3. fail-closed 降级链

### 检
```python
from zephyr.l12_system_telemetry.logs.writer import JSONLFileWriter
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | rotation | 按日轮转 |
| 2 | trace | trace_id 自动注入 |
| 3 | pii | 6 类脱敏正确 |
| 4 | degrade | fail→stderr→buffer→drop |
