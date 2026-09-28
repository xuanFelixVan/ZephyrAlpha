---
ttl: task_bound
title: L11 案卷 F107 — 回滚恢复（双轨 checkpoint+四级回滚+G0 验证自愈，infrastructure/rollback 全包）
session: zc-l11-20260927
---

# F107 回滚恢复（K 段 G11，骨架态=built/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | gov_drift 漂移检测（cascade_detector.py/state_machine.py 引用锚）、feedback_loop（scheduler_act.py）、autonomy_core（kill_switch_orchestrator.py）、trading/boot_hooks.py（启动挂钩）——本日 grep 实证 24 文件生产引用 |
| 下游消费 | 全链回滚面：git 快照/SQLite dumper/venv 同步/s3 快照生命周期（包内 54 文件族）；escalation/contracts.py 消费锚 |
| 自动化触发 | rollback_bootstrap+rollback_boot_integration（boot_hooks 挂启动链）；rollback_scheduler/rollback_drill（演练）；F84 反馈循环 actor 面引用（feedback_loop/scheduler_act.py） |
| 真源与注册表 | 蓝图=MOD-INF-021，docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md（本日 ls 实存 blueprint+index）；rollback_executor.py:22 "蓝图 MOD-INF-021 §2.1 双轨数据模型 + §2.2 回滚流程"、:26 "四级回滚操作"——总册"双轨 checkpoint+四级回滚"字面实证 |
| 门禁与质量尺 | rollback_state_machine.py 头注：MATURITY production、INVARIANTS none（状态机本体无不变量声明=质量尺弱位）；commit_quality_gate.py/rollback_abuse_detector.py/rollback_loop_detector.py 自带滥用与死循环防护件 |
| 当前运行状态 | **绿偏黄**：包体 54 .py（本日 find 实数）+24 生产引用=接线活；黄点=state_machine INVARIANTS none、G0 验证自愈触发面依赖 boot_hooks（会话拉起型=半接线风险，同 wiring_gap §1.6 D 类口径） |

## 二、子模块三级枚举（src/zephyr/infrastructure/rollback/ 实扫 54 .py，按职能三级）

1. **执行核**：rollback_executor（双轨+四级）、rollback_state_machine、rollback_wal（预写日志）、rollback_lock、rollback_verifier、rollback_target_staleness、contract.py/contracts.py（双契约件并存=内收候选）。
2. **护栏族**：rollback_abuse_detector、rollback_loop_detector、hallucination_guard、cascade_failure_simulator、rollback_simulator、forensic、external_merkle_proof。
3. **checkpoint 与环境**：git_infra_snapshot、sqlite_dumper、venv_sync、submodule_sync、s3_snapshot_lifecycle、checkpoint_gc、knowngoodstate_ledger、semantic_rollback_tag、warm_standby。
4. **触发与编排**：rollback_bootstrap、rollback_boot_integration、auto_rollback_trigger、rollback_scheduler、rollback_drill、drift_fix、forward_fix_runner、env_watcher。
5. **外延面**：rollback_dashboard、runbook_generator、intent_archiver、rollback_context_restorer、temporal_context_adapter、agent_cooldown、budget_tracker/rollback_budget、complexity_budget、secret_rotation_aware、credential_rotation_trigger、vulnerability_rescanner、right_to_be_forgotten、topology_change_log、cross_platform_shell、audit/rollback_audit_nexus。

## 三、接线四态独立复核

- **回滚执行核：已接线**——24 文件生产引用（kill_switch_orchestrator/gov_drift 双件/feedback_loop/boot_hooks/pipeline_orchestrator 等锚点本日 grep 实取）。
- **启动挂载：半接线**——boot_hooks=会话/进程拉起型触发（wiring_gap §1.6 D 类"会话一停即饿死"同款风险）；heartbeat 兜底缺席（§2.3-5 Owner 门在案）。
- **drill 演练：未定期化**——rollback_drill 在包但计划任务群无 rollback 条目（resource_profile_registry 零命中口径，随 F76 车道核）。
- **弃用件：无**（54 文件全 kept，未发现 deprecated 头注）。

### 骨架勘误
1. 总册锚点"src/zephyr/infrastructure/rollback/"成立，但规模未记：**54 .py**，其中约 1/3 为预算/冷却/法忘权等外延件——"回滚恢复"名义包实际含自治安全外延域，G11 与 F107 档案描述宜收窄为"回滚核+护栏"，外延件归属随 90 普查 §三·D 域边界裁（infra_runtime 待裁项同源）。
2. contract.py 与 contracts.py 双契约件并存——同域重复簇（宪法 §4.2 内收候选），登记待收。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 启动挂载会话拉起型（饿死风险） | heartbeat 计划任务兜底（wiring_gap §2.3-5，held_overlap 计数账先落地=Owner 门） | P1 |
| 2 | rollback_state_machine INVARIANTS none | 补状态闭包不变量（production 件质量尺缺口） | P2 |
| 3 | 双契约件+外延域边界 | contract(s) 合并候选+域归属随裁-6 | P2 |

## 五、自审闸三态

**挖干（54 文件穷举+蓝图/四级/双轨字面锚+24 生产引用普查）✅；待裁（缺口#1 heartbeat 兜底=Owner 门在案；外延件域归属=裁-6 同源）；待挖（四级回滚逐级演练实证=随 F76 计划任务群车道，本卷不重挖）。**

## 六、复跑命令

```bash
find src/zephyr/infrastructure/rollback -name "*.py" | grep -v __pycache__ | wc -l   # 54
grep -n "四级回滚\|双轨" src/zephyr/infrastructure/rollback/rollback_executor.py | head -3   # :22/:26
grep -rln "infrastructure.rollback" src/zephyr --include="*.py" | grep -v __pycache__ | grep -v "/rollback/" | wc -l   # 24
ls docs/03_modules/_domain_autonomy_core/rollback_system/
```
