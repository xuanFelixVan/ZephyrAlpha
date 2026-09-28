---
ttl: task_bound
title: "F63 仓位管理与对账——持仓状态机/对账/NAV 记录/仓位漂移"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F63 · 仓位管理与对账（总册状态 built/P0；本卷复核=built 维持（sim 面绿/实盘对照面黄），reconciler 双件同名在案）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | 柜台镜像 PositionSnapshot（broker.get_positions）；Fill 流（AsyncFillDispatcher→tracker 入账）；F57 结算对账输出 |
| 下游消费 | F42 P1 持仓体检（TDM-P-P1）；F60 NAV（live_nav_recorder 为 DrawdownTracker 基线真源）；TradingSession._compute_order_deltas（trading_session.py:636/714，M7-03 实锚） |
| 自动化触发 | eod_reconciliation 15:40 槽（M5 schedule.yaml，audit 环节⑦）；盘中=事件链 observe+执行腿双触发 |
| 真源与注册表 | 持仓双真源并存：柜台实持（账实核对基准）vs 本地 tracker（SQLite+Redis，position_tracker/tracker.py:34 T+1 锁定/FIFO-LIFO）；蓝图族=docs/03_modules/_domain_position/ |
| 门禁与质量尺 | position_state_machine：OBSERVING 禁新买/CLOSED 冷却禁重建/灰度单调（MOD-POS-002 INVARIANTS）；live_nav_recorder：读不到券商实时净值=拒装配 exit 1 禁猜基线（paper INVARIANTS） |
| 当前运行状态 | **绿（sim 面）/黄（实盘对照面）**：sim 钱包 45 户 fresh=1（09-23 起，M7-03 实测）；账实核对=position_reconciler 由 eod 槽驱动；实盘语境未开（S-1 锁着）不判 |

## 二、子模块三级枚举（position 域本日实扫：根+core 29 件+api/models/services/infrastructure）

- **状态机与核算（core/ 29 件实测）**：position_state_machine.py（572 行五态转换）、position_sizing_engine.py、pyramiding_rules.py、rebalance_engine.py、budget_change_handler.py、drawdown_controller.py（paper 会话必装配）、position_drift_monitor.py（**仓位漂移**）、position_limit_enforcer.py、cash_manager.py、core_satellite_allocator.py、single_name_cap_caliber.py、t1_sellable.py、defensive_asset_whitelist.py（327 行，F60 消费方）、firm_risk_aggregator.py、correlation_regime_monitor.py 等
- **对账与 NAV**：position_reconciler.py（**居 position/ 根**）+ex_core/position_reconciler.py（**同名双件**，M7-03 B4）+ex_core/eod_reconciliation.py（三账核对 :24，15:40 槽）；live_nav_recorder.py（253 行，根级）
- **持仓账本**：ex_core/position_tracker/tracker.py（SQLite/Redis/T+1/FIFO-LIFO 历史保险③）

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| 状态机/ sizing/漂移 | built（production 群） | core/ 29 件实扫+M7-03 门禁双源 |
| 账实对账 | 已接线（eod 槽） | 15:40 槽驱动；**同名双件无导航声明**（B4 在案未闭） |
| NAV 记录 | built（paper 必装配） | 253 行+fail-closed INVARIANTS |
| 买入腿实弹验证 | **缺证** | M7-03 B1：卖出腿 09-23 实弹过、买腿仓内未见（FIFO 批次链未被实弹验证） |

### 骨架勘误
- **总册 F63 锚点"position/core/position_reconciler.py"路径漂移**：实件在 position/ 根（position_reconciler.py），core/ 下无此件（本日 find 实证）；且同名双件（ex_core/ 各一）总册未标注。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 买腿零实弹记录 | sim 桥 smoke 补成交型买腿+tracker 批次核对（1 天，M7 施工） | P1 |
| 2 | position_reconciler 同名双件收敛 | 合并或改名+导航注记（0.5 天，内收判据"同域重复簇→收敛唯一"） | P2 |
| 3 | 卖出决策族无盘中触发面 | fusion/arbitrator/planner 挂 60min bar 事件链或显式降级人工（0.5-1 天+裁定） | P1 |
| 4 | P1 仓位参数未 confirmed（live_admission 七红之一） | Owner 门位 | P1（Owner） |
| 5 | tracker Redis 依赖单机形态必要性未声明 | 待实查不臆断（M7-03 B5） | P2 |

## 五、自审闸三态
**挖干可施工**（29 件 core 实扫+对账三件+NAV 门禁复核；总册 built 态维持，勘误 1 条锚点路径）。

## 六、复跑命令
```bash
wc -l src/zephyr/position/core/position_state_machine.py src/zephyr/position/live_nav_recorder.py   # 572/253
ls src/zephyr/position/*.py src/zephyr/position/core/*.py | grep -c reconcile   # 双件证据
find src/zephyr/position -name "position_reconciler.py"    # 根级非 core/
ls src/zephyr/position/core/*.py | grep -v __init__ | wc -l   # 28 模块（+__init__=29）
```
