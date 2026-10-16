---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-27
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-27 盘中持仓对账事件入口（与 D13-29 分工）

## 1. 定义

持仓对账器（src/zephyr/ex_core/position_reconciler.py）两条腿之一：事件入口腿——由成交回报
（execution_report）事件驱动盘中持仓对账。图内决策问题："对账到底由事件触发还是定时器触发？
事件入口腿今天醒过吗？"——图硬实查判定：事件入口腿零调用（entry_leg_unwired=true）、真跑的是
进程内定周期腿；排班注释的两句自辩与实态方向相反。本格与 D13-29 三账是两条链不合并。

## 2. 六向台账

### 2.1 输入面
- 成交回报事件面（实测行数极低）：gap_refs 登记表 c1_market.execution_report
  "消费方在等未产表，环节面见 gap 节点 D13-G02"（G02 在 B 段，不在本段）。
- 入边：D13-24（模拟盘保活与成交回路）→ D13-27（map edges）。
- 判定证据：map 节点 D13-27 evidence"簿 06 硬实查⑤：两条链拆开——事件入口腿零调用、定周期腿真跑"。

### 2.2 输出面
- 下游：边 D13-27→D13-28（结算管线）、D13-27→D13-G02。
- consumers=count:11（code=9：src/zephyr/ex_core/eod_reconciliation.py:4、
  src/zephyr/ex_core/position_reconciler.py:1、src/zephyr/ex_core/risk_layer_orchestrator.py:4、
  src/zephyr/orchestrator/execution/reconciliation_loop.py:27）。
- 事件入口腿自身产物：无独立产物表面（产物归上游槽节点计数）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-27（wiring=partial，red_reason=unwired）。
- 排班注释：src/zephyr/data/config/schedule.yaml:248-254——"盘中持仓对账走 position 事件入口
  （R-015）……execution_report 的事件扇出（PositionReconciler.handle_execution_report）属 z-land
  实现面"——注释自辩与实态（事件腿零调用）方向相反=文档滞后实证。
- 簿 06：docs/_working/map_build/fig13_daycycle/06_盘后结算与三账.md。

### 2.4 代码模块
- module_id=MOD-EX-056；module_ref=src/zephyr/ex_core/position_reconciler.py（实存）。
- 关联面：src/zephyr/ex_core/eod_reconciliation.py、
  src/zephyr/orchestrator/execution/reconciliation_loop.py:27（consumers 实存命中）。

### 2.5 门禁约束
- 宪法 §9.3"reconciler 必须事件触发，禁 cron/Timer/sleep-loop"约束的是自愈环；本槽=定时事实核对
  （schedule.yaml:251 注释引 R-015 划界）——但真跑腿恰是"进程内定时器"，与注释自证的事件入口相反，
  属门禁语义张力点（图已记账，判归实现面）。
- gap_refs：benchmark:A7-no_drift_evidence 缺位（matched 零留痕）。

### 2.6 自动化触发
- slot_source=event，无槽；cadence declared="无槽：position 事件驱动"；observed="定周期腿每若干
  分钟；事件入口腿 0 次"；trigger_facts metric=none（事件触发段无独立产物表面）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | fail | 事件入口腿零调用（entry_leg_unwired=true）；execution_report 事件面行数极低且表未产（D13-G02 侧） |
| 输出面 | warn | 定周期腿有产物与 11 条 consumers；事件入口腿无产物面 |
| SSOT 真源 | warn | 真源在册但排班注释自辩与实态方向相反（文档滞后已在图记账） |
| 代码模块 | pass | position_reconciler.py/eod_reconciliation.py/reconciliation_loop.py 实存 |
| 门禁约束 | warn | 宪法 §9.3 与"定时事实核对"的划界靠注释自证；benchmark A7 no_drift 留痕缺位 |
| 自动化触发 | warn | 事件腿 0 次=触发面空转；真触发在进程内定时器（无独立计数面） |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：本格自身 wiring=partial（不在 6 no_caller/5 hollow 主清单）；
  其输入面断链与 B 段 gap 节点 D13-G02（execution_report 桥面空转）同根——修复在 B 段与图 12。
- 建议：要么把事件入口腿接真（execution_report 事件扇出落地，牵 D13-G02 表 producers），
  要么删事件腿声明、把注释改为"进程内定周期腿"如实陈述——当前"注释说事件、实跑定时"是
  假绿温床（图 laws 第 4 条判定纪律适用）。
