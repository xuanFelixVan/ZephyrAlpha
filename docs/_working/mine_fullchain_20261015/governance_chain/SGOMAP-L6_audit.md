---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: GOMAP-L6
excavated: 2026-10-15
ttl: task_bound
---

# GOMAP-L6 审计族（治理运行七族之七，4 模块）

## 1. 定义

"事后要翻旧账"（legend review_ledger）——审计日志/状态面板/治理复盘。
SSOT：`config/governance_operations_map.yaml#families.L6_audit`（机生禁手改，generated_at=2026-10-09）。
实读数据：七族最小族，4 模块 = wired 3 + wired_by_header 1；孤儿 0 件、零触发 0 件——唯一全净族。

## 2. 六向台账

### 2.1 输入面
- pipeline GOM-L6"复盘审计"；mounts 3 件全实存核验（2026-10-15）：
  `src/zephyr/trading/status_dashboard.py`、`src/zephyr/trading/ai_audit_logger.py`、`scripts/ops_guard.py`
  （图 module 名 scripts.ops_guard；磁盘为单文件非目录）。
- 输入事件：全族台账回流（L0-L5 产物）、审计采样。

### 2.2 输出面
- 状态面板/审计日志 → Owner 复盘与裁定输入（立法流 D16-N1 呈报口的上游供血）。
- casebooks：RV1#全卷、RV2#全卷、AP#域五（指针制：docs/_working/branch_zero_takeover/review_findings{,_round2}.md、all_problems_ledger.md）。

### 2.3 SSOT 真源
- `config/governance_operations_map.yaml#families.L6_audit`。
- ROOR REG-MAP-GOMAP-001 450/94 漂移（族共性）。

### 2.4 代码模块
- 族内 4 件全实存。骨架代码指针"src/zephyr/gov_audit"实存（action_history.py、agent_signer.py 等，2026-10-15 ls），
  但注意：gov_audit 包未列入 GOM-L6 mounts（mounts 仅 trading 两件+ops_guard）——骨架指针与图挂载面存在口径差（gov_audit 属 audit 域但未挂七族），登记为口径注记非漂移。
- wired_by_header 1 件（头注释声明消费关系，机扫无 import 级消费者）。

### 2.5 门禁约束
- 无专属 gate；生成器重建守护。审计追踪政策 GOV-CMP-002（audit_trail_policy.md）为 planned 未建（nav_table_mapping.yaml 自declared）——审计面政策债在 NAV-7 记录。

### 2.6 自动化触发
- trigger_facts 七源；facts_sources 中 runtime_audit（20 文件）/gate_audit（98 文件）即本族典型落点声源。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 3 mounts 实存 |
| 输出面 | pass | 复盘→呈报口供血边在册 |
| SSOT 真源 | warn | ROOR 450/94 vs 429/64 漂移（族共性） |
| 代码模块 | pass | 4 件全实存零孤儿；gov_audit 未挂载为口径注记 |
| 门禁约束 | pass | 生成器守护 |
| 自动化触发 | pass | runtime/gate audit 声源实证 |

## 4. 缺口与建议

- 最小族（4 件）承载全图复盘职能，ops_guard 单文件挂载偏薄：建议随上户口批判读 gov_audit 包是否应挂 GOM-L6（骨架指针已指向它）。
- RV1/RV2/AP casebooks 真源均在 docs/_working/branch_zero_takeover/（工作区路径）——长期化时建议随 promote 迁移至永久区。
