---
task_id: "TASK-INF-0019"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §8 archive 子系统 + §8b 遥测成本预算"

title: "实现 archive 子系统：分层归档 + 灾备恢复 + 遥测成本预算与三级降级"
description: |
  1. 归档策略：metrics 30天→archive / logs 30天→gzip / traces 7天→gzip / profiles 14天→gzip / archive 90天→物理删除
  2. 灾备恢复：SQLite .backup 每日 + archive JSONL replay + 全盘故障→外部备份恢复
  3. 遥测成本模型：磁盘 10GB / CPU 10%单核 / 内存 512MB / LLM $0.50/月
  4. 成本感知三级降级：磁盘>80%→dev TTL减半+采样降频+P2告警 / >95%→dev暂停+staging降级+profiles关闭+P1 Feishu / =100%→仅prod+P0 Feishu
  5. 成本仪表板：磁盘用量趋势+CPU开销+30天耗尽预测
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\archive\\reaper.py"
    description: "分层归档引擎——gzip 压缩 + TTL reaper + auto_cleanup FeatureFlag"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\archive\\disaster_recovery.py"
    description: "灾备恢复——SQLite .backup + archive replay 重建"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\archive\\cost_budget.py"
    description: "遥测成本预算——磁盘/CPU/内存监控 + 三级降级逻辑"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\archive\\**\\*.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§8——归档策略+灾备恢复矩阵(RTO/RPO)+§8b——成本模型+三级降级流程+成本仪表板"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 9000
timeout_minutes: 35

acceptance_criteria:
  - "30 天后 metrics archive→gzip"
  - "90 天 archive→物理删除（auto_cleanup=ON）"
  - "SQLite .backup 每日作业可执行"
  - "archive JSONL replay 重建→数据完整性≥99.9%"
  - "磁盘>80%→P2, >95%→P1 Feishu"
  - "成本仪表板指标可查询"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\archive\reaper.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\archive\disaster_recovery.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\archive\cost_budget.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0004"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
  - "finops"
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

# TASK-INF-0019: archive 子系统 + 成本预算

## 目标
实现分层归档、灾备恢复、遥测成本控制三级降级策略。

## 执行步骤

### 读
- 蓝图 §8/§8b：归档策略/灾备矩阵/成本模型/降级流程

### 做
1. reaper.py：分级 TTL 归档 + gzip + auto_cleanup
2. disaster_recovery.py：.backup + archive replay
3. cost_budget.py：预算监控 + 三级降级

### 检
```python
from zephyr.l12_system_telemetry.archive.reaper import ArchiveReaper
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | archive | 分级 TTL |
| 2 | dr | archive replay 99.9% |
| 3 | cost | 3-level degrade |
