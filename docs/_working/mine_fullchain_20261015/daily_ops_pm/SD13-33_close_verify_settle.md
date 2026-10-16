---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-33
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-33 收盘验证→三表结算（段序契约：verify 恒先于 settle）

## 1. 定义

日循环 16:45 圈内相邻两段：close_verify（收盘验证，src/zephyr/plan_engine/close_verifier.py，
验证表 scenario_hits 带触发时刻读数）与 settle（三表结算腿，按判定表族遍历），段序契约=
"verify 恒先于 settle"（钩子序，注释自证）。图内决策问题："verify 与 settle 的先后守住了吗？
结算今天扫到几行？"——已知结构事实（簿 09 §9.3）：结算腿扫到 0 行时静默空转，不区分
"本无事"与"该有活却扑空"。dloop_stages=[close_verify,settle] 且 in_phase_stages 双真
（machine_facts 实扫在相）。

## 2. 六向台账

### 2.1 输入面
- 入边：D13-30→31→33、D13-32→33（圈驱动+日K供料，map edges）。
- 段宿主：D13-32 圈内段（slot_source=dloop_stage，无独立时点）。
- 前置判定：D13-30 日K线+D13-32 圈已跑到该段（no_ready_gate_reason 承载）。

### 2.2 输出面
- close_verify 产物：scenario_hits 验证表（带触发时刻读数，骨架 §2 D13-33 行）。
- settle 产物：判定表族遍历结算留痕；扫 0 行时静默空转（failure 面不区分两类零）。
- consumers=count:22（code=14：src/zephyr/plan_engine/close_verifier.py:6、
  src/zephyr/plan_engine/daily_loop_master_switch.py:4、src/zephyr/plan_engine/daily_plan.py:4、
  src/zephyr/plan_engine/intraday_l1_tracker.py:10）。
- 下游：边 D13-33→D13-34（日度拍板）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-33（wired/partial/🔨）。
- 簿 07（段序契约）+簿 09 §9.3（0 行静默空转判定）；
  docs/_working/map_build/fig13_daycycle/07_dloop十六段解剖.md。
- 段序契约载体=代码注释（daily_loop_master_switch.py 钩子序自证）——真源降级为注释面。

### 2.4 代码模块
- module_id=MOD-PLAN-033；module_ref=src/zephyr/plan_engine/daily_loop_master_switch.py:225/:335
  （实存；本批实读 :335 命中 "trade_date" 段产物行、:225 为空行——锚半命中）。
- 段执行体：src/zephyr/plan_engine/close_verifier.py（实存）；PHASE_STAGES(:393) 含
  close_verify/settle（machine_facts dloop_facts in_phase 双真）。

### 2.5 门禁约束
- 段序契约 verify→settle：图把它升格为命名契约，但机械强制面未见（钩子序=约定序）。
- invalidation：本段产物随 16:45 圈产生，圈前判"零产出"即作废（同 D13-32）。
- 图 laws 第 6 条适用：结算腿 0 行静默空转="检出即蒸发"风险位（不区分本无事/扑空）。

### 2.6 自动化触发
- 机制=C_inprocess_stage；cadence declared="dloop 段内（无独立时点）"、observed="每圈 1 次"；
  trigger_facts metric=none（进程内段无独立产物表面，产物归上游槽节点计数）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 入边+段宿主关系清晰；in_phase 实扫双真 |
| 输出面 | warn | scenario_hits 读数在案，但结算腿 0 行静默空转（两类零不可区分=证据面缺口） |
| SSOT 真源 | warn | 段序契约真源=代码注释（自证面），无机械强制载体 |
| 代码模块 | pass | close_verifier.py+master_switch 实存，段在 PHASE_STAGES 实扫命中 |
| 门禁约束 | pass | invalidation/图 laws 纪律适用面完整在册 |
| 自动化触发 | warn | 进程内段无独立计数面（metric=none），节拍只能间接证明 |

## 4. 缺口与建议

- 不在本段 4 gap/11 未接线清单内（wired，段级节点）。
- 建议 1：结算腿"扫到 0 行"落一行空转心跳（遍历族清单+各行数），使"本无事"与"扑空"可区分
  （与 D13-G03 的 no_drift 留痕同族整改）。
- 建议 2：verify→settle 契约从注释升格为可测断言（settle 入口断言 close_verify 段状态=done），
  防钩子序被重排静默破坏。
