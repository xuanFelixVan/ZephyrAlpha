---
task_id: "TASK-INF-0020"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §9 profiles 子系统"

title: "实现 profiles 子系统：CPU/内存连续性能剖析 + py-spy 集成 + 性能回归检测"
description: |
  实现 OTel Profiles signal 对齐的连续性能剖析：
  1. Python profiler（py-spy/Austin）每 60s 采集 10s CPU/内存样本
  2. 生成 pprof 格式→本地存储 profiles/{date}/{module}_{timestamp}.pprof.gz（TTL 14 天）
  3. 监测维度：CPU 热点/内存分配/阻塞分析(IO wait+lock contention)/GIL 竞争
  4. FLE 性能回归检测：每日基线 vs 新部署→ function duration delta>30%→PERF-REGRESSION→自动派单
  5. FeatureFlag telemetry.enable_profiling 控制（默认 OFF），环境感知 dev=OFF/staging=50%/prod=100%
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\profiles\\collector.py"
    description: "profiles 采集器——py-spy 集成 + pprof 生成"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\profiles\\regression.py"
    description: "性能回归检测——基线对比 + delta 告警"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\profiles\\**\\*.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§9——采集流程 + 4 监测维度 + FLE 消费流程"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "py-spy 采集→pprof.gz 输出"
  - "4 维度数据可提取（CPU/内存/IO/GIL）"
  - "FeatureFlag OFF→采集停止"
  - "环境差异化采样率正确"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\profiles\collector.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\profiles\regression.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0004"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
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

# TASK-INF-0020: profiles 子系统实现

## 目标
实现连续性能剖析——CPU/内存火焰图采集 + 性能回归自动检测。

## 执行步骤

### 读
- 蓝图 §9：采集流程 + 4 监测维度 + FLE 消费

### 做
1. collector.py：py-spy 集成 + pprof.gz
2. regression.py：基线对比 + delta 告警

### 检
```python
from zephyr.l12_system_telemetry.profiles.collector import ProfileCollector
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | collect | pprof.gz output |
| 2 | flag | OFF→stop |
| 3 | env | dev=0%/staging=50%/prod=100% |
