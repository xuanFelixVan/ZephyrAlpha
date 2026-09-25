---
ttl: task_bound
title: RSK-5 MINE
---

# RSK-5 尾部风险 EVT/POT + UP-5 对冲信号 — 深挖簿

> 车道 L08 风控 · 子块 5 · 班次 st-qmine-20260925 · 只读挖掘。
> 起点真源=`../SKEL.md` §2 RSK-5（其⑤"地图自相矛盾如实注"由本簿给出裁决证据）。

## ① 职责一句话

用极值理论（POT/GPD）+ ES/CVaR + 跳跃计数把"组合收益分布的左尾"量化为可裁决的预警与折扣输入，并在 CVaR 破阈值时给出**建议性质**（非指令）的尾部对冲信号。

## ② 现状实测（生产触发面判定：**监控腿已接电（但节拍被调仓事件绑架）；VaR 破限折扣腿只读不推进（实质惰化）；对冲信号腿零消费**）

| 件 | 实码 | 生产触发面实测 |
|---|---|---|
| `risk/core/tail_risk_monitor.py`（MOD-RK-15，715 行） | ES/CVaR、GPD(ξ,β) POT 拟合（ξ>0 判厚尾）、跳跃计数（`jump_count` 单调非减）、FRTB 加价（头注 `:24-42`）；POT 失败计数器跨日持久化：连续 5 日拟合失败 → 分位阈值 0.90→0.85（fail-closed，v0.2.0 AI-POT-001） | **已接电（实码+生产装配双证）**：`scripts/start_paper_session.py:108 import TailRiskMonitor`、`:461 tail_risk_monitor=TailRiskMonitor()` 注入 orchestrator；`ex_core/risk_layer_orchestrator.py:25` 数据流声明 `VaRCalculator.calculate + TailRiskMonitor.assess → DrawdownController.evaluate`；`:499` 构造必填参数。**但**评估唯一驱动=会话 `_do_rebalance` 轮（RSK-4 实测）→ **无调仓事件即整日不做尾部评估**（新缺口 L08-C32） |
| `risk/core/var_breach_state_machine.py`（36 号 §3.15，320 行） | 头注 `[CONSUMERS] MOD-POS-008(DrawdownController.evaluate var_breach_state 乘性折扣); RiskLayerOrchestrator(编排注入)` | **半接电且惰化**：orchestrator `:187` import、`:480 VarBreachStateMachine.load(state_store)`（读侧在产）、`:533` 持实例、`:815 var_breach_state=(self._var_breach_machine.state …)` → `position/core/drawdown_controller.py:417 _var_breach_multiplier` 乘性折扣生效、`:467-472` 未知态抛错 fail-closed。**但全 `src/zephyr` 内 `_var_breach_machine` 只出现 2 次（赋值 + 读 state），无任何推进调用**；其声明的推进器=`risk/core/var_intraday_recalc.py`（`IntradayVarRecalcController`）已被自家头注 `:6` 判为"**设计性死件**：src 零实例化零调用；原声称 35 号 §3.13 intraday_risk_loop 与 RiskLayerOrchestrator 编排注入均未接线；现役盘中 VaR/ES 已由 evaluate_intraday 每轮直接重算，本重算控制器功能被取代、无独立消费出口"→ **破限态永不迁移 ⇒ 折扣恒等 1.0 ⇒ 这条乘性折扣腿在生产中是哑的**（L08-C33） |
| `pf_alloc/core/tail_hedge_signal.py`（MOD-PA-024，71 行） | 纯函数 `tail_hedge_signal(portfolio_returns, cvar_threshold=-0.03, confidence=0.05, window=60)` → DataFrame[cvar_pred, hedge_signal, cvar_excess]；`[STARTUP] manual`、`stability=experimental`、`safety=L`；头注 `[CONSUMERS] TDM 风控层（UP-5 尾部对冲指令）；策略工厂 E8 组装分配` | **零消费（账实不符候选）**：`src/`+`scripts/` 全仓 grep `tail_hedge|TailHedge` **除本文件定义外零命中**；而 `config/trading_decision_map.yaml:3159 note_confirmed: 2026-09-20` 与 `:3172-3174` 明写"**2026-09-20 UP-5 接线，final3 P5**：尾部对冲信号建议通道——组合预测 CVaR(5%) 破风控阈值…喂 R1-03 白名单通道（D107 尾部弹药回测验证前维持休眠 fallback）" → 接线=**图面接线（节点+注记）而非代码接线**，建议通道在 src 内不存在（L08-C34） |
| `risk/core/copula_garch_joint.py`（MOD-RK-33，347 行） | 同域尾部依赖（GARCH + Copula） | 注册面：`risk/core/__init__.py:83-88` 注记"**并行会话 scaffold 的 copula_garch_joint(CAND-RSK-036) 导出注册**"→ 身份仍是 CAND（候选）级 scaffold，仅 `__init__` 导出 + 自家测试 `tests/risk/core/test_copula_garch_joint.py`，**无生产消费者**；与 tail_risk_monitor 的依赖关系仅存在于同域文档，不在 import 图 |
| 前端面 | `frontend/services/dashboard_feeds.py:69,613 snapshot = TailRiskMonitor().assess(np.asarray(returns…), portfolio_value, now)`（BFE-31）；`frontend/dashboard/web/features/warroom/wr-risk-cards.js:65` | **前端另起一次判定且当前为 mock 渲染**：`frontend/dashboard/web/pages/live.html:287` 原文"新增三行（BFE-26/30/31…）：回撤油门刹车=query_drawdown_throttle→DrawdownController · 流动性=query_liquidity_status→LiquidityMonitor · 尾部风险=query_tail_risk_status→TailRiskMonitor——**均 prod，当前 mock 渲染**" → 后端件在产、前端未接真源；且 `:613` 每次新建 `TailRiskMonitor()` → 跨日持久化的 POT 失败计数器（本件核心 fail-closed 机制）**在前端调用路径上被丢弃**（同 RSK-4 L08-C28 病根：展示层重算而非读 snapshot） |

