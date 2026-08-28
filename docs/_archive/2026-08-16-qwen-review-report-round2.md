---
title: Qwen 外部独立审查报告（第二轮）——量化核心算法正确性专项
date: 2026-08-16
reviewer: Qwen3.8-Max（外部独立审查员）
ttl: permanent
completes_when: "业主裁定后归档"
---

# Qwen 外部独立审查报告（第二轮）

> **审查方**：Qwen3.8-Max（一次性深度审查，只审不改）
> **任务书**：`2026-08-16-codex-external-review-brief.md` R1-R5 + 四项深挖（①crash 恢复幂等性 ②Kill Switch 清算重复触发 ③POT 厚尾拟合小样本稳定性 ④memo 36 FHS 声称 vs 代码）
> **独立性声明**：未打开 `2026-08-16-kimi-review-report-round1.md`（一审报告），本报告全部结论来自源码直读 + 独立手算（隔离运行时重算，不导入项目代码、不信测试锚点）。
> **纪律**：A 股语境（T+1/涨跌停/无裸卖空）；P0=会亏钱/会失控，P1=口径漂移/边界未定义，P2=健壮性建议。

---

## 一、P0 发现（会亏钱/会失控）

### [P0-1] 风控全链路（VaR/ES/回撤/KillSwitch/流动性危机/对账）未接入生产交易路径——纸面熔断

位置：全库接线层（证据散布于下列文件）

证据（全部为"实例化/调用方"搜索结果，非推断）：

