---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: GOMAP-L2
excavated: 2026-10-15
ttl: task_bound
---

# GOMAP-L2 资源族（治理运行七族之三，63 模块）

## 1. 定义

"资源见底前要喊"（legend resource_alert）——内存/CPU/GPU/磁盘阈值与告警、预算管理。
SSOT：`config/governance_operations_map.yaml#families.L2_resource`（机生禁手改，generated_at=2026-10-09）。
实读数据：63 模块 = wired 28 + wired_dynamic 3 + wired_by_header 11 + suspect_orphan 21；零触发 2 件。
孤儿占比 21/63≈33%——七族最高。

## 2. 六向台账

### 2.1 输入面
- pipeline GOM-L2"资源水位"；mounts 6 件全实存核验（2026-10-15）：
  `src/zephyr/gov_drift/resource_guard.py`、`src/zephyr/trading/resource_optimization.py`、
  `src/zephyr/trading/gpu_monitor.py`、`src/zephyr/data_eng/gpu_resource_manager.py`、
  `src/zephyr/infrastructure/capacity_assurance/host_resource_governor.py`、
  `src/zephyr/security/llm_defense/llm_security/layers/l5_resource_protection.py`。
- config_refs 3 件全实存：`config/resource_optimization.yaml`、`config/alert_rules.yaml`、`config/gguf_vram_budget.yaml`。
- 输入事件：资源画像/水位阈值（骨架 §2.6 口径）。

### 2.2 输出面
- 水位告警 → 排班闸（骨架口径）/L3 熔断；OpsAlertFeed 通知板（BRK-066 链路，见 2.4）。
- casebooks：AP#域三（兼挂；资源域专属病历册缺位=候选缺口，随上户口批呈批——图 casebooks_note 自declared）。

### 2.3 SSOT 真源
- `config/governance_operations_map.yaml#families.L2_resource`。
- 阈值真源实例：ALERT-SYS-003/004/005 在 `config/alert_rules.yaml`（图 disconnected BRK-066 记载）。
- ROOR REG-MAP-GOMAP-001 450/94 漂移（族共性）。

### 2.4 代码模块
- 关键链实证（wiresafe BRK-066，2026-09-18）：`host_resource_governor` 由硬编码假通道治本为实探（RAM+commit charge+CPU），
  消费方=`src/zephyr/trading/process_reaper.py`（图 consumers_count=1 吻合），OS 计划任务 10min 心跳 → OpsAlertFeed。
- 孤儿 21 件（全清单机扫在册），重点：`zephyr.autonomy_core.context.complexity_budget`（触发 7271 但 0 消费）、
  `zephyr.governance.context_governance.context_budget`（触发 10657 但 0 消费——与 autonomy_core.context.context_budget
  同名双件，后者 wired_by_header）、`zephyr.integration.budget_enforcer.__init__`、`zephyr.infrastructure.hot_plane_budget`、
  `.../warm_plane_budget`、`.../capacity_assurance.cross_module_integration`、`.../tech_stack`、`.../contracts`。
- 零触发 2 件：`scripts.governance.d12_ai_hallucination.validate_session_budget`、`scripts.governance.meta.manage_error_budget`。

### 2.5 门禁约束
- 无专属 gate；生成器重建守护。净删候选只登记不删（净删=Owner 门位，宪法 §5）。

### 2.6 自动化触发
- trigger_facts 七源；reaper 心跳消费水位判据（本次实跑 watermark 块 live 输出：ram_used_pct=57.0、commit_pct=47.12、degraded=False）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 6 mounts+3 config_refs 全实存 |
| 输出面 | pass | L3/排班闸/OpsAlertFeed 在册 |
| SSOT 真源 | warn | ROOR 450/94 vs 429/64 漂移（族共性） |
| 代码模块 | warn | 孤儿 21 件 33% 七族最高；context_budget 同名双件一孤一挂=重复簇显影位（legend no_duplicate） |
| 门禁约束 | pass | 生成器守护+Owner 门位规则明确 |
| 自动化触发 | pass | watermark live 实证；2 件零触发已按口径登记为源缺口 |

## 4. 缺口与建议

- context_budget 同名双件（autonomy_core vs governance 两包）建议按 no_duplicate 判据收敛唯一。
- 预算类孤儿 9 件（*budget*）同簇，适合一次打包认领/退役。
- 资源域专属病历册缺位（图自报）维持候选登记。
