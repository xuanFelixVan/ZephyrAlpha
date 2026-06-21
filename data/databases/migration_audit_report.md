# 旧库与新库数据完整性审计报告

生成时间: 2026-06-13T01:15:05.202528

---

## 1. 旧库 data/databases/governance.db

| 表名 | 行数 |
|------|------|
| _schema_version | 27 |
| circuit_breaker_state | 0 |
| events | 49029 |
| fle_alerts | 3 |
| fle_dispatch_log | 3 |
| fle_metrics | 99613 |
| gates | 10047 |
| handoffs | 1 |
| judgment_records | 0 |
| ke_tombstones | 3 |
| knowledge | 398 |
| slow_queries | 0 |
| sqlite_sequence | 3 |
| task_events | 12 |
| task_files | 0 |
| task_snapshots | 0 |
| tasks | 273 |
| telemetry_metrics | 35 |
| tx_idempotency | 0 |

## 2. 新库 governance.db

| 表名 | 行数 |
|------|------|
| _schema_version | 1 |
| audit_entries | 1 |
| audit_summary | 1 |
| circuit_breaker_state | 0 |
| costs | 0 |
| domains | 0 |
| drift_events | 1 |
| fix_records | 1 |
| fle_alerts | 1 |
| fle_dispatch_log | 1 |
| fle_metrics | 1 |
| gate_decisions | 1 |
| gates | 0 |
| integrity_records | 1 |
| judgment_records | 1 |
| ke_tombstones | 0 |
| knowledge | 0 |
| rule_enforcement_log | 1 |
| scan_results | 1 |
| slow_queries | 1 |
| sqlite_sequence | 17 |
| task_events | 0 |
| task_files | 0 |
| task_snapshots | 0 |
| tasks | 0 |
| tx_idempotency | 0 |
| usage_records | 1 |

## 3. 旧库 data/databases/governance.db

| 表名 | 行数 |
|------|------|
| sqlite_sequence | 1 |
| usage_records | 5 |

## 4. 数据缺失分析

### 4.1 旧库有但新库缺失或数据量不足的表

| 旧表 | 旧行数 | 新表 | 新行数 | 差异 | 状态 |
|------|--------|------|--------|------|------|
| events | 49029 | (无对应表) | - | 49029 | **缺失** |
| fle_metrics | 99613 | fle_metrics | 1 | 99612 | **不足** |
| gates | 10047 | gates | 0 | 10047 | **缺失** |
| knowledge | 398 | knowledge | 0 | 398 | **缺失** |
| tasks | 273 | tasks | 0 | 273 | **缺失** |
| fle_alerts | 3 | fle_alerts | 1 | 2 | **不足** |
| fle_dispatch_log | 3 | fle_dispatch_log | 1 | 2 | **不足** |
| ke_tombstones | 3 | ke_tombstones | 0 | 3 | **缺失** |
| task_events | 12 | task_events | 0 | 12 | **缺失** |
| telemetry_metrics | 35 | (无对应表) | - | 35 | **缺失** |
| handoffs | 1 | (无对应表) | - | 1 | **缺失** |
| usage_records (data/databases/governance.db) | 5 | usage_records (governance.db) | 1 | 4 | **不足** |

## 5. 迁移优先级总结

### 必须迁移的数据（按优先级排序）

1. **tasks** (269行) - 任务卡数据，核心业务数据
2. **events** (49029行) - 事件日志，审计追踪
3. **fle_metrics** (99613行) - FLE 指标数据
4. **gates** (10047行) - 门禁决策记录
5. **knowledge** (398行) - 知识库条目
6. **telemetry_metrics** (35行) - 遥测指标
7. **task_events** (12行) - 任务事件日志
8. **fle_alerts** (3行) - FLE 告警
9. **fle_dispatch_log** (3行) - FLE 调度日志
10. **ke_tombstones** (3行) - 知识条目标记
11. **handoffs** (1行) - 交接记录
12. **usage_records** (5行) - 使用记录（从 data/databases/governance.db）


### 需要新建的表

- **events** - 旧库有，新库没有对应表
- **telemetry_metrics** - 旧库有，新库没有对应表
- **handoffs** - 旧库有，新库没有对应表


## 6. 结论

**新库数据严重不完整**。DM-100013 的迁移脚本只创建了表结构，没有迁移实际数据。

必须执行 DM-100061 完整迁移旧库数据到新库，然后才能安全删除旧库。
