---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.1.1"
date: 2026-08-08
topic: execution_broker
scope: 07_trading_decision_architecture
---

# 设计备忘·下单对接与撮合（执行层）

> 本备忘记录"信号→订单→成交"执行层的选型推理与上限定义。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [design_memo_management_spec.md](design_memo_management_spec.md)。
> 上游：[design_memo_001 §2.2](design_memo_001_multi_strategy_concurrency.md) FirmRiskAggregator 输出 firm_target_portfolio → 下单。

## 1. 背景

### 1.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统，下单通道为 miniQMT（迅投，国金证券）
- A 股 T+1 结算、不能做空、涨跌停 ±10%（ST ±5%）、100 股整数倍
- 多策略并发架构已定稿 Model A（design_memo_001）：各 StrategyBook 输出 target_portfolio → FirmRiskAggregator 求和裁剪 → firm_target_portfolio → 下单
- 执行层是数据流主动脉的末端：接收 firm_target_portfolio，分解为订单，经风控/合规/拆单后通过 miniQMT 发出，回收成交回报，更新持仓，做 TCA 成本尸检

### 1.2 核心问题
执行层要回答"信号→订单→成交"全链路的 10 个问题：下单接口对接、撮合算法、滑点模型、交易成本、订单状态机、失败重试、执行风控、集合竞价、T+1 约束、订单分解算法。每个决策都影响实盘成本与稳定性。

### 1.3 约束条件
- miniQMT 个人账户**不支持券商端 VWAP/TWAP 算法接口**（机构客户才有）→ 拆单逻辑必须系统自实现
- miniQMT 仅 Windows，必须先启动 XtMiniQmt.exe 终端，xttrader 非线程安全
- A 股 T+1：当日买入股票次日才能卖（查持仓 `can_sell_volume`），当日卖出资金可立即用于买入（T+0 资金）
- 涨跌停板流动性失效：涨停板挂单排不上、跌停板挂单卖不出
- 个人账户资金体量小：多数订单远小于 1% ADV，过度拆单反而增加成本（每笔最低佣金 5 元）
- AI 开发 → 故障隔离与幂等是生存项：断线/拒单/重复下单必须有兜底

### 1.4 现有资产盘点（施工前已实现，本备忘为其补 why 层）

> 执行层不是从零设计——miniQMT 对接、撮合、成本、滑点、Saga 均已真实实现（非 stub）。本备忘给已有实现补 why 层决策记录 + 填补 gap。

| 环节 | 模块 | path | 状态 |
|---|---|---|---|
| 下单通道 | MiniQmtBroker | `src/zephyr/ex_core/adapters/miniqmt_broker.py` | 🟦 production |
| 券商抽象 | BrokerInterface | `src/zephyr/trading/trading_contracts/broker_interface.py` | 🟦 production |
| 订单状态机 | OrderManager | `src/zephyr/ex_core/order_manager.py` | 🟦 production |
| 成交回报 | FillHandler | `src/zephyr/ex_core/fill_handler.py` | 🟦 production |
| 撮合拆单 | AlgoTradingEngine | `src/zephyr/ex_sor/core/algo_trading_engine.py` | 🟦 production |
| 交易成本 | TransactionCostOptimizer | `src/zephyr/ex_sor/services/transaction_cost_optimizer.py` | 🟦 production |
| 滑点模型 | SlippageAnalyzer | `src/zephyr/ex_sor/services/slippage_analyzer.py` | 🟦 production |
| Saga 编排 | OrderExecutionSaga | `src/zephyr/ex_core/order_execution_saga.py` | 🟦 production |
| 调仓分解 | TradingSession | `src/zephyr/ex_core/trading_session.py` | 🟦 production |
| TCA 引擎 | DefaultTcaEngine | `src/zephyr/reporting/default_tca_engine.py` | 🟦 production |
| 持仓对账 | PositionReconciler | `src/zephyr/ex_core/position_reconciler.py` | 🟦 production |
| 撮合逻辑（回测=实盘共用） | MatchingLogic | `src/zephyr/backtest/core/matching_logic.py` | 🟦 production |

## 2. 决策

### 2.1 执行层架构总览

```
firm_target_portfolio (来自 FirmRiskAggregator, design_memo_001 §2.2)
        │
        ↓
[订单分解] TradingSession._compute_order_deltas  差额下单：目标-当前=净买卖
        │   先卖后买（释放资金再买入）/ 100股整手取整 / 微调忽略
        ↓
[资金预占] ⑬ 预校验  串行扣减可用资金，卖出单预占释放额度给后续买入
        │   提交前本地拦截资金不足（避免 54 拒单推高撤单率）
        ↓
[执行风控] 订单层熔断  单票单笔≤4% + 单票≤10笔/日 + 全账户≤50笔/日
        │   （firm 层 8% 上限在上游 FirmRiskAggregator 已裁剪）
        ↓
[Saga 六步] OrderExecutionSaga  风控→信号确认→下单→成交确认→持仓更新→报告
        │   ≤5s 超时 / 补偿幂等 / 断线重连
        ↓
[撮合拆单] AlgoTradingEngine  按订单大小自适应：小单直发/中单TWAP/大单VWAP/超大单IS
        │   参与率≤5% / 单笔≤15%ADV（miniQMT 不支持券商端算法，系统自实现）
        ↓
[挂单价] ⑭ 被动档挂买一/卖一，超时触发 Make-or-Take 切主动档
        │   涨停卖单挂涨停价 / 跌停买单挂跌停价（唯一可成交价位）
        ↓
[下单通道] MiniQmtBroker  对接 xttrader（新版 xtquant 250807.1.2）
        │   T+1查持仓 / 涨跌停±10% / 100股整数倍 / 幂等INV-007 / 回测=实盘一致性预校验
        ↓
[未成交续接] ⑪ 超时Make-or-Take / PARTIAL按urgency补单 / 14:55尾盘清退
        │
        ↓
[撤单率控制] ⑫ 滚动监控降级  >12%只挂不撤 / >15%冻结告警 / 每秒≤15笔新规
        │
        ↓
[成交回报] FillHandler  fill_id幂等 / 加权均价累积 / FillSummary
        │
        ↓
[持仓更新] PositionTracker + PositionReconciler  每5min对账 / 盘后全量对账（Phase 2）
        │
        ↓
[TCA 尸检] DefaultTcaEngine + SlippageAnalyzer + TransactionCostOptimizer
        IS成本分解 / 滑点归因 / 成本分解 → 反馈拆单算法优化（Phase 1.5 规则闭环）
```

