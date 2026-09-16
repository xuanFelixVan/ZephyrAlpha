---
ttl: task_bound
title: T1-β 节点挖矿：Kill Switch 与熔断/回撤阶梯全链路
session: st-qoder-t1a-20260915
date: 2026-09-17
parent: S11_assembled_backtest
lane: K
---

# 节点挖矿：Kill Switch 与熔断/回撤阶梯（父环节 S11_assembled_backtest）

> 挖矿对象=应急停/熔断/回撤阶梯这条"保命链"，不看收益只看断没断。方法=逐文件读函数体 +
> AST 扫 call site（不信 grep 命中），探针脚本 `.runtime/tmp/mine_ks_qz73/`。
> 结论先说：**计算核是干净的（阈值真源 fail-closed、边界判定正确、崩溃可恢复的持久化确实存在），
> 险情全在"发令面"——三层拒单闸门里只有一层真被生产代码驱动，而熔断落地时没有任何出声出口。**

## 1 现状盘点（逐条带 file:line 锚点）

### 1.1 入口地图：同名不同命的四套东西

| 组件 | 位置 | 到底是什么 | 谁在真实调用 |
|------|------|-----------|-------------|
| KillSwitch（AI 行为熔断） | `src/zephyr/security/access_control/kill_switch.py:138` | 9 个行为触发器（rapid_file_deletion 等），**纯进程内存态**（:145-153，注释自述"进程崩溃即归零"，:32-33） | 生产唯一消费者=`strategy_pipeline/pipeline_events.py:139-152` 探针；启动钩子 `trading/boot_hooks.py:305-318` 只读不断 |
| KillSwitch（交易五级表） | `src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py:61-112` | 5 级 POSITION_LIMIT/DAILY_LOSS/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT + 散文 trigger_condition | **只有 `trigger/reset/get_switch/active_switches` 被用**（编排器适配器 :166-188）；`evaluate()`（:139-152）全仓零 call site |
| KillSwitchOrchestrator（两级编排） | `src/zephyr/autonomy_core/kill_switch_orchestrator.py:259` | 包装 5 套开关做路由/传播/一致性 | 仅 `boot_hooks.py:591-604` 取单例注册（不发令）；`trip()/route_incident()` 生产零 call site（AST 实测） |
| RiskLayerOrchestrator（真身） | `src/zephyr/ex_core/risk_layer_orchestrator.py:205` | 盘中回撤/VaR/系统性/五态降级 → `_engage_kill_switch` 单一仲裁点 | **这条才是活的**：`ex_core/trading_session.py:535/580` 每轮调仓驱动 |

回撤阶梯本体：`risk/core/drawdown_tracker.py`（MOD-RK-011，阈值 THD-DRAWDOWN-001/002/003）+
`position/core/drawdown_controller.py`（MOD-POS-008，仓位上限联动）。并行未启用件两件，头块已自证：
`risk/core/drawdown_state_machine.py:6`、`risk/core/var_intraday_recalc.py:6`（均"无现役端到端消费方"，
本挖矿复核通过，不重复立项）。

### 1.2 真实触发链端到端（七跳）

| 跳 | 动作 | 锚点 | 触发方式 |
|----|------|------|---------|
| ①装配 | `DefaultRiskValidator(state_store=JsonStateStore)` + `DrawdownTracker(nav_baseline)` + 编排器组合 | `scripts/start_paper_session.py:495/459/521-527` | 进程启动（人工/服务拉起） |
| ②恢复闸门 | `recover_from_broker()` 成功才置 `_recovery_completed=True`，失败 Fail-Closed 禁下单 | `risk_layer_orchestrator.py:644/685-689` | 会话 start 事件驱动 |
| ③评估 | `_do_rebalance → _evaluate_risk_layer → evaluate_intraday(nav) → tracker.update` | `trading_session.py:535/580`；`risk_layer_orchestrator.py:745` | **只在调仓那一刻**（非独立盘中风险循环，见 KS-1） |
| ④判定 | `_classify`：\|dd\|≥15%→EMERGENCY（实测 -15.00%=EMERGENCY、-14.99%=CRITICAL，边界含等号）；另有尾部 EMERGENCY :823 / BS-007 建议 :825 / 系统性 LEVEL_3 :1063 / 五态 UNWINDING :1220 / 破产底线 :900 同口汇入 | `drawdown_tracker.py:337-347` | 事件（级别变化才发射，:310-327 去抖） |
| ⑤仲裁 | `_on_drawdown_alerted → _engage_kill_switch`：锁内置闩 → 状态层 `trigger_kill_switch()` → 事件层落盘 → 清算 | `risk_layer_orchestrator.py:638/1690-1775` | 同步同线程 |
| ⑥执行 | `execute_kill_switch_liquidation`（以券商实时持仓为准，15 笔/秒限频）+ 挂单撤销（`open_orders_provider` 注入见 `start_paper_session.py:454/470`） | `risk/stop_loss.py:282`；`risk_layer_orchestrator.py:1758-1768` | 同步 |
| ⑦清除 | 人工复位**只有 validator 侧一条 API**：`reset_kill_switch(confirmation)`，持久化失败则保持熔断 | `default_risk_validator.py:353-401` | 人工only（无自动降级路径，符合保守方向） |

