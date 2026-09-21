---
ttl: task_bound
title: 深度审查作业簿——交易会话编排器
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：交易会话编排器（X01）

- 状态: **已审**
- 级别: P0｜类型: 管线
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/trading_session.py:287`
- 生产调用方: qmt_trading_session(QMT实盘入口)、live_strategy_adapter.py:69、scripts/start_paper_session.py:103
- 测试文件: tests/ex_core/test_trading_session.py（57 passed，实测）
- 备注: 实盘会话唯一编排点

## 1 对象快照

- **范围**：`src/zephyr/ex_core/trading_session.py` 全文 1234 行（TradingSession 类 + 事件驱动调仓 receptacle + 4 个 MOD-RK-25 Provider 适配器）。核心链路：`rebalance()`(:514) → `_compute_order_deltas`(:611) → `_validate_and_submit`(:718)（先卖后买 + 执行前四级闸门 + C-004 合规闸 + 资金预占 + 订单层熔断）。
- **排除项**：qmt_trading_session.py（X01 旁系，独立多柜台会话壳，仅做连接编排）；PreExecutionChecker 内部判定逻辑归 X05；OrderManager/Saga 归 X02。
- **测试覆盖概况**：57 用例全绿（6.92s 实测）。覆盖：板块整手/零股清仓/资金预占/订单层熔断/四级闸门 Fail-Closed/事件驱动/NaN 防御。**未覆盖**：在途订单抵扣、stop 与 rebalance 竞态、跨日计数重置、submit 失败孤儿单。
- **材料包缺项声明**：运行时证据包（近 N 天 error 日志/reconcile 记录）未取——生产会话未常态运行，无日志可审；数据画像不适用（本对象消费实时 broker/行情非 DB 表）。缺陷 checklist 15 条已过一遍（命中 #12 邻近项=submit 失败假完成、#4 邻近项=无）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 资金预占代数验证通过：buy 检查 `cost > available_cash + pending_release` 且 available_cash 可为负，不变式 Σ买入 ≤ 初始cash + Σ卖出回笼 恒成立（pending_release 不随消费扣减但由 available_cash 负值对称补偿） | trading_session.py:799-817 | 通过 | 手推代数+造 sell→buy→buy 序列对拍 |
| A | `_calc_target_qty` 用含费用 total_asset 不扣费率算目标量：顶格权重（Σw=1.0）时最后买单必被资金预占拦截（千三费率预留）——设计内保守权衡，非缺陷，但隐含假设"权重和≤0.997"无显式断言 | trading_session.py:693-696 vs :284 | P3(假设) | 构造 Σw=1.0 的 rebalance 观察 blocked |
| A | 订单限价=最新价原值（`limit_price=price`），无价格笼子/涨跌停边界钳制——价格漂移或涨停价申报依赖下游（X05 笼子/X08 柜台）兜底，本层不设防 | trading_session.py:706-716 | P2 | 造 price=涨停价 调 `_build_order` 看无钳制 |
| A | `current_holdings_float` Decimal→float 转换仅作风控输入，精度损失可忽略（股数级），判定无风险 | trading_session.py:737 | 通过 | 代码读审 |
| A.3 | 测试整体判定**可信**：断言强（校验 blocked/submitted 具体构成）、Fail-Closed 各闸均有负例（:937,:1001,:1240,:1271）、NaN 边界有专测（:1024,:1031）；无日期漂移依赖（熔断 reset 测试 :765 用注入而非 today） | tests/ex_core/test_trading_session.py:937-1355 | 通过 | 已实跑 57 passed |
| B | price_provider 返回值无时效性校验：上游给陈旧价（如停牌股昨日价）直接作限价与市值基准；_SessionQuoteProvider 适配层不带 is_suspended 信号（NormalizedMarketData 全字段同价折叠+volume=0），停牌股有价即照常生成订单 | trading_session.py:178-211,652-655 | P2 | 造返回 3 天前价格的 stub price_provider 跑 rebalance |
| B | 信号/权重上游无契约校验：weight 为 NaN/inf 时 `Decimal(str(nan))` 会抛 InvalidOperation 使整批 rebalance 异常中断（非 Fail-Closed 逐单拒）——策略上游已有 NaN 防御则风险低，本层不设防 | trading_session.py:630-633,695 | P2 | 直接调 `_compute_order_deltas({'s': float('nan')}, ...)` 看抛异常 |
| C | 输出消费方清单：OrderManager（create/submit/cancel）、submitted/blocked 列表→get_session_report、_fills→MOD-RK-25 快照与 fill_handler 链、事件→_on_rebalance_requested。爆炸半径=全账户（会话级唯一下单编排点） | trading_session.py:845-858,1130-1150 | 记录 | grep 已列 |
| D | 旁系双实现：qmt_trading_session.py（多柜台编排壳，委托给 TradingSession？——经查它组合多个 session 而非复制逻辑）与 live_strategy_adapter.py 两个入口；无同公式重复实现，口径一致 | src/zephyr/ex_core/qmt_trading_session.py:60 | 通过 | 读审两文件职责切分 |
| E | **重复触发双下单**：rebalance delta 只对照 positions.holdings，不抵扣在途未成交订单——事件总线重投/手动+事件双触发时，首批订单未成交前二次 rebalance 会生成同向重复订单；资金预占仅对"broker 已冻结资金"的实盘 broker 有效拦截，Simulation/文件桥 broker 无此保证；卖出侧二次超量由柜台持仓不足拒单兜底（有报错） | trading_session.py:519-545,611-641 | P1 | 首批订单 mock 为永不成交，二次 rebalance 断言 create_order 再次同向调用 |
| E | **跨日计数永不清零**：reset_daily_circuit_breaker 全仓无生产调用方（仅 start() 自调 :391）；长驻实盘会话第 2 交易日起 _total_order_count_today 累计，满 50 笔后永久静默拦截全部新单（仅 warning 日志）——"安全方向"偏差但属断了没人知道 | trading_session.py:1121-1124 + grep 全仓 | P2 | `grep -rn reset_daily_circuit_breaker src/`（仅定义+start 自调）；造 51 笔跨日场景 |
| E | **stop() 与 rebalance 竞态**：stop() 不持 self._lock——撤单扫描 `_cancel_pending_orders` 遍历时 rebalance 可能正提交新单，后提交者漏撤，停机后残留活跃订单 | trading_session.py:414-422 vs :514-517 | P2 | 线程 A rebalance 阻塞于 broker.submit，线程 B stop()，观察新单未被撤 |
| E | **submit 失败孤儿单**：create_order 成功但 submit_order 抛异常时，registered 订单停留 OrderManager 创建态无人取消，session 只把未注册值对象记 blocked；下轮 rebalance 以新 uuid 重下 → OrderManager 孤儿单累积 | trading_session.py:845-865 | P2 | mock submit_order 抛异常，断言 order_manager 中残留 PENDING 单 |
| E | RETRY_ONCE/IDEMPOTENT_RETURN 类拒单仅 INFO 日志即弃（"上层 Saga 处理"），本链未接线 Saga（未 import order_execution_saga）→ 价格/连接类可重试拒单静默丢单，无重试无告警 | trading_session.py:1063-1070 | P2 | 造 error_code=价格类拒单观察无重试发生 |
| E | 时序：fill 回调从 broker 线程无锁 append `self._fills`（CPython list.append 原子，可接受）；rebalance 全程持锁串行，无重入死角 | trading_session.py:1130-1139,514-517 | 通过 | 代码读审 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

1. **执行前逐单热路径风控闸（熔断→时段→快照→否决 + Fail-Closed）**：对等已有。业界 OMS pre-trade risk 检查即"每单在热路径逐单校验 size/price band/position limit + kill switch 兜底"（Quod Financial, 2024-2025, https://www.quodfinancial.com/pre-trade-risk-controls-in-electronic-trading-guardrails-before-the-order-hits-the-wire/ ；Sterling Trading Tech, https://sterlingtradingtech.com/news-insights/risk-checks-in-the-oms-the-buck-stops-here ；QuestDB Glossary, https://questdb.com/glossary/pre-trade-risk-checks/）。本对象的四级闸+失效 Fail-Closed 与业界 fail-safe 原则一致，且"单单隔离不牵连整批"设计合理。
2. **事件驱动调仓（删 Timer 改事件订阅）**：对等已有。事件驱动编排替代定时轮询是事件驱动架构标准做法，与交易所 event-driven compliance 思路同构（Pico pre-trade risk 文档描述的事件化校验管线, https://www.pico.net/products/data-and-trading-software/pre-trade-risk/ ）。
3. **在途订单抵扣（open order offset）**：立卡候选。成熟 OMS/EMS 在重算目标仓位时以 open orders 冲抵 delta（避免重复下单是 EMS 基本功；参照 FIX 协议 OMS 实践与 Quod/Sterling 的订单生命周期管理描述）。本对象缺失，建议在 `_compute_order_deltas` 前拉 OrderManager 活跃单按 symbol/side 冲抵。

## 4 缺陷清单

**P1-1 rebalance 不抵扣在途订单，重复触发可双下单**
- 现状：delta=目标量-当前持仓，活跃订单（PENDING/SUBMITTED/PARTIAL）不进入计算。
- 证据：trading_session.py:611-641（仅用 positions.holdings）；:656-657（current_qty 只来自 holdings）。
- 影响：事件总线重投/手动+事件双触发/快速连续 rebalance 时同向重复订单。爆炸半径=全账户资金（实盘 broker 冻结资金可部分拦截买入，卖出由柜台持仓不足拒单；模拟/文件桥 broker 两层兜底皆弱）。
- 建议修法：`_do_rebalance` 拉取 OrderManager 活跃单，按 (symbol, side) 冲抵 delta，或存在活跃单的标的本轮跳过。
- 验证法：单测——首单 mock 永不成交，二次 rebalance() 断言无新同向 create_order。

**P2-1 跨日熔断计数永不清零（长驻会话静默停摆）**
- 现状：reset_daily_circuit_breaker 仅 start() 调一次，无日切钩子。
- 证据：trading_session.py:391,1121-1124；全仓 grep 无其他调用方（已查无）。
- 影响：第 2 交易日起累计计数，50 笔后全账户静默拒新单，仅 warning 日志。
- 建议修法：rebalance 入口比对当前交易日与上次计数日，跨日自动 reset（参照其自家"2.4A 信号③"治本思路延伸）。
- 验证法：grep 调用方；单测造 prev_day≠today 调 rebalance 断言计数清零。

**P2-2 stop() 不持锁与 rebalance 竞态，停机漏撤单**
- 现状：stop 直接 `_cancel_pending_orders`，不获取 self._lock。
- 证据：trading_session.py:414-422 vs :516-517。
- 影响：停机时正提交的订单漏撤，收盘后残留活跃单。爆炸半径=单会话全部标的。
- 建议修法：stop() 内 `with self._lock:` 包裹撤单（注意撤单是网络调用，可先置 _running=False 再持锁扫一次）。
- 验证法：并发单测——rebalance 线程阻塞于 submit 时调 stop，断言最终无活跃单。

**P2-3 create 成功 + submit 失败 → OrderManager 孤儿单**
- 现状：submit_order 抛异常进 _handle_rejection，registered 单无人取消。
- 证据：trading_session.py:845-865。
- 影响：OrderManager 残留创建态订单；柜台侧若实际受理（响应超时类异常）则形成本地不知情的真实挂单。
- 建议修法：except 分支对 registered 单尝试 cancel_order（幂等）后再分类。
- 验证法：mock submit_order 抛超时，断言 cancel_order 被调用。

**P2-4 可重试拒单静默丢单（RETRY_ONCE 未接线）**
- 现状：_handle_rejection 对 RETRY_ONCE 仅 INFO 日志，注释称"上层 Saga 处理"但本文件未 import/注入 Saga。
- 证据：trading_session.py:1063-1070。
- 影响：价格类/连接类拒单无重试无告警，调仓静默不完整。
- 建议修法：接线 order_execution_saga（X02）或在会话级提供拒单重试队列+计数告警。
- 验证法：造价格类 error_code 拒单，观察无二次 submit。

**P2-5 上游价格无时效/停牌防御**
- 现状：price_provider 输出直接作限价与市值基准；quote 适配层不带停牌信号。
- 证据：trading_session.py:178-211,652-655。
- 影响：停牌/长期无成交标的按陈旧价生成订单（柜台会拒，但占用熔断计数与风控带宽）。
- 建议修法：PriceProvider 契约增加时间戳下限校验（超龄价跳过+告警）。
- 验证法：stub 返回陈旧价，断言订单照常生成（现状复现）。

**P3-1 目标量计算隐含"权重和≤1/(1+费率)"假设无显式断言**（证据 :693-696/:284；验证法：Σw=1.0 观察 blocked）。
**P3-2 date.today() 本机时区口径**（:936；CST 服务器无影响，非 CST 部署有跨日边界误判；验证法：改服务器时区复现）。
**P3-3 checklist INTRADAY 传 UTC now 与文件头北京时刻口径声明混用**（:749 vs :126-128；INTRADAY 无 deadline 仅 checked_at 记录受影响，低危）。

## 5 挂起疑问

1. P1-1 的实际爆炸半径取决于实盘 broker（MiniQmt）get_positions 是否包含冻结资金口径——需 Owner 确认 qmt 持仓快照语义（含冻结则买入侧有兜底，卖出侧仍有超量拒单噪音）。
2. 事件总线 `ex_core.rebalance.requested` 的投递语义（at-most-once / at-least-once）未查真源——若至多一次则 P1-1 触发面收窄为手动+事件并发。
3. checklist INTRADAY 清单 provider 的数据源是否生产接线（检测失效会 Fail-Closed 拒整批）——装配层责任，未在本对象内。

## 6 完备性自评

- 六轴全查：A（数学四问：预占代数/整手/熔断阈值/费率全过）、B（price_provider/checklist/风控限额三输入逐条）、C（消费方清单+爆炸半径）、D（旁系双会话对比）、E（五问逐条：静默失败=P2-4、假阳性=无、断了没人知道=P2-1、重复触发=P1-1、时序=通过）、F（2 条对照+1 立卡）。
- 长尾：①SimulationBroker 实现未审（X08 范围外）；②CancelRateGuard 内部逻辑未深审（旁系，假设单实例防护测试已覆盖）；③事件总线实现（shared/event_bus）投递语义未读真源。

## 7 收口裁定（收口方填）
- 三态逐条：
- 修复 commit:
- 复检结论:
