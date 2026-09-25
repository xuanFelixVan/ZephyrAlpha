---
ttl: task_bound
---

# M7-03 · 仓位与卖出（T6+T7 合册）

> 挖矿班 st-commitspeed-tbl-20260924 ｜ 2026-09-25 ｜ 只读挖矿
> 合册理由（Owner 令"能合并的合并"）：position 与 sell_decision 在执行链是同一条收支轴——仓位状态机产"可卖什么"，卖出族产"何时卖多少"，中间经 sell_position_link 直接耦合，分册会互相引用过半。

## 一、环节定义与边界
仓位=持仓跟踪/仓位计算/盈亏分析/账实核对（T6）；卖出=卖出信号融合/冲突仲裁/执行计划（T7）。上游=RiskValidationBridge/柜台镜像/信号族（供料）；下游=TradingSession delta 订单/桥卖出腿（消费）。

## 二、六向台账
| 向 | 内容与实证 |
|---|---|
| 上游输入 | 柜台镜像 PositionSnapshot（broker.get_positions）；Fill 流（AsyncFillDispatcher→tracker 入账）；策略权重/预算变更（budget_change_handler）；盈亏序列（capital_curve_manager） |
| 下游消费 | TradingSession._compute_order_deltas→_make_sell_all_order（`trading_session.py:636/714`）；sell_execution_planner→订单参数；eod_reconciliation 三账核对（40 号 gap 10）；前端 position_monitor（只读构造已改 read_only，交付报告 §3） |
| 自动化触发 | eod_reconciliation 15:40 槽（schedule.yaml，audit 环节⑦）；盘中=事件链 observe+执行腿（双触发）；卖出无独立 runner（决策由 dloop/事件链供信号，执行随交易会话） |
| 真源与注册表 | 持仓双真源并存：柜台实持（桥镜像=账实核对基准）vs 本地 tracker（SQLite+Redis，`position_tracker/tracker.py:34` T+1 锁定/FIFO-LIFO）；蓝图族=docs/03_modules/_domain_position/、_domain_sell_decision/ |
| 门禁与质量尺 | position_state_machine：OBSERVING 禁新买/CLOSED 冷却禁重建/灰度单调（MOD-POS-002 INVARIANTS）；sell_execution_planner：强制清仓绕融合/止损盘中限价/止盈尾盘 14:50-14:57/跌停排队次日/T+1 不可卖（MOD-SELL-019 INVARIANTS）；position_limit_enforcer/cash_manager 硬约束 |
| 当前运行状态 | **绿（sim 面）/黄（实盘对照面）**：sim 钱包 45 户全绿 fresh=1（09-23 起）；账实核对=position_reconciler 在册由 eod 槽驱动；实盘语境未开（S-1 锁着），不判 |

## 三、子模块清单（position 38 件+sell_decision 28 件，列核心 16 件；全量=两域 blueprint 目录）
| 子模块 | 是什么 | 入口 file:line | 状态 |
|---|---|---|---|
| position_tracker.tracker | 本地持仓账本：SQLite 持久化/Redis 实时/T+1 锁定/**FIFO-LIFO**（历史保险③）/unrealized_pnl | position_tracker/tracker.py:34 | production |
| position_reconciler | 账实核对（本地 vs 券商） | ex_core/position_reconciler.py+position/position_reconciler.py 双件（同名族，见堵点 B4） | 在 |
| eod_reconciliation | 盘后全量对账（PositionReconciler 扩展三账） | ex_core/eod_reconciliation.py:24 | 在，15:40 槽驱动 |
| position_state_machine | OBSERVING/HOLDING…五态转换合法性 | position/core/position_state_machine.py:3 | production |
| position_sizing_engine | 仓位计算 | position/core/position_sizing_engine.py | production |
| budget_change_handler | 预算变更→仓位联动 | position/core/budget_change_handler.py | production |
| drawdown_controller | 仓位侧回撤控制 | position/core/drawdown_controller.py | production（paper 会话必装配） |
| sell_position_link | 卖出↔仓位联动阈值（profit_loosen/loss_tighten，FULL_STOP>REDUCE_50>OBSERVE>NORMAL） | position/core/sell_position_link.py:3 | production |
| sell_signal_fusion_engine | 多信号加权融合（综合意愿∈[0,1]，多时框共振×1.5） | sell_decision/core/sell_signal_fusion_engine.py:3 | production |
| sell_conflict_arbitrator | 多卖出理由冲突仲裁 | sell_decision/core/sell_conflict_arbitrator.py | production |
| stop_hunting_protector | 止损打保护 | sell_decision/core/stop_hunting_protector.py | production |
| sell_execution_planner | 卖出执行计划（时段/市价限价/跌停排队规则族） | sell_decision/core/sell_execution_planner.py:3 | production |
| live_nav_recorder | 实时净值记录（DrawdownTracker 基线真源=券商实时净值，读不到=拒装配 exit 1 禁猜基线） | position/live_nav_recorder.py | production（paper INVARIANTS） |
| cash_manager / position_limit_enforcer / core_satellite_allocator / rebalance_engine | 资金/限额/域配置/再平衡四件 | position/core/ | production（工程参数面归 P1 Owner confirmed 门，audit 七红 P1） |

## 四、堵点与病灶
| # | 现象/根因/修法/工作量/归属 |
|---|---|
| B1 | **买入腿零实弹记录**（audit 环节④同判）：卖出腿 09-23 实弹过（卖 510300 1100@4.604），成交买腿仓内未见——仓位侧的"买入入账→FIFO 批次→T+1 锁定"全链未被实弹验证过。修法=sim 桥 smoke 补成交型买腿+tracker 批次核对；1 天；M7 施工 |
| B2 | **卖出决策族无盘中触发面**：fusion/arbitrator/planner 三件 production 但无 runner 挂事件链或时钟（grep scripts/src/trading 零调度挂接）——现役卖出只走 delta rebalance 与 bridge-execute 防御行。修法=把 sell_signal_fusion 挂 60min bar 事件链（对齐五态归类），或显式降级人工+排班（TRD-A07 同口径）；0.5-1 天+裁定 |
| B3 | P1 仓位参数未 confirmed（live_admission 七红之一）：max_single 等工程参数以"提案可修"态在跑。Owner 门位 |
| B4 | **position_reconciler 同名双件**（ex_core/ 与 position/ 各一）：同名族无导航声明，消费方各找各的。修法=合并或改名+导航注记；0.5 天；可施工（内收判据同域重复簇→收敛唯一） |
| B5 | tracker 的 Redis 依赖在单机会话形态下是否必配未声明（paper 路径只见 JsonStateStore/SQLite 证据，Redis 面无装配点实证）——待实查，不臆断 |

## 五、提速与合并机会
- position 与 ex_core 的对账三件（position_reconciler×2+eod_reconciliation）收敛为 position/ 单域出口（同真源可派生→必并）。
- sell_decision 六件→sell_execution_planner 一出口：fusion/arbitrator 对外只见 planner（域内已低耦合，对外收口即可）。

## 六、自审闸三态
**挖干可施工**（仓位/卖出子模块与门禁两源验证齐；B1/B2 施工项明确，B5 待实查不阻断）。

## 七、复核命令（10 分钟）
```bash
grep -n "FIFO" src/zephyr/ex_core/position_tracker/tracker.py            # 历史保险③
sed -n "3,6p" src/zephyr/position/core/sell_position_link.py             # 联动阈值族
sed -n "/^\"\"\"/,/\"\"\"/p" src/zephyr/sell_decision/core/sell_execution_planner.py | head -12  # 卖出纪律
ls src/zephyr/position/core/ src/zephyr/sell_decision/core/ | wc -l      # 子模块计数对账
grep -rn "sell_signal_fusion" scripts src/zephyr/trading --include="*.py" | wc -l  # B2 零触发面
```