### 1.3 消费核实：熔断态确实拒单——但要分三层看（三层只有一层被全装配）

| 层 | 判据 | 装配现实 | 判定方向 |
|----|------|---------|---------|
| L0 整批闸门 | `is_trading_allowed = _recovery_completed and not _kill_switch_engaged`（`trading_session.py:522/537`） | 需注入 `risk_layer=`，`start_paper_session.py:526` 有 | 拒整批，正确 |
| L1 逐单风控 | `validate_order` 在 `_kill_switch_active` 时追加 HALT（`default_risk_validator.py:205-213`）→ `trading_session.py:875-888` 阻断 | `risk_validator=` 注入（`start_paper_session.py:558`） | **买卖双向拒**（不看 target_weight 符号）：熔断连平仓一起拒——与五级表 `POSITION_LIMIT="REDUCE_ONLY 允许平仓"`（`trading_kill_switch.py:74-78`）散文相矛盾，而该 action 无人实现 |
| L2 执行前四级闸门 | 闸门 1 探针：`bool(probe())` 异常→按已熔断拒（`pre_execution_checker.py:183-203`） | `start_paper_session.py:565` 显式注入 `lambda: validator.kill_switch_active` | **真·Fail-Closed，探针异常也拒**（本节点最干净的一层） |
| L3 看门狗（ghost 兜底） | `drawdown_watchdog.poll_once`：kill_switch CLOSED 且有持仓→全量强平 | **生产零 call site**（全仓 `poll_once` 命中仅 `risk/core/__init__.py:23` re-export），但其 CONSUMERS 自称"独立看门狗进程(外部调度器驱动)"（`drawdown_watchdog.py:6`） | 未接线=不存在（见 KS-2） |

探针缺省反查路径存在但弱：`trading_session.py:457-470` 从注入的 validator 摸
`kill_switch_active`，摸不到就返回 None → 闸门 1 打 DEBUG 后放行（`pre_execution_checker.py:180-181`
`KILL_SWITCH_PROBE_UNWIRED ... 按未激活继续`）=**探针未接线时 fail-open**，靠装配层兜住。

### 1.4 fail-open / fail-closed 逐路径判定

| 失效场景 | 行为 | 方向 |
|---------|------|------|
| 注册表缺文件/缺条目/value 非字符串 | `AlertThresholdConfigError` 直 raise，import 期即炸（`threshold_loader.py:126-145`；`drawdown_tracker.py:118` 模块级调用） | **fail-closed，合格** |
| nav 传入 NaN/±Inf | tracker 与编排器双点非有限门禁 raise（`drawdown_tracker.py:270-273`、`risk_layer_orchestrator.py:730-731`） | fail-closed |
| 熔断探针抛异常 | 按已熔断拒单（`pre_execution_checker.py:184-195`） | fail-closed |
| `DrawdownController.evaluate` 抛异常 | 仅 `logger.exception`，本轮无 position_cap/无 BS-007 建议，**回撤链仍生效但"该不该 KillSwitch"的建议源消失**（`risk_layer_orchestrator.py:820`） | fail-open 偏乐观 |
| 回撤监听器（=熔断仲裁点）抛异常 | `tracker._emit` 全捕获仅 `logger.error`（`drawdown_tracker.py:349-354`）→ 见 KS-5，**"半口熔断"被静默吞掉** | **fail-open，硬伤** |
| 清算持仓查询/清算执行抛异常 | 熔断态保持、新单已禁、异常吞并（`risk_layer_orchestrator.py:1748-1750/1769-1771`），存量裸暴露无人补刀 | 状态 fail-closed、资金 fail-open |
| 持久化记录损坏 | `StateCorruptError` → 按已熔断处理（`default_risk_validator.py:158-166`） | fail-closed |
| 编排器 `is_tripped()` 查询异常 | 返回 **False** 并告警（`kill_switch_orchestrator.py:491-493`，自述"查询面 fail-open"） | fail-open（但该查询面无生产消费者） |

