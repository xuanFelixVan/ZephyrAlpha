---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: GOMAP-L1
excavated: 2026-10-15
ttl: task_bound
---

# GOMAP-L1 监控族（治理运行七族之二，143 模块）

## 1. 定义

"你还活着吗"（legend alive_proof）——心跳/探针/看门狗互检：证明系统活着，死了立刻有人知道。
SSOT：`config/governance_operations_map.yaml#families.L1_monitor`（机生禁手改，generated_at=2026-10-09）。
实读数据：七族最大族，143 模块 = wired 84 + wired_dynamic 1 + wired_by_header 41 + suspect_orphan 17；零触发 1 件。

## 2. 六向台账

### 2.1 输入面
- pipeline GOM-L1"运行监控"：心跳/健康探针/看门狗互检/遥测；mounts 13 件全实存核验（2026-10-15）：
  `src/zephyr/infrastructure/system_telemetry/watchdog.py`、`.../health_probes.py`、`.../health_aggregator.py`、
  `src/zephyr/trading/health_monitor.py`、`src/zephyr/shared/lifecycle/healthcheck_service.py`、
  `.../health_discovery.py`、`.../longevity_monitor.py`、`src/zephyr/shared/maintenance/autonomy_monitor.py`、
  `src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py`、`src/zephyr/data/redundant_source/heartbeat_monitor.py`、
  `src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py`、`src/zephyr/risk/core/drawdown_watchdog.py`、
  `src/zephyr/integration/vector_memory/index_health_monitor.py`。
- 输入事件：运行面心跳/遥测（骨架 §2.6 口径）。

### 2.2 输出面
- 告警/异常 → L3 熔断族（emergency_brake 触发前哨）；遥测落点 → L6 审计族。
- casebooks：AP#域一、RV2#观察(I-2)、RV2#缺口(R2-F1)。

### 2.3 SSOT 真源
- `config/governance_operations_map.yaml#families.L1_monitor`。
- ROOR REG-MAP-GOMAP-001（`:629`）——450/94 漂移（族共性，见总报告）。

### 2.4 代码模块
- 孤儿 17 件（机扫在册，含大块 feedback_loop/diagnosers/health 子族：`global_health_map`、`memory_self_check`、
  `model_health`、`self_benchmark`、`self_llm_observability`、`dr_resilience_metrics`、`fle_self_slo_metrics`；
  及 `zephyr.infrastructure.health_monitor`、`zephyr.ops.ch_health_probe`、`scripts.ops.e2e_ch_alert_probe`、
  `zephyr.autonomy_core.context.context_health_score`、`zephyr.autonomy_core.skills.skill_telemetry`、
  `zephyr.feedback_loop.detectors.correlation.external_health`、`.../reliability.ebpf_monitor`、
  `.../gates.scope_creep_monitor`、`.../system_telemetry.otel_instrumentation`、
  `zephyr.security.llm_defense.llm_security.poisoning_monitor`）。
- disconnected 记载（人工层）：`zephyr.infrastructure.health_monitor.health_aggregator` 已删（2026-09-15 R1 CONFIRMED-DEAD 零外部 import，活聚合器=system_telemetry 版）——与孤儿清单中 `zephyr.infrastructure.health_monitor` 同域线索。

### 2.5 门禁约束
- 无专属 gate；families 层生成器重建守护。worktree_drift_watchdog 有持久落点（facts_sources.drift_watchdog files=1）。

### 2.6 自动化触发
- trigger_facts 七源全族计数；heartbeat_daemon/watchdog 常驻进程语义；reaper 10min 心跳互检（本次实跑 live）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 13 mounts 全实存 |
| 输出面 | pass | L3/L6 交接边在册 |
| SSOT 真源 | warn | ROOR 450/94 vs 429/64 漂移（族共性） |
| 代码模块 | warn | 孤儿 17 件占族内 12%（七族第二高），health_monitor 域疑似删除残留双记载（disconnected 已删 vs families 在册）需认领或销户 |
| 门禁约束 | pass | 生成器守护 |
| 自动化触发 | pass | facts 源+常驻进程实证 |

## 4. 缺口与建议

- L1 孤儿簇（feedback_loop/diagnosers/health 9 件）建议按 orphan_claim 规则批量认领或退役——同簇同判据，适合一次上户口批打包。
- `zephyr.infrastructure.health_monitor`（families 在册）vs disconnected 已删记载并存，建议生成器侧核对：若物理文件已删则应从 families 退场。