**结论（对 battle_map 口径矛盾给裁决）**：`battle_map_09_risk_control.md` BM-RC-06-B 自报 production + 有效状态🟧设计态待施工 —— 两说各对一半：**监控算法与编排注入=production（有装配铁证）**；**独立盘中 runner + 前端真源 + 对冲建议通道 + VaR 破限推进 = 未施工**。地图应改写为四段态而非单一🟧。

## ③ 六向台账

| 向 | 台账 |
|---|---|
| 上游 | 收益分布尾部序列（S34 供数：尾部数据+跳跃检测，`ulib3b_supply_relationship_ledger.md:69`）；VaR 基准=MOD-RK-05 口径；`portfolio_returns` 序列（tail_hedge_signal 入参）；state_store（var_breach 的 `load` 真源）；调用方每轮传入 returns/portfolio_value（orchestrator 装配） |
| 下游 | 头注 [CONSUMERS] MOD-RK-03（Portfolio Risk Monitor 尾部告警）+ MOD-RK-17（Kill Switch 极值触发）→ 实测经 `risk_layer_orchestrator` 极值分支汇入 `_engage_kill_switch`（`arbitration_order_v1_draft.md:103` 记"尾部极值为六源之一"）；`DrawdownController.evaluate`（乘性折扣，现惰）；前端 BFE-31（mock）；UP-5→R1-03 白名单通道（休眠 fallback，D107；`defensive_asset_whitelist.py` design，见 RSK-3/RSK-8） |
| 算法/机制 | POT 超阈值法 + GPD 形状参数 ξ 厚尾判据；ES/CVaR 一致尾部度量；跳跃计数单调非减；FRTB 加价；**AI-POT-001 失败降级=阈值放宽（0.90→0.85）而非放行**（fail-closed 方向正确，可作其他 EVT 件的模板）；tail_hedge 的"cvar_excess"作为建议强度；CVaR 近似=`rolling(60).quantile(0.05)` 后取尾均值 → **实现是历史回溯，而 docstring `:19` 声称"用分布预测的分位数计算（非历史回溯）"——算法自述与实现相反**（L08-C35） |
| 后端 | 依赖 numpy/pandas；`TailRiskMonitor()` 有状态实例（跨日持久化失败计数）⇒ **必须单例长驻**，前端与任何旁路新建实例都会丢态；orchestrator `:499` 必填注入（无默认，未注入即启动失败=好设计）；`VarBreachStateMachine.load(state_store)` 单侧读；`[STARTUP] manual`（信号件无自动启动） |
| 前端 | warroom `wr-risk-cards.js:65` BFE-31 卡片；`live.html:287` 自述 mock；VaR/CVaR 与跳跃计数在面板上的中文标签需过三层翻译（运维红线 9）；无"折扣腿惰性"的可见性（面板看不出乘性折扣没生效） |
| 数据字段 | `jump_count`、`tail_index(ξ)`、`es/cvar`、`frtb_addon`、`pot_failure_streak`（跨日）；`var_breach` 态 ∈ {NORMAL, BREACHED, RECOVERY}（`dashboard_feeds.py:146,156` 同枚举）；信号输出三列 `cvar_pred/hedge_signal/cvar_excess`；**缺**：EVT 拟合质量指标（KS/AD 优度、样本外）无字段 ⇒ "ξ 可信度"不可复核；破限态无推进时间戳 ⇒ 无法区分"真 NORMAL"与"没推进"；无物化表（L08-C06） |

## ④ 缺口清单（本层新增）