## 2 编号发现（按"现网每天在错"排序）

| # | 级别 | 发现 | 证据 | 一行治法 | 爆炸半径 |
|---|------|------|------|---------|---------|
| KS-1 | **P0** | **回撤阶梯的评估频率=调仓频率，没有独立盘中风险循环**。`evaluate_intraday` 唯一驱动点是 `TradingSession._do_rebalance`；而 `start_paper_session` 的 INVARIANTS 明文"默认纯会话保活不自动 rebalance（--strategy 缺省=安全默认）"（:8/:52/:480），且常驻 Timer 调仓 `--interval` 已于 2026-09-05 删除（:61-62/:484）。于是保活模式下净值一路跌穿 15% 也不会有一次评估；`_reconcile_tick` 那圈 Timer 只做持仓对账、不评估风险（:1800-1805/:1822-1827） | `trading_session.py:535`；`start_paper_session.py:8,61-62,480`；`risk_layer_orchestrator.py:1800-1805` | 把 `evaluate_intraday` 挂到已在圈的事件源（成交回调/行情 tick 或 `ex_core.rebalance.requested` 之外的独立事件），禁 Timer | 阶梯本体：整条 5/10/15% 保护在未调仓时=纸面 |
| KS-2 | **P0** | **熔断落地全链无 Owner 出声出口**。`_engage_kill_switch` 只 `logger.critical`+落盘（:1723）；`stop_loss.trigger_kill_switch`/`execute_kill_switch_liquidation` 内 grep 零 `publish/Alerter/notify`（`stop_loss.py:98/282`）。唯一 EventBus 订阅者 `notifier.py:190` 听 `kill_switch_triggered`，而全仓唯一发布者是 **rollback 域** `infrastructure/rollback/kill_switch.py:115-135`，其 `activate` 唯一调用者是编排器适配器 `kill_switch_orchestrator.py:213`，而编排器 `trip()/route_incident()` 生产零 call site → 订阅者活着、发布者永远不被触发 | 上述 5 处 + AST call-site 扫描（`route_incident`=0） | 在仲裁点 emit `kill_switch_triggered`（含 reason/event_id），或直接调 `Alerter().notify` | 交易熔断=最高危事件却零通知，Owner 只能靠事后翻日志 |
| KS-3 | **P1** | **发令面整块"产而不消"**：`KillSwitchOrchestrator`（MOD-AU-002）+ `KillSwitchResponseLayer`（MOD-AU-004 三级响应）在 src/scripts 内**零生产调用者**（`killswitch_response_levels.py:5` CONSUMERS 只登记 tests；实测除 tests 外无引用）。boot 只 `get_orchestrator()` 注册不发令（`boot_hooks.py:600-602`）。INVARIANTS 宣称的"系统级 TRIPPED→域级一致生效""level_3 交易级联动"没有任何一条生产路径能把它拉起来 | `kill_switch_orchestrator.py:355-472`；`boot_hooks.py:591-604` | 要么给 AI 越级/事故信号接上 `route_incident()`，要么把两级编排降为"文档设计件"并改头块，别留"已接线"错觉 | 自治域事故无全局刹车；同时误导后续施工者以为已闭环 |
| KS-4 | **P1** | **交易五级熔断表=纯散文阈值**：`trigger_condition` 是人写的字符串（"daily_pnl < -0.03 * aum"、"consecutive_rejections >= 5 OR price_deviation > 5%"、"latency > 1000ms OR fill_rate < 50%"、"broker_api_timeout > 10s OR heartbeat_miss >= 3"，`trading_kill_switch.py:83/91/99/107`），唯一能消费它的 `evaluate()` 零 call site，且 `cooldown_seconds/auto_reenable`（:78/86/94/102/110）无人读——`active_switches()` 唯一读者是编排器 `is_tripped`（:188），而该查询面无消费者。同族：日亏 3% 这条与 THD-DRAWDOWN 阶梯无任何换算关系，两套风险词汇并存 | 同上 + 实测 `active_switches()` 导入后即空表、无人置位 | 删表或逐条落判据+接 `evaluate`，二选一，不许"留着以后接" | 4 个资金/延迟阈值全不生效 |
| KS-5 | **P1** | **一次 IO 抖动=本进程清算永久不可重入**（吞异常导致"半口熔断"）。`_engage_kill_switch` 在 :1720-1721 先置 `_liquidation_started`/`_kill_switch_engaged`，随后**事件层 `trigger_kill_switch(...)`（:1733）未包 try**，state_store 写失败抛 `StateStoreError` 即向上抛 → 被 `tracker._emit` 的 blanket except 吞成一行 `logger.error`（`drawdown_tracker.py:353`）→ 第 3 步清算（:1760）根本没跑。此后任何新触发源都被 :1714-1719"重复仲裁跳过"挡死（闩永不复位，全类无 `_liquidation_started=False` 的第二处赋值，实测 grep 仅 :574/:1720）。状态层同样被吞：:1729-1730 捕获后"继续清算" | 精确到行 | 闩置位挪到清算真正发起之后（或失败即回滚闩并 CRITICAL 出声重试一次）；`_emit` 对"仲裁点监听器"例外——熔断类监听器异常必须升级为 CRITICAL+告警，不得静默 | 熔断"看起来在"、券商侧满仓裸奔，且不可自愈 |
| KS-6 | **P1** | **Timer 常驻对账违反宪法 §9 运维红线第 3 条，且与自家治本先例自相矛盾**：`threading.Timer` 自续排程（:575/:1811-1827，注释自述"每 5 分钟定时调度/默认300s"）由 `TradingSession.start()` 无条件启动（`trading_session.py:404`），`_reconcile_tick` 异常仅 log"下轮重试"（:1825）。同仓 `start_paper_session.py:61-62/:484` 已因"threading.Timer 周期调仓违反 trae_060 §3 禁时间触发"删除 `--interval`——同型问题一处改一处留 | :1815-1820 vs `start_paper_session.py:484`；AGENTS.md §9 第 3 条 | 改事件触发（成交/持仓变更/日切事件），或显式登记豁免裁定 | 静默停摆=对账冻结机制失效而无人知（未独立核实 config 默认秒数，仅注释自述） |
| KS-7 | **P1** | **阈值第二真源**：`DrawdownController` 的 soft/hard stop 与 VaR 三档全是码内字面量（`drawdown_controller.py:314-319` = 0.05/0.10/0.02/0.04/0.06/0.10），未进注册表；`alert_threshold_registry.yaml` 只有 THD-DRAWDOWN-001/002/003（:59/:78/:97，实测加载得 `{'warning':0.05,'critical':0.1,'emergency':0.15}`）。当前 5%/10% 数值**巧合对齐**，一旦 Owner 改注册表，tracker 阶梯动了、controller 的 soft/hard stop 不动 → 同一"阶梯"两套刻度 | 两处 file:line | 005/010 收进注册表同 ID 或新开 THD-POS007-*，走 `load_alert_thresholds` | 回撤仓位上限与告警级别背离（改阈值当日才暴露） |
| KS-8 | **P2** | **熔断闩无复位出口（编排器侧）**：`_kill_switch_engaged` 全类仅 :569 置 False、:1721 置 True，**无任何人工复位 API**；`is_trading_allowed`（:704）据此一票否决整批。validator 侧倒是有 `reset_kill_switch`（含双人确认语义 :353-401）。后果：复位流程必须"改记录+重启进程"两步，而重启会把高水位峰值一起清零（见 KS-9） | grep 实测 3 处赋值 | 编排器补 `disarm_kill_switch(approver)`，与 validator 复位原子化 | 恢复语义靠重启，易误操作 |
| KS-9 | **P2** | **峰值高水位不跨进程**：`DrawdownTracker` 无任何序列化 API（全文 :199-355 无 persist/load），peak 只活在内存；编排器也不持久化 peak。重启即以"券商实时净值"为新峰值（`start_paper_session.py:459` `nav_baseline`），此后只看日内回撤。static 绝对破产口径本可正交兜底（`risk_layer_orchestrator.py:739/:900`），但 `bankruptcy_floor_initial_capital` 在 `start_paper_session.py` 内**未注入**（实测 grep 零命中），命中其"未注入=大声告警不判定"分支（:546） | :459/:739/:546 | 峰值落 state_store 跨日续存，或强制装配初始本金 static 腿 | 多日累计跌 20% 时阶梯仍显示 0% |
| KS-10 | **P2** | **两处死槽/文档矛盾**：①`TradingSession(kill_switch=KillSwitchLite)`（:312/350/934-936）在 src/scripts 内**零装配点**（实测 `kill_switch=` 无命中，仅 C-004 合规闸一层永不生效）；②AI 探针跨进程不可见——`kill_switch_clear()`（`pipeline_events.py:139-152`）读的是**本进程单例**，若拉闸发生在 AutoRuntime 进程，管线进程探针恒 NORMAL（方向是 fail-closed 于探针异常，但"恒 NORMAL"不属异常）；③`risk_layer_orchestrator.py:460` 类 docstring 用法示例硬编码 `DrawdownTracker(initial_net_value=1_000_000.0)`，生产真源是券商实时净值（`start_paper_session.py:459`）——示例照抄即 AUM<85 万首轮即假 EMERGENCY | 三处 file:line | 删死槽参数或补装配；AI 熔断改跨进程态（state_store）；docstring 示例改 `nav_baseline` 占位 | 合规层假装有闸；示例误导新装配路径 |

