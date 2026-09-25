---
ttl: task_bound
title: RSK-4 MINE
doc_type: log
---

# RSK-4 35 号回撤协议族（现役闭环 + 设计件并行）— 深挖簿

> 车道 L08 风控 · 子块 4 · 班次 st-qmine-20260925 · 只读挖掘。
> 起点真源=`../SKEL.md` §2 RSK-4（其⑥遗留"谁在真实驱动 35 号家族待接线级实查"）。**本簿首项产出=对该问的实测回答**。

## ① 职责一句话

用"净值/回撤序列 → 回撤分级 → 仓位上限 → 必要时单一仲裁点强清"的现役闭环守住账户生存线，并让 35 号协议的六件辅助件（看门狗/券商端止损/连亏/强制休息/破产底线/会话持久化）在同一真源下各司其职。

## ② 现状实测（生产触发面判定：**核心闭环已接电（paper 实装配 + 每轮调仓驱动）；六件家族中仅 1 件被生产消费，其余 5 件覆盖未接电**）

**真实驱动面（回答骨架遗留问）**：
- 唯一生产装配点=`scripts/start_paper_session.py` → 构造 `RiskLayerOrchestrator` 并作为 `risk_layer=` 注入 `TradingSession`；由 `tests/scripts/test_start_paper_session.py:153,174`（`assert isinstance(session._risk_layer, sps.RiskLayerOrchestrator)`）双向锁死。
- 运行期驱动=`ex_core/trading_session.py:556-561 _do_rebalance` 起手闸门（`if self._risk_layer is not None and not self._risk_layer.is_trading_allowed: 整批拒下`）+ 每轮 `evaluate_intraday`；`risk_layer_orchestrator.py:458-460` 的 `RiskLayerOrchestrator(drawdown_controller=…, drawdown_tracker=…)` 是**头注用法示例**（不是装配点）。
- **家族头注统一声称的"RiskOrchestrator §6.5 接线位"从未落地**（`drawdown_state_machine.py:6` 自述"原声称 RiskOrchestrator §6.5 接线位从未落地"），真接线位=上面两处。→ 六件头注的"接线位"表述是**过期承诺**，与现役闭环并不矛盾（现役闭环走 tracker/controller，不靠 §6.5），矛盾仅在于"读者会以为家族六件已在产"。

**六件家族逐件接电判定（本层高价值，SKEL 只给"全 production + 头注声称 §6.5"）**：

| 家族件 | 模块 | 生产消费点（实测） | 判定 |
|---|---|---|---|
| 破产底线 static 腿 | `risk/core/drawdown_bankruptcy_floor.py` | **有**：`ex_core/risk_layer_orchestrator.py:164-168` 直接 `import check_bankruptcy_floor`，`:483` 注入 `bankruptcy_floor_initial_capital=float(initial_cash)`，`:76-85` 判定 → `bankruptcy_floor_breached=True → position_cap 0.0 + 禁新开仓（最严口径）`（`:321,330,340` snapshot 字段与合成）；另 `scripts/backtest/crisis_drill_monthly.py:72-74,224` 月度危机演练复用同函数（口径 0.85×初始、严格小于） | **已接电（实码+生产/演练事件链双证）** |
| 独立看门狗 | `risk/core/drawdown_watchdog.py`（`WatchdogVerdict, poll_once`） | 仅 `risk/core/__init__.py:19-23` re-export + `config/governance_operations_map.yaml:58,2099-2100` 运维登记 + 自家测试；`src/`、`scripts/` 内**无任何调用者**（同名的 `data/redundant_source/poll_once`、`tick_subscriber._poll_once` 是他件自有方法，非本件） | **覆盖未接电**（骨架"外部调度器驱动（设计）"→ 实测外部调度器不存在） |
| 券商端 stop 同步挂 | `risk/core/drawdown_broker_side_stop.py` | 自家测试 + `error_code_registry.yaml:2876-2877` 登记；无 src 消费 | **覆盖未接电** |
| 连亏 cap_multiplier | `risk/core/drawdown_consecutive_loss.py` | 自家测试 + `echo-guard.yml:50-58` stable_key 登记；**未发现 `cap_multiplier` 在 `position_sizing_engine` 的消费点**（本层 grep head 40 截断，标待复证 L08-C29） | **覆盖未接电（待复证）** |
| 强制休息 | `risk/core/drawdown_forced_rest.py` | 自家测试；无 src 消费 | **覆盖未接电** |
| 盘前/盘后会话持久化 | `risk/core/drawdown_session_persistence.py` | **它是 MOD-RK-049 的唯一实例化者**，而其两入口 `premarket_initialization` / `postmarket_persist` 被 `tests/risk/test_risk_signal_consumer_wiring.py:172-173` 断言零调用者；`echo-guard.yml:50,54,58` 三处 stable_key 锁其 load/save 签名 | **覆盖未接电（并被诚实锁上锁）** |

