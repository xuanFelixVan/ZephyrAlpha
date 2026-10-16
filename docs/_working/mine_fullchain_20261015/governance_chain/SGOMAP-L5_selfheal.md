---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: GOMAP-L5
excavated: 2026-10-15
ttl: task_bound
---

# GOMAP-L5 自愈族（治理运行七族之六，95 模块）

## 1. 定义

"坏了要自己好"（legend self_heal）——reconciler 事件驱动修复，对不上就修，禁定时空转。
SSOT：`config/governance_operations_map.yaml#families.L5_selfheal`（机生禁手改，generated_at=2026-10-09）。
实读数据：七族第二大族，95 模块 = wired 63 + wired_dynamic 1 + wired_by_header 25 + suspect_orphan 6；零触发 0 件。

## 2. 六向台账

### 2.1 输入面
- pipeline GOM-L5"自愈对账"；mounts 6 件全实存核验（2026-10-15）：
  `src/zephyr/infrastructure/auto_fix_engine/self_heal_agent.py`、
  `src/zephyr/governance/semantic_audit/self_healer.py`、
  `src/zephyr/governance/resilience_governance/f5_boot_integration.py`、
  `src/zephyr/governance/audit/reconcile_worker.py`、`.../reconcile_runner.py`、`.../reconciliation_registry.py`。
- 输入事件：L4 收割产物/对账差异（事件触发，禁 cron——宪法 §9.3）。

### 2.2 输出面
- 修复结果落库/落账 → L6 审计复盘；reconcile_reports facts 源（752 文件）。
- casebooks：SV#方案、SV#裁定、DCS#队列、AP#域三（指针制）。

### 2.3 SSOT 真源
- `config/governance_operations_map.yaml#families.L5_selfheal`。
- ROOR REG-MAP-GOMAP-001 450/94 漂移（族共性）。

### 2.4 代码模块
- 事件触发实证：d8_doc_sync 五件 reconciler（agents_cheatsheet_drift/algo_flow_translation/metric_count_drift/
  readme_version_sync/requirements_version_sync）consumers 全部=`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`
  （图 consumers 字段+文件实存双证）——即提交网关事件驱动，非 Timer。
- `scripts/backup/backup_reconciler.py`（wired，consumer=git_commit_gateway）。
- 孤儿 6 件：`scripts.governance.generate_gate_face_reconciliation`（触发 1116 但 0 消费）、
  `scripts.governance.repair.concurrent_write_test`、`scripts.governance.repair.p2_pg_concurrent_test`、
  `zephyr.feedback_loop.diagnosers.health.self_health_monitor`、
  `zephyr.feedback_loop.diagnosers.reliability.capacity_aware_repair`、
  `zephyr.feedback_loop.gates.blueprint_code_reconciler`。
- 骨架指针核验：`src/zephyr/infrastructure/auto_fix_engine`（骨架称"11 修复器"）——self_heal_agent 实存；修复器数量未逐一清点（族级挖掘以图 counts 为准）。

### 2.5 门禁约束
- 无专属 gate；生成器重建守护。 reconciler 必须**事件触发**为运维红线（宪法 §9.3），图内 wired 件全部满足。

### 2.6 自动化触发
- trigger_facts 七源；reconcile_reports 752 文件为全图第二大声源。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 6 mounts 实存 |
| 输出面 | pass | L6 交接+reports 声源 |
| SSOT 真源 | warn | ROOR 450/94 vs 429/64 漂移（族共性） |
| 代码模块 | warn | 孤儿 6 件（含 blueprint_code_reconciler——自愈族自己的门件无人消费）；事件触发合规无违例 |
| 门禁约束 | pass | 宪法 §9.3 红线+图内全 wired 件合规 |
| 自动化触发 | pass | git_commit_gateway 事件链实证 |

## 4. 缺口与建议

- generate_gate_face_reconciliation（1116 触发 0 消费）：触发多消费零=典型"喊了没人听"，建议认领或退役。
- blueprint_code_reconciler 孤儿：蓝图-代码对账件未接线，与 nav-F 维（蓝图-代码同步）有合并候选关系，建议随上户口批判读。
