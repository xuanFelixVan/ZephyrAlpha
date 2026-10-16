---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: GOMAP-L3
excavated: 2026-10-15
ttl: task_bound
---

# GOMAP-L3 熔断族（治理运行七族之四，21 模块）

## 1. 定义

"紧急刹车人人可拉"（legend emergency_brake）——kill_switch/熔断器/降级级联/死人开关。
SSOT：`config/governance_operations_map.yaml#families.L3_fuse`（机生禁手改，generated_at=2026-10-09）。
实读数据：21 模块 = wired 16 + wired_dynamic 1 + wired_by_header 2 + suspect_orphan 2；零触发 0 件。

## 2. 六向台账

### 2.1 输入面
- pipeline GOM-L3"熔断降级"；mounts 8 件全实存核验（2026-10-15）：
  `src/zephyr/security/access_control/kill_switch.py`、`src/zephyr/infrastructure/rollback/kill_switch.py`、
  `src/zephyr/infrastructure/capacity_assurance/kill_switch.py`、
  `src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py`、
  `src/zephyr/shared/resilience/circuit_breaker.py`、`src/zephyr/feedback_loop/resilience/deadman_switch.py`、
  `src/zephyr/governance/resilience_governance/emergency_track_guardian.py`、
  `src/zephyr/autonomy_core/killswitch_response_levels.py`。
- 输入事件：L1 监控告警（骨架口径）/escalation 末端激活。

### 2.2 输出面
- 停机指令 → L4 收割族；保命动作唯一入口=route_incident（MOD-AU-002 路由层）。
- casebooks：空（病历缺口显式登记——图 casebooks_note：熔断/kill_switch 域无永久病历册，
  `.runtime/audit/kill_switch_orchestrator.jsonl` 是 facts 流非病历本）。

### 2.3 SSOT 真源
- `config/governance_operations_map.yaml#families.L3_fuse`。
- ROOR REG-MAP-GOMAP-001 450/94 漂移（族共性）。

### 2.4 代码模块
- 入口收敛实证（2026-09-18 wiresafe BRK-064/066）：策略层 MOD-AU-004（killswitch_response_levels）→
  路由层 MOD-AU-002 route_incident（`src/zephyr/autonomy_core/kill_switch_orchestrator.py`，wired，consumers=
  emergency_track_guardian+boot_hooks）→ 5 套本体；boot 同批注册（`src/zephyr/trading/boot_hooks.py` 实存）。
- 图内注记：生产侧 respond() 调用点仍为 0（记黄，施工包 lanes/wiresafe_BRK-064_construction_pack.md）。
- 孤儿 2 件：`scripts.arch_guard.fitness_functions.check_kill_switch_latency`（触发 111）、
  `zephyr.infrastructure.kill_switch_sim`（触发 2295 但 0 消费；图注记净删候选只登记不删——净删=Owner 门位）。

### 2.5 门禁约束
- 无专属 gate；生成器重建守护。宪法 §7 入口：`zephyr.security.access_control.kill_switch`（实存）。

### 2.6 自动化触发
- trigger_facts：族内最高 `zephyr.infrastructure.capacity_assurance.kill_switch`/`rollback.kill_switch`/
  `security.access_control.kill_switch` 三件各 26510 触发（gate_audit 25544 为主源）；deadman_switch 2523。
- deadman/熔断均为事件触发语义（宪法 §9.3 禁 cron 口径一致）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 8 mounts 全实存 |
| 输出面 | pass | route_incident 唯一入口+L4 交接 |
| SSOT 真源 | warn | ROOR 450/94 vs 429/64 漂移（族共性） |
| 代码模块 | warn | 孤儿 2 件（kill_switch_sim 净删候选待 Owner）；respond() 生产调用点 0 记黄在案 |
| 门禁约束 | pass | 生成器守护 |
| 自动化触发 | pass | 26510 触发三连实证，事件触发语义合规 |

## 4. 缺口与建议

- 熔断域病历册缺位（图自报）：建议事件流 jsonl 归档成册随上户口批呈批。
- kill_switch_sim 净删候选与 capacity_assurance/kill_switch 域重复面：维持登记待 Owner 净删裁定。
- respond() 调用点为 0：路由层已收敛但生产触发链未闭环，BRK-064 施工包在案，建议排期收口。