**现役闭环三件（tracker/controller/capital_curve）实测**：
- `risk/core/drawdown_tracker.py:203`、`position/core/drawdown_controller.py:334`、`position/core/capital_curve_manager.py:193` 的实例化行**均属 docstring 用法示例**；真实例化点=`risk_layer_orchestrator.py:104`（I2 注入声明）+ start_paper_session 装配（同上）。
- `capital_curve_manager`（MOD-POS-007）被 `position/core/strategy_book.py:4` 与 `position/core/position_sizing_engine.py:4` 以 DEPENDENCIES 声明消费（sizing 链在产）。
- 前端旁路（新发现，见 ⑥）：`frontend/services/dashboard_feeds.py:452-484 query_drawdown_throttle` **另起一次判定**。

## ③ 六向台账

| 向 | 台账 |
|---|---|
| 上游 | 净值序列（`evaluate_intraday` 每轮喂 NAV，`tests/risk/test_var_calibration_handoff.py:10` 描述"会话进程→evaluate_intraday 健康轮→save_premarket_baseline"）；券商实时持仓（清算口径，orchestrator 唯一发单点以券商为准）；初始本金注入 `bankruptcy_floor_initial_capital`（**未注入即大声告警且不判定**，`:83`）；36 号 §3.18 阶段 6 产端日终 `var_backtest_report_YYYY-MM-DD` 经 state_store 回流盘前（`:108`，`daily_auditor.py:5`/`backtest_store.py:6` 双端消费声明） |
| 下游 | `RiskLayerSnapshot`（`:120,290,321`：position_cap / allow_new_position / degraded / systemic_level / rollback_state / var_model_status / fhs_active / bankruptcy_floor_breached）→ `trading_session` 拒单与目标权重缩放；`_engage_kill_switch`（`:114` A1 单一仲裁点）→ `stop_loss.trigger_kill_switch` + `execute_kill_switch_liquidation`（15 笔/秒 + event_id 幂等 + LIQUIDATING 锁）；`position_sizing_engine`（连亏/半 Kelly）；`governance/lifecycle_governance/rollback_state_machine.py:5`（CONSUMERS 含本件，回滚态进 snapshot）；`risk/risk_signal_sequencer.py:22`（与本件分工声明：本件为执行侧真源） |
| 算法/机制 | 回撤分级 → position_cap 阶梯；破产底线严格小于判定；REBUILD 静态映射 VaR3%/CVaR5%（36 号 §3.10）；五态降级机（53 号 §3.8，`LiquidityRecoveryState`/`check_recovery`，见 `37_liquidity_crisis_protocol.md:236`）；FHS（`tests/risk/test_fhs_orchestration_wiring.py`）与黑天鹅模式库 MOD-RK-31（`adaptive_risk_coordinator.py:5` CONSUMERS=本件，"设计契约"字样=未接电）；`var_breach_state_machine.py:6` CONSUMERS=DrawdownController 乘性折扣 + "RiskLayerOrchestrator(编排注入)"（该条被 `test_risk_signal_consumer_wiring.py:57` 列为**待核实的虚假消费声称**之一） |
| 后端 | orchestrator 单实例挂 4 件既有组件（controller/tracker/VaR/TailRisk）+ state_store（JsonStateStore，`start_paper_session.py:494`）；`is_trading_allowed` 为会话级硬闸；恢复未完成 → 整批拒下（`trading_session.py:558-561`）；清算限频 15 笔/秒分片 + 幂等键；挂单撤销经 `open_orders_provider` 注入（`start_paper_session.py:454,470`） |
| 前端 | `frontend/services/dashboard_feeds.py:442-484`（BFE-26 回撤油门刹车）：`_throttle_gear(position_cap)` 四档 full/half/brake/stop + 中文档名 `_GEAR_ZH`；输出 `risk_level/position_cap/reduce_ratio/actions/strategy_stops/kill_switch_advised/recovery_factor` —— **注意它是"advised"而非执行真源**（见 ④ L08-C28） |
| 数据字段 | `RiskLayerSnapshot` 八字段（上表）；`state_store` 命名空间：`var_backtest_report_YYYY-MM-DD`（36 号日终产端）、premarket baseline、`var_calibration_applied` 消费指针（幂等）；**缺项**：回撤分级/清算流转无物化表（L08-C06）、家族六件产物无统一落库、`bankruptcy_floor_initial_capital` 未注入时**只告警不落态**（复盘看不出"那天判定缺席"） |

## ④ 缺口清单（本层新增；SKEL 已立项引用不重复）