**复核为"合格、不立项"**：注册表 fail-closed（KS 之外最好的一个点）、EMERGENCY 边界含等号、
非有限值双点门禁、`_query_today_fills` 缺能力时降级有 warn、五触发源汇入单一仲裁点（:823/825/900/1063/1220/1696
互斥幂等，仲裁点设计意图与实现一致）。

## 2.5 自欺模式对号表（任务点名的五类，逐条判命中）

| 自欺模式 | 命中 | 具体条目 |
|---------|------|---------|
| 产而不消（flag 无人消费） | **命中 4 条** | 编排器/响应层零发令（KS-3）；五级表 active/cooldown/auto_reenable 无人读（KS-4）；`KillSwitchLite` 槽零装配（KS-10①）；L3 看门狗裁决零 call site（1.3 表 L3 行） |
| 阈值一处声明、另一处另用字面量 | **命中 2 条** | KS-7（0.05/0.10 在 controller 码内，注册表只发 tracker 三档）；KS-4（日亏 3% 只在散文 trigger_condition 里，与阶梯无换算） |
| 给定输入值域后永不触发的分支 | **命中 1 条 + 1 条未证** | 命中：`check_consistency`/`is_tripped` 的全部分支因无生产者而不可达（KS-3）；未证：`trading_kill_switch.evaluate()` 内 `if not ks.active` 分支是否永真（无人调用，无从取值域，标 未验证） |
| 异常被吞导致守卫失效 | **命中 3 条** | KS-5（`_emit` 吞仲裁点异常→清算不跑且闩锁死）；`trading_kill_switch.evaluate` :150-151 吞 evaluator 异常后返回"无触发"（**判据异常=不熔断，fail-open**）；`_reconcile_tick` :1825 吞对账异常仅"下轮重试" |
| "已接线"文档声明被代码打脸 | **命中 3 条** | `drawdown_watchdog.py:6` CONSUMERS 称"独立看门狗进程(外部调度器驱动)"，仓内无该驱动（`process_reaper.py`/`register_process_reaper_task.ps1` 零 kill_switch 引用，实测）；`killswitch_response_levels.py:5-8`（CONSUMERS 只登记 tests + MATURITY=production + INVARIANTS 称"level_3 系统级全局熔断+交易级联动"），无生产者路径；`notifier.py:164` docstring 称"kill_switch_triggered 自动通知 Owner（永久系统四要素：自动触发）"，交易域侧永不被触发 |

