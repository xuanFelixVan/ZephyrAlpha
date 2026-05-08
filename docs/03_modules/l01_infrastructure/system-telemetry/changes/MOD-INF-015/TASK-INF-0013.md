---
task_id: "TASK-INF-0013"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §4——Cardinality 控制 + 僵尸指标清理 + 时钟偏差检测 + Counter 重置 + 幂等性"

title: "实现 metrics 高级数据质量保障：Cardinality/Zombie/ClockSkew/CounterReset/Idempotency"
description: |
  实现 metrics 子系统的全部数据质量保障机制：
  1. Cardinality 控制：标签白名单 + 基数上限 1000 自动聚合 + 800 告警 + TTL 7 天裁剪 + strict_mode FeatureFlag + zombie_scan
  2. 僵尸指标与标签清理：每 7 天扫描无写入指标→ZOMBIE→隐藏→30天物理删除→再次写入自动复活
  3. 时钟偏差检测：monotonic clock 测时长 + wall clock 排序 + 每 5min skew metric + 偏差 >100ms→P2/>1s→P1
  4. Counter 重置检测：process_start_ts 标签 + FLE reset-aware + 10min stale detection + delta recording
  5. 幂等性：idempotency_key={module}_{metric}_{ts_ns}_{nonce} + flush dedup 72h + Counter exactly-once
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\cardinality.py"
    description: "Cardinality 控制器——标签白名单/上限/聚合/TTL/zombie_scan"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\clock_guard.py"
    description: "时钟偏差防护——monotonic clock + skew metric + TraceParent 对齐"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\counter_reset.py"
    description: "Counter 重置检测——process_start_ts + stale + delta recording"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\idempotency.py"
    description: "幂等性保障——idempotency_key 生成 + dedup table 72h"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\cardinality.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\clock_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\counter_reset.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\idempotency.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§4——Cardinality 控制策略表 + Zombie 清理流程 + 时钟偏差防护 + Counter 重置 + 幂等性机制"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "cardinality_limit=1000 → 第 1001 个 label 组合自动聚合"
  - "7 天无写入指标 → ZOMBIE 标记"
  - "monotonic clock 时长与 wall clock 时长一致"
  - "process restart → counter 从 0 开始 + delta recording 重建"
  - "同一 idempotency_key 72h 内重复写入 → dedup 只保留第一条"

rollback_instructions: |
  1. 删除 cardinality.py / clock_guard.py / counter_reset.py / idempotency.py

depends_on:
  - "TASK-INF-0012"
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

# TASK-INF-0013: metrics 高级数据质量保障

## 目标
实现 Cardinality 控制、僵尸指标清理、时钟偏差检测、Counter 重置检测、幂等性保障五大机制。

## 执行步骤

### 读
- 蓝图 §4：Cardinality 表/Zombie 流程/Clock Skew 防护/Counter Reset 机制/Idempotency 机制

### 做
1. cardinality.py：白名单 + 上限聚合 + 告警 + TTL + zombie_scan
2. clock_guard.py：dual clock + skew metric + TraceParent 对齐
3. counter_reset.py：process_start_ts + stale + delta
4. idempotency.py：key gen + dedup table 72h

### 检
每个模块独立单元测试

## 验收标准
| # | 指标 | 目标值 |
|---|------|--------|
| 1 | cardinality | >1000→聚合, >800→告警 |
| 2 | zombie | 7天→ZOMBIE, 30天→物理删除 |
| 3 | clock | monotonic span duration=wall clock span duration |
| 4 | counter | restart→delta 重建 |
| 5 | dedup | 72h 同 key→只保留第一条 |