| # | 缺口 | 证据 | 判级 |
|---|---|---|---|
| L08-C28 | **前端二次判定与执行侧不同源**：`query_drawdown_throttle` 每次 `DrawdownController()` 新建实例、`black_swan=BlackSwanSignal()` 硬编码默认、峰值/回撤由请求方自带 → 展示的 position_cap 系统性偏乐观（黑天鹅恒无、策略连亏仅传 drawdown_pct），且新实例不含任何跨日状态。Owner 在面板上看到的档位可能严于/松于真实执行档位而不自知 | `dashboard_feeds.py:462-476` | **P1**（终局全貌=AI 自制一切可自动化者，展示层必须读 `RiskLayerSnapshot` 真源而非重算；修法=读 snapshot 单点，零新组件） |
| L08-C30 | 家族五件"production 成熟度 + 零消费者"的**身份虚高**：`MATURITY=production` 与实测覆盖未接电冲突（watchdog/broker_side_stop/consecutive_loss/forced_rest/session_persistence）→ 建议按 §2 判据三态重登为"实码在盘·无触发面"，并纳入 L08-C03 同一次内收窗口 | 本簿 ② 表 | P1（治理面；禁以"有代码即 production"记账） |
| L08-C31 | watchdog 无调度者但 `governance_operations_map.yaml:58,2099-2100` 已把它登记为运维件（运维按图找不到进程）；同时其"独立进程看门狗"设计若接电须遵守运维红线 3（事件触发，禁 cron/Timer） | 同上 | P2 |
| L08-C29 | consecutive_loss → sizing 的 `cap_multiplier` 消费链复证（本层 grep 截断，未证实亦未证伪） | — | 挖掘债（下轮补枪） |
| 引用不重复 | SKEL L08-C03（MOD-RK-049 三选一，本簿给出家族侧连带事实：**现役闭环真源=orchestrator+tracker+controller，设计件的五件并行不接电不影响现役生存线**）、L08-C06（流转全史物化表）、L08-C01/TRD-A13（仲裁序，本簿补充：orchestrator :74-85 的"最严口径合成"**已是既成立法先例**，与 `arbitration_order_v1_draft.md:26` 引用一致） | — | 已在账 |

## ⑤ 自审闸三态裁定

**MINING**。骨架 §3 的 5 项 MINING 债：本簿清空 2 项（"RiskOrchestrator §6.5 真实装配面"→ 实测不存在，真位=start_paper_session + evaluate_intraday；"六件家族模块正文"→ 接电判定表已给，正文逐行未读）。仍欠：
1. 35 号 memo（`docs/_working/archive/2026-09/design_memos/35_drawdown_protocol_impl.md`，1664+ 行）§3.5 触发表 / §3.13 盘中循环 / §3.19-§3.20 / §4.10 / §6.6 逐节对表；
2. 53 号五态降级机 memo；36 号 memo §3.10/§3.15；
3. `risk_layer_orchestrator.py` 正文（1900+ 行，本簿只读头注 INVARIANTS + :76-85/:104-120/:164-168/:290-340/:458-483 关键点）：`_engage_kill_switch` 全实现、清算幂等键与 LIQUIDATING 锁的 fail-closed 细节、`check_recovery` 阶梯；
4. `drawdown_controller.py` 正文（risk_level 阶梯与 position_cap/reduce_ratio/actions 的真实映射，L08-C28 需据此定"面板能否只读不算"）；
5. `tests/risk/test_bankruptcy_floor_wiring.py` + `test_fhs_orchestration_wiring.py` + `test_rollback_state_wiring.py` 三件的断言面（它们是本家族唯一"接线证明"，其覆盖口径决定本块能否升 SEALED）。
**不封矿**理由（纪律）：现役闭环是资金安全主链，"规模已够跑 paper"不是封矿理由；量尺=终局全貌（六件家族要么接电要么退役，不得长期停在"production 无消费者"）。

## ⑥ 挖矿日志

- Read `../SKEL.md` §2 RSK-4 → 取"谁在真实驱动"作为本块靶心。
- Grep src+scripts `drawdown_watchdog|broker_side_stop|consecutive_loss|forced_rest|bankruptcy_floor|session_persistence` → 得家族六件消费面全表（含 `risk/core/__init__.py` re-export 假信号、echo-guard 三处 stable_key、crisis_drill_monthly 复用）。
- Grep src `DrawdownTracker(|DrawdownController(|CapitalCurveManager(|risk_layer_orchestrator` → 定位真实例化只在 docstring 与 orchestrator 注入声明；顺带命中 `dashboard_feeds.py:462` → 追出 L08-C28。
- Read `dashboard_feeds.py:425-484` → 确认前端每次新建 controller + 黑天鹅默认值 → 乐观偏置判定成立。
- Grep 全仓 `check_bankruptcy_floor|RiskLayerOrchestrator|risk_layer=` → **拿到生产装配铁证**（`test_start_paper_session.py:153,174` + orchestrator `:164-168/:483`）。
- Grep src+scripts `poll_once|bankruptcy|forced_rest|consecutive_loss|cap_multiplier` → 排除同名他件假信号（tick_subscriber/sina_tencent_provider 的 poll_once），确认 watchdog 零驱动。
- 前序块顺带取证（跨块复用，未额外调用）：`drawdown_state_machine.py:6` 家族头注矛盾原文、`test_risk_signal_consumer_wiring.py:57` 把 "RiskLayerOrchestrator(编排注入)" 列为待核实虚假消费。
- 纪律：只读；未跑任何测试/脚本；未起进程；未写 `.runtime` 根；无 git 写。
- 外部对表：未做（留统一轮；候选=Grossman-Zhou 1993 / Yang-Zhang 2012 / Choi 2021，`../SKEL.md` §5 已登记，本块 position_cap 阶梯与 DD 上限最优策略对表）。