诚实声明（**未验证，不立项**）：`risk/core/alert_generator.py:235-257` 会因
`report.kill_switch_active` 判 RED 告警，但该 RED 告警的下游出口（谁读 AlertGenerator 产物、
是否落到 Owner 可见面）本次未追，故 KS-2 的表述严格限定为"熔断仲裁点自身无出口 + EventBus
订阅链断裂"，不等于"全系统绝无可能知悉"。`governance/escalation/escalation_engine.py`
与熔断的交互亦未追（仅确认 reaper 与熔断无耦合）。

## 3 六向挖矿日志表

| 向 | 内部发现 | 判定 |
|----|---------|------|
| ①上游（净值进料） | nav 由会话按最新价市值算（`trading_session.py:556-580`，缺价回退成本价）；KS-9 峰值不续存 | signal |
| ②下游（执行） | 三层拒单闸门 L0/L1/L2 各就各位但装配面不对称（1.3 表）；L3 看门狗零 call site（KS-2/KS-3 类） | signal |
| ③机制（判定） | 阶梯判定正确；BS-007 `kill_advised` 只来自黑天鹅（`drawdown_controller.py:430-431`），**回撤到 15% 不由 controller 建议**，只由 tracker 监听链点火——两条阶梯各自点火 | signal |
| ④后端（状态/持久化） | validator 有 Crash-only 外部化（:144-176 加载 + 损坏 fail-closed）；编排器闩纯内存无复位（KS-8） | signal |
| ⑤前端（告警透出） | 零出口（KS-2）；`frontend/services/dashboard_feeds.py` 只透出 `query_drawdown_throttle`（:29），读 controller 不读熔断态 | signal |
| ⑥数据字段 | `KILL_SWITCH_STATE_NAMESPACE` 记录含 active/event_id/reason/scope/reset_at/confirmed_by（:120-125）——审计字段够用，缺"谁批准的复位"与持仓核验的强制约束（`holdings_verified_zero` 缺失只 warn，:371-376） | signal |