### 2.2 决策①：miniQMT 下单接口对接（按现状定型）

**决策**：复用已实现的 [MiniQmtBroker](file:///d:/ZephyrAlpha/src/zephyr/ex_core/adapters/miniqmt_broker.py)（MOD-L06-001，production），对接新版 xtquant 250807.1.2 的 xttrader API。

**已实现能力**：
- `connect/disconnect/submit_order/cancel_order/query_order/get_positions` 全套 BrokerInterface
- A 股约束校验：T+1（查持仓 `can_sell_volume`）/ 涨跌停 ±10%（ST 简化统一 10%）/ 100 股整数倍 / 停牌跳过
- 幂等下单：所有订单携带 `idempotency_key`（INV-007），重复提交返回已存在的 broker_order_id
- 断线重连：`_call_xttrader_with_reconnect` 失败自动 `_reconnect` 重试 1 次
- 线程安全：`threading.Lock` 保护所有 xttrader 调用（xttrader 非线程安全）
- 回测=实盘一致性：与 D_BACKTEST 共用 [MatchingLogic](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/matching_logic.py)，`submit_order` 内置 `pre_trade_simulate` 预成交校验
- 与 D_DATA 共用 xtquant 连接（`shared_xtquant_conn`，避免重复 connect 到 miniQMT 终端）

**xttrader 错误码映射**（代码已实现）：0=成功 / -1=连接失败 / -2=未就绪 / -3=订单号重复 / 50=涨停 / 51=跌停 / 52=数量不合法 / 53=价格不合法 / 54=资金不足 / 55=持仓不足。

**为何不再造**：MiniQmtBroker 已 production 且通过测试，重复造轮子违反 AI-dev 归因清晰度原则。本备忘只记录 why，不改 what。

### 2.3 决策②：撮合算法——按订单大小自适应

**决策**：复用 [AlgoTradingEngine](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/core/algo_trading_engine.py)（MOD-XS-005）的 6 种算法 + [AlgoParamOptimizer](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/core/algo_trading_engine.py) 自适应选择，默认选择规则按**订单占 ADV 比例**分档：

| 订单大小 | 占 ADV | 默认算法 | 理由 |
|---|---|---|---|
| 小单 | <1% | 整单限价直发（不拆） | 冲击可忽略，拆了反增成本（每笔最低佣金 5 元） |
| 中单 | 1-5% | TWAP 等量切片 | 均匀执行，被动挂单，冲击可控 |
| 大单 | 5-15% | VWAP 按日内量能分布 | 契合 A 股日内成交量分布（开盘20%/上午25%/午盘10%/尾盘45%），隐藏在市场自然成交量里 |
| 超大单 | >15% | IS（Almgren-Chriss 风险厌恶轨迹） | 平衡冲击成本与时机风险，urgency 驱动前/后置加载 |

**硬约束**（代码已实现）：
- 参与率 ≤5%（证监会程序化交易规定，§10.1 Hard Block）
- 单笔订单 ≤15% ADV（Almgren-Chriss 模型上限，§13.1，超则 `OrderTooLargeError` 否决+上游拆分）
- 切片数量和 == 订单总量（Decimal 守恒不变量）

**为何自适应而非统一算法**：
- 个人账户小资金多数订单 <1% ADV，统一 TWAP/VWAP 会让小单也拆，增加下单次数和成本
- 统一不拆单则浪费了已实现的拆单能力，大单（如打板集中买入）有冲击风险
- 自适应复用现有 `AlgoParamOptimizer` 逻辑，每档用最合适的算法，既简单又保留大单拆单能力

**6 种算法用途**（代码已实现，注册表模式）：TWAP（等量切片被动挂单）/ VWAP（按日内量能分布）/ ICEBERG（小额显示量隐藏大单）/ POV（参与率≤5%）/ IS（AC 风险厌恶轨迹）/ ALT（激进对手价吃单，游资"狙击"量化版）。

### 2.4 决策③：滑点模型——DECISION 决策价为主基准

**决策**：回测与实盘 TCA 统一用 **DECISION（决策价）** 作为主滑点基准。

**基准定义**（[SlippageAnalyzer](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/services/slippage_analyzer.py) 已支持 5 基准）：
- DECISION = 信号生成时刻价格（主基准）
- ARRIVAL = 下单到达时刻价格（辅助，隔离执行质量）
- VWAP / TWAP / PREV_CLOSE（辅助对比）

**为何选 DECISION**：
- DECISION 衡量"信号→成交"全链路总损耗，是 Implementation Shortfall（IS）的核心指标
- 与 [DefaultTcaEngine](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_tca_engine.py) 的 IS 成本分解（时机+冲击+滑点+佣金）口径一致
- 回测最保守（含信号延迟成本），实盘不会比回测差
- 回测=实盘口径一致：回测用 DECISION 算滑点，实盘 TCA 也用 DECISION，双向可追溯

**滑点符号约定**（代码已实现）：BUY 正=买贵了=成本 / SELL 正=卖便宜了=成本。

**归因模型**（代码已实现三因子+残差）：market_impact（平方根冲击模型，`coeff × √participation × volatility_bps`）+ timing（执行期间价格漂移）+ spread（half-spread）+ residual（残差吸收模型误差）。

**预测模型**：[SquareRootImpactPredictor](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/services/slippage_analyzer.py) 平方根法则（Almgren-Chriss 简化版），`impact_bps = coeff × √participation × vol_bps + half_spread`。

**理论依据**：平方根形式不是经验拟合，而是**无动态套利约束（no-dynamic-arbitrage）下唯一自洽的冲击形式**（Gatheral 2010）。这一约束保证了"冲击的衰减函数不能允许通过组合交易构造无风险套利"，平方根律是满足该约束的存活形式。这为模型可信度提供了理论地基，而非仅依赖实证拟合。MVP 用平方根律（瞬时冲击）足够；Phase 2 可上推 Bouchaud Propagator 模型（描述冲击的时间衰减结构，今天的交易影响未来价格）。

### 2.5 决策④：交易成本模型（佣金万0.854 + 2023 法定费率）

**决策**：复用 [TransactionCostOptimizer](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/services/transaction_cost_optimizer.py)（MOD-EX_SOR_EXT-003），费率按用户实盘账户校准。

| 成本项 | 费率 | 方向 | 性质 | 来源 |
|---|---|---|---|---|
| 佣金 | **0.854 bps（万0.854）**，最低 5 元 | 双边 | 可谈 | 用户国金 miniQMT 账户实盘费率 |
| 印花税 | 5 bps（0.05%） | 卖方单边 | 法定 | 2023-08-28 由 0.1% 降至 0.05% |
| 过户费 | 0.1 bps（0.001%） | 双边 | 法定 | 2022-04-29 由 0.002% 降至 0.001% |
| 监管费 | 0.2 bps（0.002%） | 双边 | 法定 | 证监会规费 |
| 冲击成本 | 隐性 | — | 估计 | LinearImpactEstimator（Kyle's lambda 简化） |
| 机会成本 | 隐性 | — | 估计 | 未成交部分 × 决策价 × 0.1% |

**佣金最低收费影响**：万0.854 费率下，5 元最低佣金对应成交金额 ≈ 5.85 万元。**单笔成交 <5.85 万都触发最低 5 元佣金**——个人账户小资金多数订单走最低收费，此时佣金成本占比反而高于费率隐含值。拆单需谨慎（拆得越碎，最低佣金触发越多）。

**已修复**（v1.0.0 施工，commit 015826ae）：[FeeSchedule](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/services/transaction_cost_optimizer.py) 默认已更新为 `Decimal("0.854")`（万0.854）。实盘开户后需对照交割单二次校准。

### 2.6 决策⑤：订单状态机（7 态 + 先卖后买）

**决策**：复用 [OrderManager](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py) 7 态状态机。

**7 态机**（代码已实现）：
```
PENDING → {SUBMITTED, CANCELLED}
SUBMITTED → {PARTIAL, FILLED, CANCELLED, REJECTED}
PARTIAL → {FILLED, CANCELLED, REJECTED}
FILLED / CANCELLED / REJECTED → 终态
EXPIRED → 终态
```

**状态转换校验**：`VALID_TRANSITIONS` 字典校验非法转换，违规抛 `ValueError`。[FillHandler](file:///d:/ZephyrAlpha/src/zephyr/ex_core/fill_handler.py) 的 `_FILL_TRANSITIONS` 与其对齐（但更宽容——不阻断并发填充导致的非法转换，仅 warn）。

**执行顺序规则——先卖后买**：
- 订单分解时，卖出订单优先于买入订单提交
- 理由：A 股 T+0 资金——卖出回笼的资金可立即用于买入。先卖后买释放资金，避免买入时资金不足（error_code=54）
- 已修复（v1.0.0 施工，commit 015826ae）：[TradingSession._validate_and_submit](file:///d:/ZephyrAlpha/src/zephyr/ex_core/trading_session.py) 已按先 SELL 后 BUY 排序（`sorted(deltas, key=lambda o: 0 if o.side is OrderSide.SELL else 1)`）

**状态码映射**（[MiniQmtBroker._map_xt_status](file:///d:/ZephyrAlpha/src/zephyr/ex_core/adapters/miniqmt_broker.py) 已实现）：xttrader 48=UNKNOWN→PENDING / 49=PENDING→SUBMITTED / 50=PARTIAL / 52=FILLED / 53=CANCELLED / 55=REJECTED / 56=EXPIRED。

### 2.7 决策⑥：失败重试与异常——分类处理

**决策**：三层异常处理（断线重连 + Saga 补偿 + 拒单分类处理）。

**层1 断线重连**（[MiniQmtBroker._call_xttrader_with_reconnect](file:///d:/ZephyrAlpha/src/zephyr/ex_core/adapters/miniqmt_broker.py)，已实现）：
- xttrader 调用失败 → 自动 `_reconnect` 重连 1 次 → 重试
- 连接失败带重试：`_do_connect_with_retry` 最多 3 次，间隔 1 秒

**层2 Saga 补偿**（[OrderExecutionSaga](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_execution_saga.py)，已实现）：
- 六步（风控→信号→下单→成交→持仓→报告）任一步失败自动补偿
- 步骤3（下单）失败 → 撤单（幂等：已成交则忽略）
- 步骤4（成交）超时 → 撤单（步骤3补偿）
- 步骤5（持仓）失败 → 持仓回滚（反向 apply_fill，幂等）
- ≤5s 超时硬约束 / 补偿幂等 / Redis Stream 状态持久化

**层3 拒单（REJECTED）分类处理**（部分实现：分类映射 + `classify_rejection` + `_handle_rejection` 日志已实现，RETRY/冻结/对账动作待 Saga 接管，见 §6.1 gap 4）：

| 拒单原因 | error_code | 处理策略 | 理由 |
|---|---|---|---|
| 涨停/跌停 | 50/51 | 不重试，直接放弃 | 涨跌停板排不上，重试无意义且浪费频次 |
| 资金不足 | 54 | 不重试，告警+冻结该策略新开仓 | 账户级问题，重试不会变有钱 |
| 持仓不足 | 55 | 不重试，告警+持仓对账 | T+1 锁定或持仓数据不一致，需对账 |
| 数量不合法 | 52 | 不重试，告警（代码 bug） | 100 股整数倍校验已在 submit_order 前做，到这层是 bug |
| 价格不合法 | 53 | 修正价格重试 1 次 | 可能是涨跌停价边界 1 分钱误差，修正后重试 |
| 连接类错误 | -1 | 重连后重试 1 次 | 已被层1断线重连覆盖，兜底再试 1 次 |
| 订单号重复 | -3 | 返回已存在的 broker_order_id（幂等） | 幂等机制已处理 |

**原则**：涨跌停/资金/持仓类拒单不重试（重试无意义），价格/连接类拒单重试 1 次（可恢复）。宁可放弃不可盲目重试，避免撤单率超标（BM-EXE-04 撤单率 ≤15%）。

### 2.8 决策⑦：执行风控——订单层熔断

**决策**：在 firm 层风控（单票 8% 上限，design_memo_001 §2.2）之上，加订单层熔断防乌龙指与过度交易。

| 熔断项 | 阈值 | 触发动作 | 理由 |
|---|---|---|---|
| 单票单笔量 | ≤4% 账户市值 | 超限拒绝下单 | 比 firm 层 8% 低一半，留 2 倍缓冲（可分 2 笔建仓到位） |
| 单票下单频次 | ≤10 笔/日 | 超限冻结该票当日新下单 | 防同一票疯狂下单（拆单算法正常 5-10 片够用） |
| 全账户下单频次 | ≤50 笔/日 | 超限冻结全账户新下单 | 防程序失控（5 策略 × 10 笔 = 50，够用） |

**对齐监管约束**（battle_map_10 BM-EXE-04）：
- 参与率 ≤5%（证监会程序化交易规定）
- 撤单率 ≤15%（2026.4.7 新规）
- 报单停留时间 ≥50μs

**为何 4% 而非 8%**：单笔 8% = firm 层上限，一笔到位冲击成本高且无缓冲；4% 留 2 倍缓冲是行业惯例（机构一般单笔 ≤2-5%），可分 2 笔建仓降低冲击。

**为何不省略订单层熔断**：2013 光大乌龙指就是没有订单层单笔量+频次上限，一笔异常订单打穿风控。订单层熔断是账户级安全网，不可省。

### 2.9 决策⑧：集合竞价——MVP 仅连续竞价

**决策**：MVP 阶段仅参与连续竞价（9:30-11:30 + 13:00-14:57），不碰集合竞价。

**A 股交易时段规则**（上交所 2026 修订交易规则 §3.3.2）：

| 时段 | 时间 | 机制 | 撤单 |
|---|---|---|---|
| 开盘集合竞价（自由申报期） | 9:15-9:20 | 收集委托，9:25 撮合 | 可撤单 |
| 开盘集合竞价（真实博弈期） | 9:20-9:25 | 收集委托，9:25 撮合 | **不可撤单** |
| 静默期 | 9:25-9:30 | 主机不接收任何申报 | 不可挂不可撤 |
| 连续竞价（上午） | 9:30-11:30 | 逐笔撮合 | 可撤单 |
| 午休 | 11:30-13:00 | — | — |
| 连续竞价（下午） | 13:00-14:57 | 逐笔撮合 | 可撤单 |
| 收盘集合竞价 | 14:57-15:00 | 收集委托，15:00 撮合 | **不可撤单** |

> **撤单规则澄清**：9:20-9:25 不可撤单（非 9:25-9:30）。9:25-9:30 是静默期（既不能挂也不能撤），与"不可撤单"是两个概念。上交所 2026 修订规则 §3.3.2 原文："9:20至9:25的开盘集合竞价阶段、14:57至15:00的收盘集合竞价阶段，本所交易主机不接受撤单申报"。

**为何 MVP 不碰集合竞价**：
- 集合竞价价格不可控（下单时不知道最终成交价），价差大风险高
- 开盘集合竞价流动性不足，价差大，容易买贵卖便宜
- 对 T+1 策略意义有限（当天买了不能卖，不如连续竞价灵活）
- MVP 先把连续竞价做扎实，集合竞价是优化项

**代码 gap**：[TradingSession](file:///d:/ZephyrAlpha/src/zephyr/ex_core/trading_session.py) 当前只做连续竞价，集合竞价订单类型（限价单+市价单规则不同）未实现，待第二阶段。

### 2.10 决策⑨：T+1 约束（按现状定型）

**决策**：复用 [MiniQmtBroker._check_t_plus_1](file:///d:/ZephyrAlpha/src/zephyr/ex_core/adapters/miniqmt_broker.py) 已实现的 T+1 校验。

**A 股 T+1 规则**：
- **T+1 股票**：当日买入的股票，次日才能卖出。卖出时查持仓 `can_sell_volume`（可用卖出数量，已扣除当日买入）
- **T+0 资金**：当日卖出回笼的资金，可立即用于当日买入

**已实现**：`_check_t_plus_1` 在卖出时调用 `xttrader.query_stock_positions` 查 `can_sell_volume`（fallback `avail_volume`/`available`），可用不足则拒单（error_code=-2）。

**协同**：先卖后买顺序（决策⑤）正是为了利用 T+0 资金——卖出释放的资金立即用于买入。

### 2.11 决策⑩：firm_target_portfolio → 订单分解（差额下单）

**决策**：复用 [TradingSession._compute_order_deltas](file:///d:/ZephyrAlpha/src/zephyr/ex_core/trading_session.py) 差额下单算法。

**算法**：
```
total_asset = cash + total_market_value
for symbol, weight in firm_target_portfolio:
    target_qty = floor(total_asset × weight / price, 100股)  # 向下取整到整手
    delta = target_qty - current_qty
    if abs(delta) >= 100:  # 忽略 <100 股微调
        order = BUY if delta > 0 else SELL
# 持仓中但不在目标权重 → 全部卖出（清仓）
```

**执行顺序**（决策⑤）：先 SELL 后 BUY 排序——卖出释放资金（T+0）再买入，避免资金不足。

**整手处理**：向下取整到 100 股整手，不足 100 股的微调忽略（避免碎片化订单触发最低佣金）。

**幂等**：每个订单携带 `idempotency_key`（INV-007），重复调仓不会重复下单。

### 2.12 决策⑪：未成交/部分成交订单的续接处理（Open Order Resolution）

**决策**：对提交后未成交或部分成交的订单，按 urgency 分档续接，而非统一挂死或统一撤单。

> v1.0.0 的状态机只定义了 PARTIAL 的合法后继态，未定义"剩余量怎么决策"。这是实盘"信号发了但没成交"的直接落地点，缺失会导致订单悬挂、持仓与目标长期偏离。v1.1.0 补全。

**续接算法**（待实现，本备忘定型规则）：

| 订单剩余状态 | 触发条件 | 处理策略 | 理由 |
|---|---|---|---|
| SUBMITTED 未成交 | 挂单 ≤ T 秒（默认 30s） | 继续等待 | 给被动挂单充分成交时间，避免频繁撤单推高撤单率 |
| SUBMITTED 未成交 | 挂单 > T 秒 | **Make-or-Take 切换**：撤单 → 对手价主动吃单（剩余量） | 被动挂单超时未成交，转主动兜底，保证成交确定性 |
| PARTIAL 剩余 <100 股 | 任意 | 忽略，订单转 CANCELLED | 避免碎片化订单触发最低佣金（5 元） |
| PARTIAL 剩余 ≥100 股 | urgency=高（打板） | Make-or-Take 切换补单 | 打板需快速成交，不可久等 |
| PARTIAL 剩余 ≥100 股 | urgency=低（多因子） | 留单等成交，下轮调仓再校准 | 多因子换手率低（3-5 天），不必急于补单 |
| 任意非终态 | 14:55 收盘前 | **尾盘清退**：转入收盘集合竞价或放弃（MVP 选放弃→撤单） | 避免隔夜挂单（miniQMT 不支持隔夜挂单，且 T+1 资金/持仓需盘后清算） |

**Make-or-Take 切换**（介于纯被动 TWAP 与纯主动 ALT 之间的中间档）：
```
挂限价单(买一/卖一) → 等 T 秒
  ├─ 成交 → 完成
  └─ 未成交 → 撤单 + 对手价主动吃单(剩余量)  # 兜底
```
平衡成本（被动挂单省 spread）与成交确定性（主动兜底防漏单）。对打板策略必需（纯被动会错过龙头）。

**为何不统一挂死等成交**：A 股限价单可能因价格远离挂单价而长期不成交，挂死会导致持仓与目标长期偏离，下轮调仓时重复下单（虽有幂等保护，但占用资金预占额度）。

**为何不统一撤单转市价**：市价单冲击成本高，且 A 股市价单有"最优五档"限制，大单可能成交到极差价位。

### 2.13 决策⑫：撤单流程与撤单率控制（Cancel Flow + Rate Limiting）

**决策**：主动撤单按场景触发 + 撤单率滚动监控降级，确保不触犯 2026.4.7 程序化交易新规。

> v1.0.0 §2.8 提了撤单率 ≤15% 约束，但撤单触发逻辑和撤单率控制算法未定义。这是合规生存项。

**2026 程序化交易新规硬约束**（2026.4.7 生效，7.7 全面执行）：
- **每秒报单 ≤15 笔**（高频认定标准从 300 笔骤降至 15 笔）
- **每秒撤单 ≤15 笔**
- **单日撤单率 ≤15%**
- **报单停留时间 ≥50μs**

> 这直接决定拆单切片间隔下限：若每秒最多 15 笔，则切片间隔 ≥ 1000ms/15 ≈ 67ms（实际应远大于此，留合规缓冲）。MVP 切片间隔默认 ≥10s，远超下限。

**主动撤单触发场景**（待实现）：

| 触发条件 | 动作 | 理由 |
|---|---|---|
| 价格远离挂单价 > X tick（默认 3 tick） | 撤单重挂 | 市场价格已偏离，原挂单价无意义，重挂到新盘口 |
| 挂单超时（决策⑪ T 秒） | 撤单转 Make-or-Take | 见决策⑪ |
| 策略信号反转 | 撤单 | 目标权重已变，原订单方向错误 |
| 资金被更高优先级订单占用 | 撤单重排 | 先卖后买优先级调整 |

**撤单率滚动监控与降级**（待实现）：
```
maintain rolling_window = 最近 500 笔报单的成交/撤单记录
rolling_cancel_rate = 撤单数 / 总报单数

if rolling_cancel_rate > 12%:   # 预警线（阈值 - 3% 缓冲）
    降级为 "只挂不撤" 模式：挂单后禁止撤单重挂，必须等成交或收盘
if rolling_cancel_rate > 15%:   # 硬线
    冻结全账户新下单，告警人工介入
```
**为何 12% 预警而非等到 15%**：滚动窗口有滞后性，等看到 15% 时实际可能已超。留 3% 缓冲是合规安全垫。

**为何不省略撤单率控制**：2026 新规下撤单率超限会被交易所标记为异常交易，轻则警告重则限制交易。这是合规生存项，不可省。

### 2.14 决策⑬：资金预占与预校验（Pre-Trade Cash Reservation）

**决策**：下单前做资金预占，避免并发提交多个 BUY 单时资金不足（error_code=54）。

> v1.0.0 决策⑤讲了"先卖后买释放资金"，但下单前如何预判资金足够未定义。先卖后买是粗粒度排序，并发提交多个 BUY 单时，若不做资金预扣，可能都通过预校验但实际提交时资金不足。

**资金预占算法**（待实现）：
```
available_cash = broker.get_positions().cash
pending_release = 0   # 待成交卖出单的净回笼资金

for order in sorted_deltas:  # 先卖后买顺序
    if order.side == SELL:
        预估回笼 = order.quantity × price × (1 - 卖出费率)
        pending_release += 预估回笼
        预占 = 0   # 卖出不占资金
    else:  # BUY
        预估占用 = order.quantity × price × (1 + 买入费率)
        预占 = 预估占用

    if 预占 > available_cash + pending_release:
        拒绝下单（资金不足，归入 blocked_orders）
        # 注意：不提交给 broker（避免 54 拒单），直接本地拦截
    else:
        available_cash -= 预占   # 立即扣减预占额度
        submit(order)
```

**与拒单分类（决策⑥）的协同**：
- error_code=54（资金不足）是"已提交给 broker 后被拒"——说明预占机制失效或 broker 端有其他扣款
- 本决策的预校验是"提交前本地拦截"——更早一层，避免无意义的 54 拒单（54 拒单会推高报单数和撤单率）
- 两者是防御纵深：预校验拦截 99%，54 拒单兜底 1%（如 broker 端费率变动、其他程序占用资金）

**为何不依赖 broker 端资金校验**：miniQMT 的 broker 端校验是提交时同步检查，但并发提交多个订单时，每个订单提交时都看到"资金够"，但累计起来不够。本地预占是串行扣减，保证累计不超。

### 2.15 决策⑭：挂单价算法（Pegging / Pricing Logic）

**决策**：MVP 默认被动档挂单——买单挂买一价、卖单挂卖一价（不跨价，避免主动吃单成本），超时未成交触发决策⑪的 Make-or-Take 切换。

> v1.0.0 讲了拆单算法（TWAP/VWAP 切片），但每个子单的具体挂单价未定义。这是 TWAP/VWAP 落地的最后一公里。

**挂单价规则**（待实现）：

| 订单类型 | 默认挂单价 | 理由 |
|---|---|---|
| 被动买单 | 买一价（bid） | 不跨价，省 spread，排队等成交 |
| 被动卖单 | 卖一价（ask） | 不跨价，省 spread，排队等成交 |
| 主动买单（Make-or-Take 兜底） | 卖一价（ask） | 跨价吃单，保证成交 |
| 主动卖单（Make-or-Take 兜底） | 买一价（bid） | 跨价吃单，保证成交 |
| 涨停板卖单 | 涨停价 | 唯一可能成交的价位（排队） |
| 跌停板买单 | 跌停价 | 唯一可能成交的价位（排队） |

**为何默认被动档**：
- 个人账户小资金多数订单 <1% ADV，被动挂单排队足够成交
- 被动档省 spread（A 股 spread 约 1-2 tick，被动档比主动档省 1-2 tick 成本）
- 主动吃单只作兜底（Make-or-Take），不作为默认

**为何不挂 mid 价**：A 股最小变动单位 0.01 元，mid 价常落在两个 tick 之间，无法挂单；且挂 mid 等于既不占买一也不占卖一，成交概率更低。

**为何不挂对手价（主动档）作为默认**：主动档跨价吃单，每笔都付 spread，小单累积成本高。仅 urgency 高（打板）或超时兜底时用。

**Phase 1.5 改进项**：peg 到盘口（盘口移动时自动撤单重挂跟随），需实时盘口数据（miniQMT `xtdata.get_full_tick` 支持）。MVP 先用静态挂单（挂出后不动，超时才撤），简单可靠。

## 3. 考虑过的替代方案（拒绝理由）

### 3.1 撮合：统一 TWAP —— 拒绝
- **拒绝理由**：小单也拆，增加下单次数和成本（每笔最低佣金 5 元）；不契合 A 股日内量能节奏
- 自适应分档已覆盖 TWAP 适用场景（中单 1-5% ADV），无需全局统一

### 3.2 撮合：不拆单整单限价直发 —— 拒绝
- **拒绝理由**：浪费已实现的 AlgoTradingEngine 6 种算法；大单（如打板集中买入）有冲击成本风险
- 自适应分档已覆盖直发适用场景（小单 <1% ADV），无需全局不拆

### 3.3 集合竞价：参与开盘+收盘 —— 拒绝（MVP 延后）
- **拒绝理由**：集合竞价价格不可控，价差大风险高；MVP 阶段先把连续竞价做扎实
- **重评条件**：首批策略跑 3 个月有 track record 后，按策略类型差异化评估（打板可参与开盘集合竞价抢龙头）

### 3.4 滑点：ARRIVAL 到达价基准 —— 拒绝
- **拒绝理由**：只算执行环节成本，不含信号延迟，回测偏乐观，实盘可能比回测差
- DECISION 基准衡量全链路成本，回测最保守，已选为主基准

### 3.5 滑点：VWAP 基准 —— 拒绝
- **拒绝理由**：A 股个人账户小单 vs VWAP 意义有限（小单成交价本来就接近 VWAP）；VWAP 要等全天收盘才算得出，盘中不知道
- 保留为辅助对比基准（SlippageAnalyzer 已支持），不作主基准

### 3.6 订单层熔断：不设，全依赖 firm 层 —— 拒绝
- **拒绝理由**：2013 光大乌龙指教训——没有订单层单笔量+频次上限，一笔异常订单可打穿风控
- 订单层熔断是账户级安全网，不可省

### 3.7 拒单：统一重试 3 次 —— 拒绝
- **拒绝理由**：涨跌停板重试 3 次也无用，还浪费频次、推高撤单率（违反 ≤15% 监管约束）
- 分类处理：可恢复（价格/连接）重试 1 次，不可恢复（涨跌停/资金/持仓）直接放弃

### 3.8 未成交续接：统一挂死等成交 —— 拒绝
- **拒绝理由**：A 股限价单可能因价格远离挂单价长期不成交，挂死导致持仓与目标长期偏离，下轮调仓重复下单
- 按 urgency 分档续接（决策⑪）：超时 Make-or-Take、PARTIAL 按 urgency 补单、14:55 尾盘清退

### 3.9 未成交续接：统一撤单转市价 —— 拒绝
- **拒绝理由**：市价单冲击成本高，A 股市价单有"最优五档"限制，大单可能成交到极差价位
- Make-or-Take 平衡：被动挂单优先（省 spread），超时才转对手价主动吃单（保证成交）

### 3.10 挂单价：默认主动档对手价 —— 拒绝
- **拒绝理由**：主动档每笔跨价吃单付 spread，小单累积成本高；个人账户小资金被动档排队足够成交
- 默认被动档（买一/卖一），主动档仅作 Make-or-Take 兜底或 urgency 高（打板）时用

### 3.11 撤单率：不设控制全靠 broker 端 —— 拒绝
- **拒绝理由**：2026.4.7 新规下撤单率超限被交易所标记异常交易，轻则警告重则限制交易
- 滚动监控降级（决策⑫）：>12% 只挂不撤、>15% 冻结告警，合规生存项不可省

## 4. 上限定义（Ceiling）

### 4.1 系统上限
- **单 broker**：miniQMT（国金证券）。多 broker 路由（[OptimalOrderRouter](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/core/optimal_order_router.py) XS-01）已实现但 MVP 不启用
- **6 种撮合算法**：TWAP/VWAP/ICEBERG/POV/IS/ALT，注册表模式可扩展
- **7 态订单状态机**：PENDING/SUBMITTED/PARTIAL/FILLED/CANCELLED/REJECTED/EXPIRED
- **订单层熔断**：单票单笔 4% / 单票 10 笔日 / 全账户 50 笔日
- **撤单率控制**：滚动 500 笔窗口，>12% 只挂不撤 / >15% 冻结告警；每秒报单/撤单 ≤15 笔（2026 新规）
- **挂单价**：默认被动档（买一/卖一），Make-or-Take 超时切主动档
- **资金预占**：串行扣减，提交前本地拦截资金不足
- **连续竞价时段**：9:30-11:30 + 13:00-14:57（MVP 不含集合竞价）

### 4.2 演进路径
- **第一阶段（MVP，立即施工）**：连续竞价 + 自适应撮合 + DECISION 滑点 + 万0.854 佣金 + 订单层熔断 + 拒单分类处理 + 未成交续接 + 撤单率控制 + 资金预占 + 被动档挂单价。复用全部已实现 production 模块，补代码 gap（见 §6.1）
- **Phase 1.5（首批策略 track record 1-3 个月）**：① 自适应参与率 POV（盘口深度/价差/波动率动态调参与率，取代固定 5%）② peg 到盘口（盘口移动自动撤单重挂跟随）③ TCA 规则闭环（滑点持续超阈值→自动调高拆单分档阈值）④ 冲击模型 coeff 校准（用实盘 TCA 数据回归拟合 SquareRootImpactPredictor 的 coeff，为 Phase 2 RL 地基）
- **第二阶段（首批策略 track record 3 个月后）**：上加集合竞价（按策略差异化）+ 算法参数 RL 优化器（需 coeff 已校准 + 足够 TCA 历史数据；2026 研究表明成本模型准确性对 RL 算法选择有决定性影响——MACE 研究中 AC 冲击模型下 TD3 最优而固定成本下 PPO 最优）
- **第三阶段（AUM 增长或 miniQMT 容量不足时）**：启用多 broker 路由 + ICEBERG 隐藏大单 + Bouchaud Propagator 模型（冲击时间衰减结构，超越平方根律瞬时冲击）

### 4.3 为何这是上限而非妥协
- 个人账户资金体量小，多数订单 <1% ADV，6 种算法 + 自适应已覆盖全场景
- miniQMT 个人账户不支持券商端算法，系统自实现拆单已是个人系统能力上限
- 集合竞价是优化项非必需项，MVP 连续竞价足以验证策略 alpha
- 多 broker 路由是机构需求，个人单账户单 broker 足够

## 5. 待裁定（暂缓）

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| 集合竞价参与 | MVP 先做连续竞价；集合竞价价格不可控风险高 | 首批策略 track record 3 个月后，按策略差异化评估 |
| 多 broker 路由 | 个人单账户单 broker 够用；XS-01 已实现但未启用 | AUM 增长或 miniQMT 容量不足 |
| 算法参数 RL 优化器 | 需足够 TCA 历史数据训练；Phase 1 规则驱动已够用 | 累积 6 个月实盘 TCA 数据 |
| Pre-Trade 合规检查（BM-EXE-04） | wash trade/spoofing 检测需多账户数据；个人单账户无自交易风险 | 多账户或合规要求升级 |
| ST 股 ±5% 涨跌停差异化 | 代码当前简化统一 10%；ST 股识别需数据源 | 实盘涉及 ST 股时 |
| 盘后全量对账（EOD Reconciliation） | MVP 盘中每5min对账够用；盘后三方核对流程待定 | 实盘上线后，T+1 结算确认需求 |
| peg 到盘口（动态挂单跟随） | MVP 静态挂单够用；动态跟随需实时盘口数据 + 撤单率预算 | Phase 1.5，撤单率控制稳定后 |

## 6. 待定问题（需人决策/代码 gap）

### 6.1 代码 gap

**v1.0.0 gap（4/5 已闭合 + 1 部分实现，commit 015826ae）**：
1. ✅ **OrderManager.VALID_TRANSITIONS 补 EXPIRED**：[OrderManager](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py) 已补 `OrderStatus.EXPIRED: set()` 及相关转换。
2. ✅ **FeeSchedule 佣金默认值**：[TransactionCostOptimizer](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/services/transaction_cost_optimizer.py) 已更新为 `Decimal("0.854")`（万0.854）。
3. ✅ **TradingSession 先卖后买顺序**：[TradingSession._validate_and_submit](file:///d:/ZephyrAlpha/src/zephyr/ex_core/trading_session.py) 已改为先 SELL 后 BUY 排序。
4. ⚠️ **拒单分类处理实现**（部分）：[OrderManager](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py) 已实现 `RejectionAction` 枚举 + `classify_rejection` 静态方法（8 错误码映射）+ [TradingSession._handle_rejection](file:///d:/ZephyrAlpha/src/zephyr/ex_core/trading_session.py) 分类日志。**待补全**：RETRY_ONCE/ALERT_FREEZE/ALERT_RECONCILE 的实际动作（重试 1 次 / 冻结策略新开仓 / 触发持仓对账）待上层 OrderExecutionSaga 接管——当前 MVP 仅记录日志 + 归入 `_blocked_orders`。
5. ✅ **订单层熔断实现**：[TradingSession](file:///d:/ZephyrAlpha/src/zephyr/ex_core/trading_session.py) 已实现 `_is_blocked_by_circuit_breaker`（单票单笔4%/单票10笔日/全账户50笔日）。

**v1.1.0 gap（待施工，本备忘定型规则）**：
6. **未成交续接实现**（决策⑪）：Make-or-Take 超时切换（被动挂单 T 秒未成交→撤单转对手价）、PARTIAL 按 urgency 补单、14:55 尾盘清退。待在 [OrderExecutionSaga](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_execution_saga.py) 或新建 OpenOrderResolver 实现。
7. **撤单率控制实现**（决策⑫）：滚动 500 笔窗口监控、>12% 只挂不撤降级、>15% 冻结告警、主动撤单触发场景（价格远离/超时/信号反转）。待在 [OrderManager](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py) 或新建 CancelRateGuard 实现。
8. **资金预占实现**（决策⑬）：串行扣减可用资金、卖出单预占释放额度、提交前本地拦截资金不足。待在 [TradingSession._validate_and_submit](file:///d:/ZephyrAlpha/src/zephyr/ex_core/trading_session.py) 实现。
9. **挂单价算法实现**（决策⑭）：被动档买一/卖一、主动档对手价、涨停卖单挂涨停价/跌停买单挂跌停价。待在 [AlgoTradingEngine](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/core/algo_trading_engine.py) 或新建 PricingPolicy 实现。
10. **盘后全量对账实现**（Phase 2）：券商对账单 vs 系统持仓 vs 资金三方核对、T+1 可用更新、未成交订单日终转 EXPIRED。待在 [PositionReconciler](file:///d:/ZephyrAlpha/src/zephyr/ex_core/position_reconciler.py) 扩展。

### 6.2 开放问题
- **佣金费率实盘校准**：万0.854 为用户口头提供，实盘开户后需对照交割单二次校准
- **集合竞价差异化规则**：第二阶段评估时，需定打板策略是否参与开盘集合竞价、卖出流是否走收盘集合竞价
- **与 G19/G20 接口对齐**：执行层接收 firm_target_portfolio，上游 G19 买入流/G20 卖出流定型后需对齐接口契约（本备忘先定执行层 spec，不依赖 G19/G20 细节）
- **Make-or-Take 超时 T 的初始值**：决策⑪ 默认 30s，实盘需按标的流动性校准（高流动性票可降到 10s，低流动性票可升到 60s）
- **撤单率滚动窗口大小**：决策⑫ 默认 500 笔，实盘需校准（窗口太小则敏感易误降级，太大则滞后失去预警作用）
- **资金预占费率假设**：决策⑬ 预估占用/回笼用的费率需与 broker 端实际扣款一致，否则预占额度会偏

## 7. 引用

### 7.1 相关设计备忘
- [design_memo_001 §2.2](design_memo_001_multi_strategy_concurrency.md) FirmRiskAggregator 输出 firm_target_portfolio → 下单（上游契约）
- [design_memo_001 §2.5](design_memo_001_multi_strategy_concurrency.md) 回撤 Protocol（账户级风控，与订单层熔断协同）
- [discussion_000 §3 G22](discussion_000_discussion_framework.md) 下单对接与撮合主题组定义
- [design_memo_management_spec §4.3](design_memo_management_spec.md) 设计备忘推荐章节结构

### 7.2 相关作战地图
- [battle_map_10_execution.md](../battle_map/battle_map_10_execution.md) 执行阶段 6 环节：
  - BM-EXE-01 自适应风控审批（production，C-004）
  - BM-EXE-02 交易执行（production，C-002 / MOD-XS-002 broker_adapter）
  - BM-EXE-03 执行质量 TCA（production，MOD-L07-001）
  - BM-EXE-04 Pre-Trade 合规检查（design，MOD-EX-024/007 planned）
  - BM-EXE-05 智能订单路由与拆单（design，MOD-EX-014 planned / MOD-XS-005 stable）
  - BM-EXE-06 成交回报处理与持仓更新（design，MOD-EX-008 planned / MOD-EX-001 stable）

### 7.3 depgraph 模块（用 path/blueprint_id 引用，非 node_id）

| 模块 | blueprint_id | path | 域 |
|---|---|---|---|
| MiniQmtBroker | MOD-L06-001 | `src/zephyr/ex_core/adapters/miniqmt_broker.py` | D_EX_CORE |
| OrderManager | MOD-L06-001 | `src/zephyr/ex_core/order_manager.py` | D_EX_CORE |
| FillHandler | MOD-EX-001 | `src/zephyr/ex_core/fill_handler.py` | D_EX_CORE |
| OrderExecutionSaga | MOD-EX-057 | `src/zephyr/ex_core/order_execution_saga.py` | D_EX_CORE |
| TradingSession | MOD-L06-001 | `src/zephyr/ex_core/trading_session.py` | D_EX_CORE |
| PositionReconciler | MOD-EX-056 | `src/zephyr/ex_core/position_reconciler.py` | D_EX_CORE |
| AlgoTradingEngine | MOD-XS-005 | `src/zephyr/ex_sor/core/algo_trading_engine.py` | D_EX_SOR |
| TransactionCostOptimizer | MOD-EX_SOR_EXT-003 | `src/zephyr/ex_sor/services/transaction_cost_optimizer.py` | D_EX_SOR |
| SlippageAnalyzer | MOD-EX_SOR_EXT-001 | `src/zephyr/ex_sor/services/slippage_analyzer.py` | D_EX_SOR |
| DefaultTcaEngine | MOD-L07-001 | `src/zephyr/reporting/default_tca_engine.py` | D_REPORTING |
| MatchingLogic | — | `src/zephyr/backtest/core/matching_logic.py` | D_BACKTEST |
| BrokerInterface | MOD-L06-001 | `src/zephyr/trading/trading_contracts/broker_interface.py` | D_TRADING |

### 7.4 外部参考
- 《上海证券交易所交易规则（2026年修订）》（上证发〔2026〕41号，2026-07-06 施行）§3.3.2 集合竞价撤单规则
- 《程序化交易管理实施细则》（证监会/沪深北交易所，2026-04-07 生效，7-07 全面执行）：每秒报单≤15笔、每秒撤单≤15笔、单日撤单率≤15%、报单停留≥50μs
- miniQMT / xtquant 250807.1.2 API 文档（`xttrader.order_stock` / `StockAccount` / `query_stock_positions`）
- 2023-08-28 印花税降率（0.1%→0.05%）；2022-04-29 过户费降率（0.002%→0.001%）
- Almgren-Chriss 最优执行框架（平方根冲击模型）；Implementation Shortfall（IS）成本分解
- Gatheral (2010) 无动态套利约束下平方根冲击形式的唯一性证明
- 2026 最优执行 RL 研究：DASRL（AAMAS 2026，动态动作空间）、TT-DAC-PS（arXiv 2026.06，自适应探索 Actor-Critic）、MACE+AC（arXiv 2026.04，成本模型对 RL 算法选择的决定性影响）、Queue-Reactive+DDQN（arXiv 2025.11，model-free RL）

## 8. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-08 | 1.0.0 | 初稿 | G22 下单对接与撮合执行层 spec 定型：10 要点决策（撮合自适应/滑点DECISION/佣金万0.854/7态机/拒单分类/订单层熔断4%-10-50/集合竞价MVP不碰/T+1查持仓/差额下单先卖后买）+ 现有 production 资产 why 层补全 + 5 项代码 gap 标注 |
| 2026-08-08 | 1.1.0 | 施工环节流程补全 | 审查发现 4 个施工环节流程算法缺失（实盘生存项）：⑪未成交续接（Make-or-Take/PARTIAL补单/尾盘清退）、⑫撤单率控制（滚动监控降级/2026新规每秒≤15笔）、⑬资金预占（串行扣减/提交前拦截）、⑭挂单价算法（被动档买一卖一/主动档对手价）。补 §2.4 Gatheral 无套利理论依据。补 Phase 1.5 演进路径（自适应参与率/peg盘口/TCA规则闭环/coeff校准）。补 2026 最新执行 RL 研究引用。v1.0.0 的 5 项代码 gap 已施工（commit 015826ae），新增 v1.1.0 gap 6-10 待施工。 |
| 2026-08-08 | 1.1.1 | 文档-代码漂移对账 | 逐项核查 §6.1 五项 v1.0.0 gap 对照实码：gap 4（拒单分类）由 ✅ 修正为 ⚠️ 部分实现——分类映射(`_REJECTION_ACTIONS`/`classify_rejection`)+`_handle_rejection` 日志已实现，RETRY/冻结/对账实际动作待 Saga 接管。修正 §2.5/§2.6/§2.7 三处 stale 内联"代码 gap"标注（佣金费率/先卖后买已施工，拒单分类标为部分实现）。 |