| 模块 | 生产实例化/调用方 | 搜索范围 |
|---|---|---|
| `VaRCalculator()` | 0（仅 docstring 示例 [var_calculator.py L295](file:///d:/ZephyrAlpha/src/zephyr/risk/core/var_calculator.py#L295)） | src 全库 |
| `TailRiskMonitor()` | 0（仅 docstring [tail_risk_monitor.py L343](file:///d:/ZephyrAlpha/src/zephyr/risk/core/tail_risk_monitor.py#L343)） | src 全库 |
| `DrawdownController()` / `.evaluate()` | 0（仅 docstring [drawdown_controller.py L413](file:///d:/ZephyrAlpha/src/zephyr/position/core/drawdown_controller.py#L413)） | src 全库 |
| `DrawdownTracker()` / `on_drawdown_alerted` 监听注册 | 0 | src 全库 |
| `run_intraday_liquidity_check()` | 0 | src 全库 |
| `execute_kill_switch_liquidation()` | 0（唯一调用点在 tests/risk/test_l04_risk_management.py） | src 全库 |
| `daily_pnl_check()`（唯一通向 `trigger_kill_switch` 的路径） | 0 | src 全库 |
| `RiskOrchestrator`（memo 36 全文依赖的编排者） | **类不存在**，src 零匹配 | src 全库 |
| `PositionReconciler(` / `SettlementReconciler(`（ex_core/trading 版） | 0（仅 docstring Usage 示例） | src 全库 |

生产交易主链 [trading_session.py](file:///d:/ZephyrAlpha/src/zephyr/ex_core/trading_session.py) 实际接入的风控只有：`KillSwitchLite`（[discipline_prohibition_checker.py L121](file:///d:/ZephyrAlpha/src/zephyr/compliance/discipline_prohibition_checker.py#L121)，策略级、当日有效、次日自动复位）+ 日申报计数门禁 + 四项严禁纪律闸。

推演：memo 36 §3.5 的 5 级系统性风险、BS-007→Kill Switch、35 号回撤 EMERGENCY（>15%）→Kill Switch、流动性危机 LEVEL_3 逃生指令——**全部只存在于"模块内部逻辑正确"的测试里，没有任何生产代码会调用它们**。回撤 25% 时系统不会熔断，会继续按策略信号下单。项目记忆声称"风险相关模块先施工至 production，符合风险优先原则"——模块是 production，但**接线是零**，等于消防栓装了没接水管。

修复建议：这不是算法 bug，是集成缺口，优先级应高于一切算法修复。最小补丁：① trading_session 盘前/盘中循环注入 `DrawdownController.evaluate()` + `VaRCalculator/TailRiskMonitor`，`position_cap` 喂入仓位引擎；② `DrawdownTracker.on_drawdown_alerted` 注册 EMERGENCY→`trigger_kill_switch`+`execute_kill_switch_liquidation` 监听；③ KillSwitch 状态持久化（见 P0-3）；④ PositionReconciler 接入盘中定时（蓝图阶段 2 本就规划）。接线前建议冻结实盘资金规模。

---

### [P0-2] crash 恢复幂等性（深挖①）：无重放机制 + PositionTracker 明示不做 fill_id 去重——重启即账本归零，未来任何重放都会重复记账

位置：[tracker.py L147-157](file:///d:/ZephyrAlpha/src/zephyr/ex_core/position_tracker/tracker.py#L147-L157)、[order_execution_saga.py L731-748](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_execution_saga.py#L731-L748)、[miniqmt_broker.py L825-852](file:///d:/ZephyrAlpha/src/zephyr/ex_core/adapters/miniqmt_broker.py#L825-L852)

证据：
1. `PositionTracker.apply_fill` docstring 原文："**阶段1不做幂等去重（同一 fill_id 重复调用会重复更新）。幂等性由调用方保证**"（L154-157）。
2. 全库不存在 crash 后从持久化日志重放成交重建 PositionTracker 的代码（搜 replay/restore/recover/重建 于 ex_core 零命中）；PositionTracker 无序列化接口。
3. 断线重连四步（miniqmt_broker `_reconnect`）的 Step 3 `_sync_order_state_on_reconnect` 只把券商端 `traded_volume/traded_price` 同步进**订单缓存**（L844-847），**不调用 apply_fill**——持仓账（holdings/cash/avg_cost）不补齐。
4. FillHandler 的 fill_id 幂等集是纯内存 `set`（[fill_handler.py L196](file:///d:/ZephyrAlpha/src/zephyr/ex_core/fill_handler.py#L196)），重启即失效。

推演（回答任务书"重复恢复会不会重复成交"）：
- **现状**：没有重放，所以不会"重复成交"——但代价更糟：进程重启后系统账归零，与券商账全面漂移，而 PositionReconciler 又未接线（P0-1），系统将以空仓错觉继续交易 → 重复建仓（真金白银的重复买入，比重复记账更贵）。
- **Saga 补偿路径**：`_compensate_position` 构造 `rollback-{fill_id}` 反向 Fill 调 apply_fill（L736-748）——rollback fill 是新 fill_id，天然绕开任何 fill_id 去重；若补偿本身因异常重试执行两次，持仓被**双倍回滚**（多头直接变空头数量）。
- **Saga 超时竞态**：step4 超时→撤单补偿，若撤单时订单恰好成交（cancel 返回 False），代码仅 log warning（L719-722），fill 回调在 finally 被清理 → 成交真实发生但 step5 未执行 → 系统账少记持仓。这正是任务书 R4.1 点名的"部分成交后断线恢复"场景。

修复建议：① apply_fill 增加 fill_id 持久化去重集（DB/append-only 文件），这是阶段 2 蓝图已承诺项，应提到 P0 优先级；② 启动恢复流程：重启后先 query 券商持仓+当日成交全量重建 PositionTracker（以券商为准），重建完成前禁止下单（Fail-Closed）；③ rollback fill 用确定性 fill_id（`rollback-{原id}` 已具确定性，配合①的去重集即可幂等）；④ Saga 超时分支在 cancel 返回 False 时强制查询订单终态，已成交则补走 step5 而非吞掉。

---

### [P0-3] Kill Switch（深挖②）：状态纯内存（重启即解除）+ 清算函数无幂等/无状态锁（重复触发=重复下单）

位置：[default_risk_validator.py L58-59, L208-214](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_risk_validator.py#L58-L59)、[stop_loss.py L203-357](file:///d:/ZephyrAlpha/src/zephyr/risk/stop_loss.py#L203-L357)

证据：
1. `_kill_switch_active` 是构造参数内存布尔，无任何持久化（文件内搜 persist/save/load 零匹配）。**进程 crash/重启 → 熔断状态自动归 False**。若熔断后、清算完成前进程挂掉（极端行情下恰是高发场景），重启后系统自认"未熔断"，继续接受新订单——熔断在最需要它的时刻失效。
2. `execute_kill_switch_liquidation` 每次调用生成**新 uuid event_id**（L251），无幂等键、无"已清算标的"去重、无并发锁。positions 由调用方传入：若首次清算部分成交后（如 1000 股已卖 500），第二次触发仍用旧 positions 再发 1000 股市价单。A 股无裸卖空下剩余 500 股的卖单会成交 → 对同一持仓发两轮全量卖单；若持仓已清零则被券商拒单，白耗申报额度（申报计数器不记撤单，见 P1-5，拒单记录同样消耗申报口径）。
3. 两个触发源（drawdown EMERGENCY 事件 + BS-007 advised）无互斥仲裁（见 P1-7），并发调用本函数将并行发单。
4. `stop_loss.trigger_kill_switch()` 自述"仅记录事件，不管理状态"（L153-157），与 DefaultRiskValidator 的状态管理是两套独立机制，无调用关系——触发记录与状态置位可能只发生其一。

修复建议：① kill_switch 状态落盘（JSON/DB，含触发时间+reason+event_id），启动时加载，Fail-Closed（读不到状态按已熔断处理）；② 清算函数加全局状态锁（`LIQUIDATING` 态拒绝二次进入）+ 逐标的清算前查实时持仓（以券商 `get_holdings` 为准而非调用方快照）+ 幂等键（触发事件 event_id 贯穿）；③ 合并两个触发入口为单一仲裁点。

---

## 二、P1 发现（口径漂移/边界未定义）

### [P1-1] 深挖④结论：memo 36 声称的 FHS 在代码中不存在；且文档以可执行语气引用不存在的 API

位置：`36_var_es_monitoring.md` §3.10 动作 4 / §3.9.1 / §3.16 vs `src` 全库

证据：src 全目录搜 `fhs|garch|should_switch_to_fhs|fhs_engine|FHS_COOLDOWN|Filtered Historical|残差重采样`（不区分大小写）**零命中**。memo 36 内部口径自相矛盾：
- §3.16 标题注明"远期 Phase 2"（诚实）；
- 但 §3.10 RECALIBRATE 动作表把 `RiskOrchestrator → fhs_engine.enable()` 写成**带执行者、带参数、带回滚机制的可执行动作**（"GARCH 拟合失败→回退 historical+标记 FHS 不可用"）；
- §3.9.1 Christoffersen 独立性失败分支写"action = RECALIBRATE，**优先选 FHS（§3.16）**"——独立性失败时的首选动作指向不存在的代码；
- 动作表的执行者 `RiskOrchestrator` 类本身也不存在（src 零匹配）。

风险：回测一旦真出现独立性失败（A 股波动率聚集下并不罕见），运维/AI 照文档执行会调用不存在的接口；"已施工 ✅"标记（§3.11 组件状态表全部打勾）加剧误判。

修复建议：§3.10 动作 4 改标"未施工（远期）"，独立性失败的当前实际动作明确为"动作 1 扩窗口 + 动作 2 切方法"；RiskOrchestrator 未建前，所有以它为执行者的动作表统一标注。

### [P1-2] memo 36 §3.2 声称的 `assess(returns, var_forecast)` 与"强制校验 es≥var"在代码中不存在；ES 尾部切片口径在离散收益下系统性失真

位置：[tail_risk_monitor.py L359-376, L437-454](file:///d:/ZephyrAlpha/src/zephyr/risk/core/tail_risk_monitor.py#L359-L376) vs memo 36 §3.2

证据：
1. 实际签名 `assess(returns, portfolio_value=1.0, now=None)`——**没有 var_forecast 参数**，因此文档声称的"强制校验 `es_forecast >= var_forecast`"（§3.2 原文）不可能存在；模块蓝图 INVARIANTS 写着 `ES>=VaR` 但代码无任何校验。
2. ES 实现 `tail = returns[returns <= var_quantile]`，其中 `var_quantile = np.quantile(returns, 0.05)` 为**线性插值**分位数。独立手算（隔离运行时，线性插值口径）：100 样本 = 1×(-0.10) + 99×0.0 时，0.05 分位插值位置 = 0.05×99 = 4.95，落在 sorted[4]=0 与 sorted[5]=0 之间 → **q=0，VaR=0**，tail 切片 = 全部 100 个样本 → ES=0.001。历史中明明有 -10% 损失日，95% VaR 却报 0。A 股策略日收益含大量 0（未持仓/平盘日），该失真不是边角案例而是常态。
3. 任务书 R1.2 的 off-by-one 之问：代码取"≤ 插值分位数的切片"，当插值把分位数拉向 0 时，切片混入大量非尾部样本，ES 被稀释；文档 §3.2 公式注释写"最差 (1-c) 比例收益均值的负数"——**代码口径（≤插值分位数）与文档口径（最差固定比例）在离散样本下不一致**。

修复建议：① 补 `assess(returns, var_forecast)` 契约或修订文档；② ES 改用"最差 ⌈n(1-c)⌉ 个样本均值"的固定比例口径（与文档对齐，且天然满足 ES≥VaR 的离散形式）；③ 增加 ES≥VaR 硬校验，违反时告警而非静默。

### [P1-3] 深挖③结论：POT 厚尾拟合在 60 日窗口下常态样本量 ≤3，GPD 拟合是噪声发生器

位置：[tail_risk_monitor.py L458-512](file:///d:/ZephyrAlpha/src/zephyr/risk/core/tail_risk_monitor.py#L458-L512)、memo 36 §3.7

证据（独立手算，线性插值分位 + 严格大于阈值）：
- 60 日窗口、50% 负收益日（30 个 losses）：u = quantile(losses, 0.90) 插值位置 26.1，严格大于 u 的 exceedances **仅 3 个** < 5 → `return None`；
- 60 日全负收益日（60 losses）：exceedances 6 个，刚过 ≥5 门槛；
- min_history=30 且 15 个负日：exceedances 2 个 → None。

即：memo §3.7 声称"POT 拟合 60 交易日，最差 10% ≈ 6 个样本"隐含假设**天天亏损**；真实策略（负日占比 40-60%）下 POT 要么永久返回 None（厚尾诊断静默缺失），要么用 5-6 个超额值拟合 GPD——MLE 在 n<20 时 ξ 的抽样方差极大，`ξ>0.2 → 厚尾告警`、`ξ>0.5 → FRTB 加价 3.0×shape`、`EMERGENCY 联动 Kill Switch` 全部由噪声驱动。另发现 [L480-482](file:///d:/ZephyrAlpha/src/zephyr/risk/core/tail_risk_monitor.py#L480-L482) 存在死代码：先按 returns 右侧（**盈利侧**）算了一遍 threshold/exceedances，随后 L485-489 用 losses 侧重算覆盖——第一遍逻辑方向就是错的且白算，提示该函数经历过未清理的重写。

修复建议：① exceedances < 20（EVT 经验下限）时不输出 shape 驱动的告警/FRTB/EMERGENCY 判定，降级为纯历史模拟 ES + "POT 样本不足"标记；② 删除 L480-482 死代码；③ memo §3.7 的"6 样本"假设修正为按负日占比表达，并把 §3.2 的"连续 5 日 POT 失败→阈值 0.90→0.85"兜底落码（当前未落码，见漂移清单 D5）。

### [P1-4] 系统性风险 5 级仓位上限非单调：YELLOW 0.5 → ORANGE 0.7，风险升级仓位上限反而放宽

位置：[drawdown_controller.py L178-184](file:///d:/ZephyrAlpha/src/zephyr/position/core/drawdown_controller.py#L178-L184)

证据：`_RISK_LEVEL_CAP = {GREEN:1.0, YELLOW:0.5, ORANGE:0.7, RED:0.5, BLACK:0.0}`。VaR 从 3%（YELLOW）升到 5%（ORANGE），position_cap 从 0.5 升到 0.7。ORANGE 语义是"禁止新开+减仓 30%"，但 `position_cap` 是总仓位上限，被下游 sizing 消费时 0.7 > 0.5 意味着升级后**允许持有更多**。memo 36 §3.5.1 表格与代码一致（文档同错），§3.5.3 还称该序列"渐进式减仓……天然避免 gambling-for-resurrection"——0.7 的凸起与"渐进减仓"字面矛盾。

修复建议：若 ORANGE 的 0.7 是"从当前仓减 30%"的存量语义，应与 YELLOW 的"新开减半"语义在契约上分离（新增 `action_semantics` 字段），且对存量上限取 `min(YELLOW_cap, 0.7×当前实际仓位)`；否则直接把 ORANGE cap 降为 ≤0.5 恢复单调。

### [P1-5] 日申报笔数计数器：撤单侧未接线（撤单不计入）+ 计数器纯内存（重启归零）

位置：[cancel_rate_guard.py L160-162, L225-230, L321-327](file:///d:/ZephyrAlpha/src/zephyr/ex_core/cancel_rate_guard.py#L160-L162)、[order_manager.py L280-299](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py#L280-L299)

证据：
1. `record_cancel()` 的生产调用方为零（全库仅 tests 调用）；生产只接了 `trading_session.py:508 record_submit()`。A 股 2026 程序化新规申报口径含撤单，代码注释自己也写"撤单同属申报口径"（L326）——**设计知道要双计，接线只计了一半**。高频撤单的报单频率风险完全漏计，1 万笔阻断线形同虚设（可 9999 报单 + 无限撤单）。
2. `_daily_count/_daily_date` 纯内存，无持久化——重启归零。Kill Switch 清算（P0-3）重复触发产生的拒单/申报在重启后全部清零，阻断线可被"重启"绕过。
3. 跨日重置用 `date.today()` 自然日——交易日口径下无实质问题（非交易日无申报），但夜盘/隔日预申报场景未定义（A 股当前无夜盘，记为边界未定义）。

修复建议：① order_manager 撤单路径（cancel_order 成功/失败均）接 `record_cancel()`；② 计数器落盘（当日计数+日期），启动加载；③ 明确"申报=报单+撤单"口径写入 43 号文档并加 reconciler 校验。

### [P1-6] 结算对账配对键：部分成交场景下 order_id 回退键互相覆盖，成对漏检

位置：[settlement_reconciliation.py L303-321](file:///d:/ZephyrAlpha/src/zephyr/trading/settlement_reconciliation.py#L303-L321)

证据：`key = fill.broker_fill_id if fill.broker_fill_id else fill.order_id`，随后 `system_by_id[key] = fill`——dict 直接覆盖。一笔订单分 3 笔部分成交、且 broker_fill_id 缺失时，3 个 Fill 共享 order_id 键，**只剩最后一笔**进入对账；券商侧 `broker_by_id` 同理。前两笔部分成交的价格/数量差异、甚至"系统有券商无"全部静默丢失。任务书 R4.1 点名的"部分成交后断线恢复"恰是 broker_fill_id 最易缺失的场景（断线期回报丢失，恢复补录时往往只有 order_id）。

修复建议：配对键改为 `(order_id, 序号)` 或多对多匹配（按 order_id 分组后逐笔贪心配价格/数量）；`broker_fill_id` 缺失时至少按 order_id 分组做**数量总和**比对。

### [P1-7] 多 Protocol 同刻触发无仲裁（任务书 R5.4 最担心项，证实未定义）

位置：drawdown_tracker（事件推送）/ liquidity_crisis_manager（返回值拉取）/ default_risk_validator（内存布尔）三套机制之间

证据：
1. 三个 Protocol 对外接口形态互不一致：回撤用监听器事件（[drawdown_tracker.py L309](file:///d:/ZephyrAlpha/src/zephyr/risk/core/drawdown_tracker.py#L309)），流动性危机用函数返回值 `LiquidityLoopResult`，KillSwitch 是验证器内存布尔。全库搜 priority/优先级/仲裁于 risk 域零命中。
2. position_cap 无合并规则：流动性危机恢复侧硬编码 `{0:1.0, 1:1.0, 2:0.70}`（liquidity_crisis_manager L909），触发侧 L2 上限却是检测器配置值——**同一级别两个真相源**；回撤侧 cap、VaR breach ×0.8（未实现）各自独立，无 `min()` 合并点。
3. 极端行情（任务书预设场景：回撤>15% EMERGENCY + 流动性 LEVEL_3 + BS-007 同刻触发）下，三条链各自产出"清仓"指令但无单一执行者，叠加 P0-1（全部未接线）= 无人执行；即便接线，也是三路并发重复清算（见 P0-3）。

修复建议：设立唯一 RiskArbiter：收集各 Protocol 的 cap/动作建议 → `min(caps)` + 动作去重合并 → 单一执行通道；这也应是 memo 36 通篇引用的 RiskOrchestrator 的最小职责定义。

### [P1-8] 幽灵持仓枚举不完整：系统侧"无该标的记录"（连 CLOSED 都没有）漏检

位置：[stop_loss.py L382-386](file:///d:/ZephyrAlpha/src/zephyr/risk/stop_loss.py#L382-L386)

证据：情况 1 判定条件 `strategy_state.get(sym) == "CLOSED"`——券商有仓、系统侧**根本没有该 symbol 键**（get 返回 None）时不判 ghost。该场景真实存在：人工手工建仓、其他通道建仓、crash 后状态丢失（P0-2 重启归零时**所有**持仓都变成"无记录"）。情况 2 依赖 kill_switch_state 参数，而状态本身不持久化（P0-3），重启后恒 "OPEN"，情况 2 永不触发。

修复建议：判定改为 `strategy_state.get(sym) != "OPEN"`（非 OPEN 即 ghost），把举证责任倒置——券商有仓而系统不能证明是 OPEN 的一律报警。

### [P1-9] 流动性危机 LEVEL_2/LEVEL_3 不可达：唯一入口只喂一路信号，逃生指令是死代码

位置：liquidity_crisis_manager `run_intraday_liquidity_check` → detector.check 调用点（L854-858）

证据：该入口只传 `sell_pressure` + `bid_ask_spread` 两路输入中的**一路有效信号**（涨跌停时 spread 置 1.0 计入），检测器按活动信号数定级（1 信号→LEVEL_1，2→LEVEL_2，≥3→LEVEL_3），且未传 sentiment_index（情绪断路器升级路径不走）→ `level_num` 恒 ≤1。后果：L2→1、L3→2 恢复分支、`min_hold_minutes {2:15, 3:30}`、LEVEL_3 `escape_directive`（含 `kill_switch_required=True`，全系统唯一指向 Kill Switch 的流动性逃生通道）**全部不可达**。跌停长期封死时系统只能输出 LEVEL_1（halt_new_orders），无清仓逃生路径。

修复建议：入口补齐第二/三路信号（成交量萎缩、IPO 抽离、情绪指标），或明确裁定"流动性危机永远 LEVEL_1"并删除 L2/L3 死代码与文档承诺。

### [P1-10] 流动性指标语义反转：全零成交额（最坏流动性）被判"流动"

位置：liquidity_monitor `compute_amihud` L243-251、`assess` L359-362

证据：零成交额日 → illiq=inf→NaN→dropna 全部剔空 → `len==0 → return 0.0`；0.0 不大于阈值 → `is_illiquid=False`。同时成交量萎缩侧 `v_ma==0 → return 1.0`（ratio=1.0 不 <0.5 阈值）也不触发。**一只完全无成交的股票被两条指标同时判为流动性良好**。另：索引对齐只查长度不查索引（L458-463），长度相同索引错位 → 除法全 NaN → 同样静默返回 0.0；窗口不足（≥2 点但 <N 点）`tail(n)` 静默用全部点，无告警。

修复建议：全零成交/剔空后样本 < 窗口 50% → 直接 `is_illiquid=True`（Fail-Closed）+ WARNING；索引对齐改为按 index join 并校验重合度。

### [P1-11] memo 31 修订记录声称"§2.3 已落码"，但 dist_adj 分布感知调整因子在代码中不存在

位置：`31_position_sizing.md` L209 + v1.25.0 修订记录 vs src 全库

证据：`dist_adj|distribution_adjust` 在 src 零命中，仅存在于文档（31 号 §2.3.3"默认 ≤1，正偏例外 ≤1.1"）。而 31 号 v1.25.0 修订记录原文："核查确认 §2.2/§2.3/§2.8 全链路已落码"。任务书 R3.2 要求审的"正偏例外 ≤1.1 是否可被构造输入绕过"——**无代码可审**，问题降级为文档-代码漂移（见 D2）。position_sizing_engine 实际只有 C1 半 Kelly + C3 波动率 + C4/C5 VaR/CVaR 调整，无分布感知项。

---

## 三、P2 发现（健壮性建议）

### [P2-1] Kelly 盈亏平衡点浮点尾差：f* = 7.4e-17 > 0 绕过"不下注"分支

位置：[position_sizing_engine.py L336-350, L590-592](file:///d:/ZephyrAlpha/src/zephyr/position/core/position_sizing_engine.py#L336-L350)

证据：独立手算 `p=0.4, b=1.5`（精确盈亏平衡 bp=q）→ `(b*p-q)/b = 7.4e-17`，`max(0.0, f_star)` 保留该正尾差 → `f_star <= 0` 分支不触发，走"正常半 Kelly"分支记录 `w=3.7e-17`。最终 `int(w*nav/price)=0` 不会真实下单，**行为无害但分支语义错误**（审计日志把"不下注"记成"半 Kelly 下注"）。任务书 R3.3 关心的追高等值边界则已妥善处理：[discipline_prohibition_checker.py L241-252](file:///d:/ZephyrAlpha/src/zephyr/compliance/discipline_prohibition_checker.py#L241-L252) 用 `> threshold + 1e-9 EPS`，恰达阈值不判违规，行为确定——阴性。

修复建议：Kelly 分数加 `if f_star < 1e-12: return 0.0`。

### [P2-2] PositionSizingPlan.target_qty 不做整手取整，依赖下游且契约未声明

位置：[position_sizing_engine.py L505](file:///d:/ZephyrAlpha/src/zephyr/position/core/position_sizing_engine.py#L505)

证据：`target_qty = int(weight*nav/price)` 直接截断到 1 股。整手逻辑在 [board_lot.py round_buy_qty](file:///d:/ZephyrAlpha/src/zephyr/ex_core/board_lot.py#L239-L262)（板块差异化：主板 100/科创板 200 起）与 trading_session `_calc_target_qty`（`//100`），但两者都不消费 PositionSizingPlan——若任何执行路径直接消费 plan.target_qty，将产出零股买单（A 股买入必须整手，零股只能卖）。

修复建议：sizing 引擎输出前调用 board_lot 取整，或在 CTR-POS-001 契约显式声明"target_qty 未整手，消费方必须整手"。

### [P2-3] n-1 自由度不一致：var_calculator 用 ddof=1，tail_risk_monitor.detect_jumps 用 ddof=0

位置：[var_calculator.py L346](file:///d:/ZephyrAlpha/src/zephyr/risk/core/var_calculator.py#L346) vs [tail_risk_monitor.py L530](file:///d:/ZephyrAlpha/src/zephyr/risk/core/tail_risk_monitor.py#L530)

证据：任务书 R1.5 之问——`np.std(returns)` 默认 ddof=0（总体口径）出现在跳跃检测，而 VaR/Sortino 全用 ddof=1。影响小（n=60 时差 0.8%）但同域口径不一，3σ 跳跃阈值与波动率告警在临界值两侧可能给出矛盾信号。

修复建议：统一 ddof=1 或在文档显式声明跳跃检测用总体口径的理由。

### [P2-4] VaR 极端输入边界：min_history 与置信度不联动；holding_period>1 的 √T 缩放在历史法上是近似

位置：[var_calculator.py L196-212, L443-457](file:///d:/ZephyrAlpha/src/zephyr/risk/core/var_calculator.py#L443-L457)

证据：config 允许任意 confidence∈(0,1)，但 min_history=30 固定——c=0.99 时 0.01 分位插值位置 = 0.01×29 = 0.29，几乎就是最小值本身，30 样本的 99% VaR 无统计意义。全同值序列（σ=0）无除零风险（公式无除法），NaN 有过滤——阴性。年化方向（R1.3）：`annualized_vol = std×√252` 方向正确，VaR 本身用持有期 √T 与年化因子分离，未发现乘反——阴性。历史法 √T 缩放代码注释自认近似，T=1 默认下无影响。

修复建议：`__post_init__` 增加 `min_history >= ceil(20/(1-confidence))` 类联动校验，或样本不足该置信度要求时降级告警。

### [P2-5] Sortino 的"未持仓日 0"口径：数学自洽但经济语义存疑

位置：[regime_meta_allocator.py L616-639](file:///d:/ZephyrAlpha/src/zephyr/pf_alloc/core/regime_meta_allocator.py#L616-L639)

证据：MAR_daily = 0.02/252 ≈ 7.9e-5 > 0，零收益日（未持仓）满足 `r < MAR` 计入 downside——这正是任务书 R2.1 说的"全时间线纪律"口径，代码未破坏（阴性）。但副作用：轻仓/空仓策略的 downside 样本被大量 (0-7.9e-5)² ≈ 6.3e-9 的微小项主导 → downside deviation 极小 → Sortino 虚高 → perf_score 顶格 1.5。低暴露策略在 PerformanceScore 上系统性占优，allocation 会向"没怎么下注"的策略倾斜。独立手算示例：60 日（20 个 -0.01 + 40 个 +0.005），总样本 ddof=1 口径 Sortino = -0.21；若误用 downside 样本数 ddof=1 口径则为 -0.12——两种口径差 1.76×，说明该统计量对分母选择极敏感，代码选 n-1 总样本（memo §3.4 #13 有意裁定，与 Sharpe 一致）自洽，但 n_downside≥15 门槛对"0 也算 downside"的口径过于容易满足。

修复建议：downside 样本构成中零收益日占比 >50% 时标记 `LOW_POSITION_INFLATED` 告警（复用现有 gap 监控通道），或将未持仓日剔除出 downside 分母（需与 34 号文档同步裁定口径）。

### [P2-6] 结算对账：券商记录结算日期不匹配仅 warning 不剔除

位置：[settlement_reconciliation.py L312-321](file:///d:/ZephyrAlpha/src/zephyr/trading/settlement_reconciliation.py#L312-L321)

证据：`rec.settlement_date != settlement_date` 只 log warning，记录照常进索引参与配对——跨日记录（T 日成交 T+1 结算单混入）可能与当日 Fill 错误配对产生假 MISMATCH，或顶掉正确配对。

修复建议：日期不匹配记录移入独立 `out_of_scope_records` 列表单独报告，不参与配对。

### [P2-7] 回撤恢复系数语义：回补 <50% 时 recovery_factor=1.0（不折扣），与"恢复中应更保守"直觉相反

位置：[drawdown_controller.py L618-634](file:///d:/ZephyrAlpha/src/zephyr/position/core/drawdown_controller.py#L618-L634)

证据：`recovered_pct < recovery_trigger → return 1.0`——深回撤但回补不足 50% 时恢复系数为 1（完全由风险级别主导），回补 50% 后反而跳到 `steps=int(0.5/0.25)=2 → 0.5`。**开始回补的瞬间仓位上限可能不升反降**（1.0→0.5），在"回补触发恢复"的边界产生非单调跳变。文档（ALGO_FLOW A4）与代码一致，属设计语义问题而非实现 bug。

修复建议：明确 recovery_factor 语义（"恢复中的上限"vs"未恢复不约束"），若为前者则回补 0-50% 段应给 0.25 底档而非 1.0。

---

## 四、阴性结论（审过未发现 P0/P1 的项）

| 审查点 | 结论 |
|---|---|
| R1.3 年化因子方向 | 未发现乘反。`annualized_vol = std×√252`（收益→风险方向正确），VaR 用持有期 √T 独立缩放 |
| R1.4 极端输入（σ=0 除零/NaN） | 参数法/历史法公式均无除法，全同值不崩；NaN 有过滤；样本不足抛 `InsufficientVaRHistoryError`（仅置信度联动缺失，见 P2-4） |
| R2.2 water-filling N=2 兜底 | 数学正确。手算：N=2 时 N×cap=0.8<1 → relaxed_cap=1-(N-1)×0.05=0.95，raw 1:3 → 0.25/0.75 不越界，Σ=1；两策略排序相同/相反均收敛，5 轮迭代上限内终止 |
| R2.3 shrinkage 双重折扣 | 未发现连乘。`_compute_raw_allocation` 不含 shrinkage（归一化约掉的设计被代码忠实执行），shrinkage 只在 effective_budget 层单次缩放 |
| R2.4 CRISIS floor 状态残留 | 未发现。`is_crisis` 是逐次调用的纯函数参数，floor 0.09/0.05 按调用切换，无跨调用状态 |
| R3.1 半 Kelly f*≤0 截断 | 基本正确（0 仓位输出，无负数漏出），仅盈亏平衡点浮点尾差分支语义问题（P2-1） |
| R3.3 追高等值边界 | 行为确定。严格 `>` + 1e-9 容差，恰达阈值不判违规，与"超阈值"语义一致 |
| R3.4 §2.8 漂移带口径 | 代码用绝对权重差 `abs(actual-target) > 阈值`（严格大于，等值不触发），与 memo 31 §2.8.1 ±2%/±3% 一致；"触发评估非触发执行"与 §2.8.2 成本门槛链一致 |
| R4.3 unknown 兜底桶 | 未发现静默吞差异。DriftType 5 类全部显式（3 MISMATCH + 2 MISSING），无 "other/unknown" 桶（但部分成交配对覆盖缺失是 P1-6） |
| R5.3 回撤状态机死状态 | drawdown_tracker 告警级别由当前回撤唯一决定 + 去抖（同级别不重复发射），无不可达/不可退状态（多 Protocol 仲裁缺失是 P1-7，流动性 L2/L3 不可达是 P1-9） |
| 对账冻结集累加风险 | PositionReconciler 冻结集每次全量重算（非累加），恢复一致自动解冻，`unfreeze` 后仍漂移会重冻——逻辑正确（问题仅在于未接线，P0-1） |

---

## 五、文档-代码漂移清单

| # | 文档声称 | 代码事实 | 严重度 |
|---|---|---|---|
| D1 | memo 36 §3.10 动作 4：`RiskOrchestrator → fhs_engine.enable()` 可执行；§3.9.1 独立性失败"优先选 FHS" | FHS/GARCH/should_switch_to_fhs/FHS_COOLDOWN src 零匹配；RiskOrchestrator 类不存在 | 高（P1-1） |
| D2 | memo 31 v1.25.0 修订记录："§2.2/§2.3/§2.8 全链路已落码" | dist_adj（§2.3.3）src 零匹配 | 高（P1-11） |
| D3 | memo 36 §3.2：`assess(returns, var_forecast)` + "强制校验 es_forecast >= var_forecast" | 实际签名无 var_forecast 参数，无 ES≥VaR 校验 | 高（P1-2） |
| D4 | memo 36 §3.15：`drawdown_controller.evaluate(var_breach_state=...)` + VarBreachStateMachine + ×0.8/×0.9 乘性折扣 + §3.18/§3.19 持久化 7 阶段 | evaluate() 签名无该参数；VarBreachStateMachine 类不存在；memo §3.19 末尾自认"代码差距（待施工）"但 §3.15 正文仍以已实现语气描述 | 中 |
| D5 | memo 36 §3.2 v1.4.0："POT 失败兜底 pot_fallback_historical 标记 + 连续 5 日失败→阈值 0.90→0.85" | src 无 pot_fallback 标记、无连续失败计数器、阈值为 frozen 常量 | 中（P1-3 关联） |
| D6 | memo 36 §3.7："POT 拟合 60 交易日，最差 10% ≈ 6 个样本" | 该估算隐含全负日假设；50% 负日常态下仅 3 个 exceedances，低于代码自身 ≥5 门槛 | 中（P1-3） |
| D7 | memo 36 §3.11 组件状态表：5 组件"✅ production 已建" + "2 轮 27 测试全绿" | 组件模块存在且测试绿，但无任何生产接线（P0-1）——"production"一词在文档语境=模块成熟度，在读者语境=线上生效，两种解读的落差是本漂移清单的根因 | 高 |
| D8 | memo 36 §3.5.3："渐进式减仓（YELLOW 0.5 → ORANGE 0.7 → RED 0.5 → BLACK 0.0）……天然避免赌博回本" | 序列非单调（0.7 凸起），"渐进减仓"措辞与数值矛盾 | 中（P1-4） |
| D9 | stop_loss.py 头注 ALGO_FLOW："execute_kill_switch_liquidation 为 Kill Switch 执行链路" + 35 号文档声称该链路"已施工 v1.39.0" | 生产调用方为零，仅测试调用 | 高（P0-3 关联） |

**漂移模式总结**：文档系统性地把"模块已建+测试全绿"表述为"能力已生效"，而把"接线/编排/持久化"拆成待裁定项散落在各 memo 的 §6/代码差距小节。45 项测试全绿与生产零接线并存，正是任务书"测试可能镜像错误假设"的极端形态——**测试镜像的不是错误公式，而是"已闭环"的错误前提**。

---

## 六、修复优先级建议

1. **P0-1 接线**（风控链接入 trading_session）——不修此项，其余所有算法修复都不产生实际保护；
2. **P0-3 KillSwitch 持久化 + 清算幂等**、**P0-2 apply_fill 去重 + 启动恢复**——三者共同构成"崩溃不失控"底线；
3. **P1-2/P1-3 ES 口径 + POT 门槛**——影响所有下游风险分级的输入质量；
4. **P1-5 撤单计数接线**——合规硬约束，监管侧风险；
5. 其余 P1/P2 与漂移清单 D1-D9 的文档修订可并入同一批次。

---

*审查员：Qwen3.8-Max · 2026-08-16 · 只审不改，未修改任何代码；未阅读一审报告；全部数值结论经隔离运行时独立重算。*