| # | 缺口 | 证据 | 判级 |
|---|---|---|---|
| L08-C32 | 尾部评估节拍=调仓节拍：市场剧变但策略不触发调仓的交易日，尾部风险整日不评估（与"独立盘中 runner 缺位/TRD-A07"同源但更精确——不是缺 runner，是**已有评估被绑在错误的事件源上**） | `risk_layer_orchestrator.py:25` + RSK-4 实测 `_do_rebalance` 唯一驱动 | **P0 级候选（资金安全语义）**；修法须守运维红线 3（事件触发，禁 Timer/cron）→ 候选事件源=tick/行情到达或日中 checkpoint 事件 |
| L08-C33 | VaR 破限状态机只读不推进 → 乘性折扣恒 1.0（哑腿）；且无人声明"该由谁推进"（原声明件 var_intraday_recalc 已自判设计性死件） | `:480/:533/:815` + `var_intraday_recalc.py:6` | P1（**禁以"折扣是保守加强项，不生效=偏松"为由拖**：它会让 RED 级破限不降仓位） |
| L08-C34 | UP-5 "已接线"注记与零消费冲突（图面接线冒充代码接线）→ 与 RSK-3 L08-C24 同族账实不符，需统一以"实码+生产事件链"二证重判 | `config/trading_decision_map.yaml:3159,3172-3174` vs 全仓 grep 零命中 | P1（治理面，禁文档冒充） |
| L08-C35 | `tail_hedge_signal` docstring 声称"预测分位数（非历史回溯）"，实现为 rolling quantile 历史尾均值；且信号未绑定 A 股可执行工具（个股无期权、对冲池=期货/ETF，见 RSK-6 S45 零分析消费）→ 信号语义悬空 | `:19` vs `:52-63` | P1 |
| L08-C36 | 前端旁路新建 `TailRiskMonitor()` 丢弃跨日 fail-closed 计数器 + 面板 mock 未接真源 | `dashboard_feeds.py:613`、`live.html:287` | P1（与 RSK-4 L08-C28 同批治本：展示层只读 `RiskLayerSnapshot`/持久化态，禁重算） |
| 引用不重复 | SKEL RSK-5⑥（S34 供数→runner 环缺位=TRD-A07、UP-5 回测欠账 D107、EVT/POT 标准件对表）；L08-C08（R1-03 白名单回测 or 显式休眠，与本块对冲信号同批验证） | — | 已在账 |

## ⑤ 自审闸三态裁定

**MINING**。清空骨架 §3 债 2 项中的 1 项（tail_hedge_signal.py 正文 71 行全读；var_breach 消费链实测）。仍欠：
1. `tail_risk_monitor.py` 正文（715 行，本簿只取头注口径）：POT 阈值选取、GPD 拟合实现、失败计数器持久化键、FRTB 加价公式；
2. `docs/03_modules/_domain_risk/algo_flow/tail_risk_monitor.yaml`（外置推导图）；
3. `copula_garch_joint.py` 头注以下正文（尾部依赖估计方法、是否与 EVT 件同阈值轴）；
4. `var_breach_state_machine.py` 正文（迁移条件与"谁该调它"的公开 API 名，用于 L08-C33 施工定位）；
5. 36 号 memo §3.15/§3.16（FHS 编排与破限状态机的关系——orchestrator `:118` A5 声明 `should_switch_to_fhs` 三触发 + 10 日冷却 + 3 次永久禁用 + `note_fhs_backtest_verdict` 次日裁决，**这条才是现役尾部→执行的另一条腿，必须核实其是否也惰性**）；
6. `tests/risk/test_fhs_orchestration_wiring.py` 断言面。
禁封矿：尾部风险是"低频高损"域，现状"没触发过"不构成降级理由（量尺=终局全貌）。

## ⑥ 挖矿日志

- Grep src+scripts `TailRiskMonitor|tail_hedge|copula_garch|VarBreachStateMachine|var_breach_state` → 45 命中，一次拿齐三条腿的装配/消费/前端/mock 证据（`start_paper_session.py:461`、`orchestrator:25/480/815`、`dashboard_feeds:613`、`live.html:287`、`var_intraday_recalc.py:6` 诚实死件声明）。
- Bash 只读：四件行数体检（715/71/320/347）+ `config/trading_decision_map.yaml` 内 `UP-5|D107|tail_risk` grep → 取得 `:3159 note_confirmed 2026-09-20` 与 `:3172-3174`（图面接线证据）+ D107 尾部弹药/预备金语义（`:5672` 外审修复注记：尾部弹药=D110 信号触发+回测验证后动用）。
- Read `tail_hedge_signal.py` 全文（71 行）→ L08-C35 算法自述矛盾 + 零 A 股工具绑定。
- Grep `_var_breach_machine|breach_machine\.|def (advance|observe|migrate…)` → **决定性负证据**：全 src 内该类实例仅"赋值+读 state"两处，无推进调用 ⇒ 哑腿判定成立。
- 顺带取证（未额外调用）：`risk/core/__init__.py:83-88` copula 件为并行会话 scaffold（CAND 级）。
- 纪律：只读；未起 numpy/pandas 计算作业；未跑测试；GPU 未触碰；无 git 写。
- 外部对表：未做（留统一轮；候选标准件=McNeil-Frey-Embrechts《Quantitative Risk Management》POT/GPD 公式对表，`../SKEL.md` §5 已登记；A 股适配闸=个股期权不可得、以股指期货/ETF 为对冲载体，须核 S45 期货池消费）。
