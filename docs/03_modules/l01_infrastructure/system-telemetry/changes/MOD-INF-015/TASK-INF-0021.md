---
task_id: "TASK-INF-0021"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §10 health 子系统——Watchdog + LifecycleManager + §10b Meta-Telemetry"

title: "实现 health 子系统：独立 Watchdog 进程 + LifecycleManager 轮询 + Meta-Telemetry 自体内省"
description: |
  1. 独立 watchdog 进程：每 10s ping Telemetry / 每 30s 通过 LifecycleManager 轮询所有模块 health_check()
     健康评分=weighted_avg(自身+各模块 ModuleHealth) / 评分<0.7→重启→失败→Escalation→Feishu
     自保：OS systemd/Windows Service 自动重启
  2. 6 项健康检查：buffer占用率/log writer延迟/trace collector吞吐/schema validator拒绝率/进程alive/disk space
  3. Meta-Telemetry（B81）：12 维 meta-metric（ingress_rate/flush_duration/batch_size/buffer_depth/dropped_total/
     log_write_duration/spans_collected/sampled_ratio/schema_rejection/dlq_size/storage/per_module_top10）
  4. Meta-Metrics 独立存储 telemetry_meta 表（不污染 Discovery API）→3 类消费者（Watchdog/FLE/AI）
  5. Meta-Metrics 独立 TTL：high-freq 7天/medium 30天/module-aggregate 90天
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\telemetry\watchdog.py"
    description: "独立 watchdog 进程——健康轮询 + 自动重启 + Escalation"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\health\\checker.py"
    description: "6 项健康检查执行器"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\health\\meta_telemetry.py"
    description: "Meta-Telemetry——12 维自体内省指标采集 + telemetry_meta 表"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\health\\**\\*.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§10——Watchdog 设计 + 健康检查维度 + 自保设计 + §10b——12 Meta-Metrics + 存储策略 + 3 消费者"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "watchdog 独立进程——非 Telemetry 进程内"
  - "每 30s 轮询所有 LifecycleManager 已注册模块 health_check()"
  - "健康评分<0.7→重启 Telemetry"
  - "12 项 meta-metric 全部可采集"
  - "telemetry_meta 独立表存储——不污染 Discovery API"
  - "MCP get_telemetry_health() 暴露 meta-metric 给 AI"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\health\watchdog.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\health\checker.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\health\meta_telemetry.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0009"
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

# TASK-INF-0021: health 子系统 + Meta-Telemetry

## 目标
实现独立 watchdog 进程 + LifecycleManager 轮询 + 12 维 Meta-Telemetry 自体内省。

## 执行步骤

### 读
- 蓝图 §10/§10b：Watchdog + 健康检查 + Meta-Telemetry 12 维

### 做
1. watchdog.py：独立进程 + 健康评分 + 重启逻辑
2. checker.py：6 项健康检查
3. meta_telemetry.py：12 meta-metrics + telemetry_meta 表

### 检
```python
from zephyr.l12_system_telemetry.health.meta_telemetry import MetaMetricsCollector
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | watchdog | 独立进程 |
| 2 | poll | 30s lifecycle scan |
| 3 | meta | 12 metrics 可采集 |
| 4 | table | telemetry_meta 独立 |