**计数：signal 6 / noise 0 / 受阻 0。**

## 4 残余/待裁定（须 Owner，不自批）

1. **KS-1 触发源选择**：日内风险评估挂哪个既有事件（成交回调 / 行情 tick / 持仓变更 / 日切）？
   本挖矿只指出"现在等于调仓频率"，不替 Owner 选点（选点=生产流转，high 门位）。
2. **KS-2 告警渠道**：`pipeline_events.alert()` 注释自陈"渠道未定=日志+Alerter 落盘先行"
   （:155-164），熔断类事件是否升格为独立渠道（短信/IM）属 Owner 决策。
3. **KS-4 五级表去留**：删表 vs 逐条落判据，是"注册表净删"级动作，须裁定；日亏 3% 与
   THD-DRAWDOWN 5/10/15 的口径关系（并存还是取代）亦须裁定。
4. **KS-7 阈值收口**：0.05/0.10 收进 THD-DRAWDOWN-001/002 还是新开 THD-POS007-*——
   注意真源数值 5%/10%/15%（THD-DRAWDOWN-001/002/003）、`MIN_COMMISSION=5`、
   佣金万 0.854（`Decimal("0.0000854")`）均为 Owner 已确认事实，本文不改。
5. **KS-6  Timer 豁免**：盘中对账若判定为"非 reconciler 而是巡检"，需登记豁免裁定，否则按 §9 第 3 条改事件触发。
6. **KS-8/KS-9 复位剧本**：人工复位 SOP（改记录→重启→峰值如何续）属运行手册层，需 Owner 定稿后再接自动路径。

## 5 子节点清单

| 节点 | 为什么值得挖 | 建议投喂 |
|------|-------------|---------|
| `risk/stop_loss.py` 清算执行体 | `trigger_kill_switch:98` / `execute_kill_switch_liquidation:282` 是唯一真发单点，幂等键 event_id、LIQUIDATING 锁、15 笔/秒限流的实际语义从未被挖 | stop_loss.py 全文 + `tests/risk/test_l04_risk_management.py` |
| `ex_core/pre_execution_checker.py` 四级闸门 | 唯一真 Fail-Closed 层，闸门 2/3/4（时段/快照/否决）判定链与 veto_engine 真源未挖 | pre_execution_checker.py + `risk_veto_engine` |
| `ashare_systemic_risk_detector` + 五态降级机 | 另两条点火源（LEVEL_3:1063 / UNWINDING:1220）的指标由谁生产、`rollback_metrics_provider` 是否真注入（本次未核） | risk_layer_orchestrator §A3/A4 + rollback_state_machine |

## 6 封矿判定

- **本节点主体封批**：入口四套同名件已辨明（1.1），真实触发链七跳逐跳定性质（1.2），
  消费核实到"三层闸门只有一层全装配"（1.3），fail 方向逐路径判定（1.4），10 条发现全部
  落到 file:line 或实测数值，残余 6 条待裁定不自我放行。
- **转子节点**：清算执行体、四级闸门、系统性/降级双点火源（§5）。
- 一句话结论：**这套保命链是"计算核对、判定核严、发令核全哑"——回撤阶梯该算的都算对了，
  但它只在调仓那一刻被看一眼、拉闸之后没人通知 Owner、而唯一真拦住单的层是靠装配脚本手写
  lambda 兜住的；真正在跑的熔断是"沉默的熔断"。**
