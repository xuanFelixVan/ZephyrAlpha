---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: GOMAP-L0
excavated: 2026-10-15
ttl: task_bound
---

# GOMAP-L0 生命周期族（治理运行七族之一，64 模块）

## 1. 定义

"谁生谁死有登记"（legend birth_registry）——进程/服务出生走统一产房、退休走登记销户，不留无名进程。
SSOT：`config/governance_operations_map.yaml#families.L0_lifecycle`（schema 0.3，families 层生成器全量重建禁手改，
generator=`scripts/governance/generate_governance_map.py`，generated_at=2026-10-09）。
实读数据：族内 64 模块 = wired 32 + wired_dynamic 7 + wired_by_header 14 + suspect_orphan 11；零触发（trigger_facts.total=0）1 件。

## 2. 六向台账

### 2.1 输入面
- pipeline 人工语义层 GOM-L0"孵化"：统一 spawn 入口/NSSM 永久服务/boot 编排；mounts 8 件：
  `src/zephyr/shared/infra/process_pool.py`、`src/zephyr/shared/infra/process_lifecycle_gateway.py`、
  `src/zephyr/infrastructure/process_supervisor.py`、`zephyr.trading.windows_service`（已退役，见 2.4）、
  `src/zephyr/shared/lifecycle/daemon_registry.py`、`src/zephyr/trading/boot_hooks.py`、
  `src/zephyr/infrastructure/runtime/startup_shutdown.py`、`zephyr.trading.auto_runtime_core._OllamaProcessManager`。
- 输入事件：会话/任务起止（骨架 §2.6 口径）。

### 2.2 输出面
- 孵化产物的生命周期事件 → L1 监控（alive_proof）、L4 收割（reaper_duty）；daemon_registry 户籍供 L6 审计翻账。
- casebooks 挂载：AP#域一、RV2#缺口(R2-F2)、MM#全册（casebooks_legend 指针制，真源路径见图 casebooks_legend_zh）。

### 2.3 SSOT 真源
- `config/governance_operations_map.yaml#families.L0_lifecycle`（机生）。
- ROOR 发现行：`docs/registry_of_registries.yaml:629` REG-MAP-GOMAP-001——entry_count=450、description"suspect_orphans=94"，与图实读 429/64 漂移（对账结论见骨架缺口批与本次挖掘总报告）。

### 2.4 代码模块
- mounts 实存核验（2026-10-15）：8 件中 7 件实存；`zephyr.trading.windows_service` 已物理退役——commit 4577786d4e7
  "[C394 批退役] windows_service.py 物理退役（Owner 2026-10-08 批）"，零活 import 实证，但 pipeline 人工层 GOM-L0 mounts 仍挂载该名。
- 族内孤儿 11 件（wiring=suspect_orphan，图 families 层机扫）：`zephyr.shared.lifecycle.__init__`、
  `zephyr.infrastructure.lifecycle`、`zephyr.governance.lifecycle_governance.__init__`、`zephyr.pf_alloc.strategy_lifecycle_event`、
  `zephyr.orchestrator.execution.data_lifecycle`、`zephyr.feedback_loop.detectors.reliability.flag_lifecycle`、
  `zephyr.feedback_loop.gates.flag_lifecycle_manager`、`scripts.governance.meta.session_startup_check`、
  `scripts.governance.d5_architecture.lifecycle.detect_retirement_candidates`、
  `scripts.governance.d5_architecture.lifecycle.retire_module`、
  `scripts.governance.d5_architecture.validators.lifecycle.__init__`。
- 零触发 1 件（files=0 口径=源缺口非零触发，图 ssot_note 自declared）。

### 2.5 门禁约束
- 无 GOMAP 专属 gate_registry 行（grep GOVERNANCE-MAP/GOMAP 零命中）——families 层"禁手改"由生成器全量重建保证（重跑对拍即守护）。
- 孤儿处置门位：净删=Owner（宪法 §5），地图只登记（legend orphan_claim：孤儿要认领或销户）。

### 2.6 自动化触发
- trigger_facts 七源计数（图 facts_sources）：commit_queue_ledger 2008 文件、lookup_audit 824、reconcile_reports 752、gate_audit 98、runtime_audit 20、drift_watchdog 1、reaper_last_run 1。
- 下游联动：`src/zephyr/trading/process_reaper.py`（OS 计划任务 10min 心跳，本次实跑 source=live）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | warn | 8 mounts 中 1 件（windows_service）已退役仍挂载——人工语义层滞后于 2026-10-08 批退役 |
| 输出面 | pass | L1/L4/L6 交接边在册 |
| SSOT 真源 | warn | ROOR REG-MAP-GOMAP-001 计数漂移 450/94 vs 429/64（全族共性） |
| 代码模块 | pass | 孤儿 11 件为机扫已登记状态（orphan_claim 有主），非指针失效 |
| 门禁约束 | pass | 生成器重建守护，无 gate 属设计内 |
| 自动化触发 | pass | facts 七源+reaper live 实证 |

## 4. 缺口与建议

- GOM-L0 人工层陈旧 mount：windows_service 亡挂，建议下次人工语义层维护批删除该 mount 行（families 机生层不含它，不影响 counts）。
- 孵化双入口（process_pool vs process_lifecycle_gateway）合并候选 M1 已在图 disconnected 注记——维持登记，待上户口批呈批。
- ROOR 漂移为全七族共性，统一对账结论见总报告。
