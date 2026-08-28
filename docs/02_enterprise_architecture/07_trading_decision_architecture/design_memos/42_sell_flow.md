---
ttl: permanent
doc_type: architecture_view
title: 卖出流 spec
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.7.2"
date: 2026-08-15
topic: sell_flow
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-14 第三批施工（会话 AI-SELL-001），MVP 4 模块——MOD-SELL-000 分诊/004 止损/005 止盈/019 执行编排，分支 87764ffb29 经 a337e0f54c 合并回 dev；本档升 v1.7.1（补阶段 5b + 触发条件勘正）。
>
> **最终成果**：sell_decision 227 测试全绿；4 节点经依赖图确认为稳定+生产态；止损/止盈/破位/分批四族的 MVP 范围按本档取舍落地。
>
> **未做事项及原因**：
> - MOD-SELL-014/017 未施工——MVP 范围决策（登记 CAND-SELL-001，触发条件=G04 参数校准 + 连续小亏实盘证据）。
> - TradeLevelCircuitBreaker（交易级熔断）Phase 2 未做——同登记候选库，等触发条件。
> - G04 参数校准（ATR 倍数/移动止损回撤/时间止损差异化）未做——依赖首批策略回测/实盘轨道记录，属"等数据"非施工缺口（遗留 #48 统筹跟踪）。

> ## 结案报告回填（2026-08-28 代码实证复核）
> 原"MOD-SELL-014/017 未施工（MVP 决策）"已过时：sell_decision/core/strategy_specific_stop_framework.py（MOD-SELL-014）与 trade_level_circuit_breaker.py（MOD-SELL-017，evolving 成熟度+测试在位）均已落码；MVP 4 模块（SELL-000/004/005/019）+21 测试文件实证不变。
> **仍真实未完工**：G04 参数校准（ATR 倍数/移动止损/时间止损差异化+熔断 N=2/3）待首批策略回测/实盘 track record（既定挂载，跨文档校准项）。

# 卖出流 spec

> 本备忘把 [battle_map_07_sell_flow](../battle_map/battle_map_07_sell_flow.md) 14 环节的"what is"落地为卖出侧"how + when"的可施工 spec：止损/止盈/破位/分批四族的 MVP 取舍、时序、T+1 约束、与回撤 Protocol 联动。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 边界：本备忘只定卖出**流的编排与退出策略**（when + how to exit）；选股信号（G04/G05）、仓位算法（G12）、回撤风控阈值（G16）不在本备忘范围，本备忘只消费/响应其产出。D_SELL_DECISION 域 24 模块（[68_d_sell_decision](../../02_domain_architecture_docs/68_d_sell_decision.md)）的算法细节以代码/蓝图为准，本备忘定"为什么这么编排"。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G20 卖出流 spec |
| 所属 | 作战地图 07 |
| 依赖 | G19（[41_buy_flow](41_buy_flow.md)，突破失败降级联动） |
| 对标 | O'Neil 卖出法则 / 机构 ATR 止损 / trailing stop / A 股 T+1 跌停排队 |
| 正交性 | ⚠️ 情绪退潮卖出与 regime 协同（但 regime 只给 Shrinkage，卖出逻辑在策略内） |
| 优先级 | P3 |
| 状态 | 已定稿·MVP 已施工（AI-SELL-001：Triage/止损/止盈/执行编排 4 模块落码，28/35 未就绪有降级） |

## 2. 背景

### 2.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道，**T+1，不能做空**）
- 卖出决策域 D_SELL_DECISION 已有 24 模块（[68_d_sell_decision](../../02_domain_architecture_docs/68_d_sell_decision.md)）：**13 生产态**（⚠️ v1.6.0 精确化：其中 6 个为 __init__.py 包入口 generated 占位，真实业务生产态 7 个——突破成败/收集器/融合引擎/紧迫度/冲突仲裁/猎杀防护/置换再平衡，详见 §2.4）+ **11 设计态**（止盈/止损/策略止损范式/分批退出/情景预案/做T/闭环优化等）
- battle_map_07 已有 14 环节（6 运营态 / 7 设计态 / 1 弃用态），BM-SELL-04 止盈止损族是核心待施工环节
- 卖出侧比买入侧更复杂——"何时卖"是交易最难决策，且 A 股 T+1 + 跌停板约束叠加

### 2.2 核心问题
battle_map_07 锁定了卖出流的**环节拓扑**（突破成败→收集评分→止盈止损族/置换再平衡→融合仲裁→冲突仲裁→执行→闭环优化），但未定义：
- 止损/止盈/破位/分批四种退出方式是否全需要（过度工程审查）
- 止损用固定% / 移动 / ATR 哪种，参数怎么定
- 止盈逻辑怎么定（固定/移动/分批/时间加权）
- 情绪退潮卖出与 regime CRISIS/RECOVERY 如何协同（[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) 退潮阶段是骨架）
- 破位卖出（突破成败 BM-SELL-01 已建）如何与止损族联动
- 分批卖出是否 MVP 必需
- T+1 卖出约束（当日买入次日才能卖、跌停板不卖、做T 例外）
- 与 [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 回撤 Protocol 四级阈值如何联动

### 2.3 约束条件
- **T+1 不能做空**：当日买入次日才能卖；跌停板无法成交（不提交卖单，排队次日集合竞价）；做T 是唯一日内卖出例外（底仓净数量不变）
- **system_charter §3 约束四（策略三维度解耦）**：卖出（how）独立于选股（what）/仓位（how much）
- **保守原则**（BM-SELL-06）：同标的同时有买卖信号→卖出优先；风控>仓位>市场态>卖出>T+1预测>...>买入
- **Kill Switch 不可覆盖**（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5.5）：触发即执行，不允许人工覆盖延迟
- **BM-SELL-04 策略止损范式**（MOD-SELL-014 设计态待施工，v1.6.0 订正——此前标"已建"有误：68 域文档 planned 无代码无蓝图、源码目录无实现文件，battle_map"generated"仅包入口级；MVP 先用 §3.3 Chandelier 按持仓阶段切 M 值的简化分工替代）：不同策略类型用不同止损风格（趋势宽/均值回归中/高频紧/Carry 宽/套利无）

### 2.4 已施工设施盘点（通用规则 #11：先清楚有什么 → 才能知道怎么改 → 才能知道该退役什么）

> v1.6.0 新增。卖出流不是从零设计——信号收集/融合/仲裁/紧迫度/破位/猎杀防护/置换再平衡均已 production（非 stub）。本备忘为止损/止盈/Triage 等待施工环节补 why 层 spec。盘点分三块：**sell_decision 域已施工 7 模块** + **跨域可复用设施** + **未施工清单（本 spec 的施工对象）**。

**sell_decision 域已施工**（7 个业务生产态模块，全部 [MATURITY] production，v1.6.0 源码核实）：

| 环节 | 模块 | blueprint_id | path | 本备忘消费方式 |
|---|---|---|---|---|
| 突破成败（破位卖出源） | BreakoutFailureDetector | MOD-SELL-003 | `src/zephyr/sell_decision/core/breakout_failure_detector.py` | §3.6 破位卖出：K≥3 次失败→FORCED_CLEAR 强制清仓 |
| 卖出信号收集 | SellSignalCollector | MOD-SELL-001 | `src/zephyr/sell_decision/core/sell_signal_collector.py` | §3.2 收集评分：8 类信号枚举（含时间止损第⑦类枚举，算法待施工） |
| 融合仲裁 | SellSignalFusionEngine | MOD-SELL-007 | `src/zephyr/sell_decision/core/sell_signal_fusion_engine.py` | §3.1 融合：加权融合算综合卖出意愿 0~1，强制清仓绕过 |
| 紧迫度 | SellUrgencyScorer | MOD-SELL-009 | `src/zephyr/sell_decision/core/sell_urgency_scorer.py` | §3.8 执行时序：紧迫度→市价/限价执行策略映射 |
| 冲突仲裁 | SellConflictArbitrator | MOD-SELL-008 | `src/zephyr/sell_decision/core/sell_conflict_arbitrator.py` | §3.8 做T 优先级：卖出优先+强/弱冲突分级（⚠️ depgraph build_status=deprecated 与源码 production 标注分裂，见 §7） |
| 猎杀防护 | StopHuntingProtector | MOD-SELL-015 | `src/zephyr/sell_decision/core/stop_hunting_protector.py` | §3.3 止损位偏移 1-2% + 软止损 OBSERVING 观察期（四态机 NORMAL/OBSERVING/CONFIRMED/CLEARED） |
| 置换再平衡 | ReplacementRebalanceSeller | MOD-SELL-006 | `src/zephyr/sell_decision/core/replacement_rebalance_seller.py` | §3.7 倒金字塔分批（50-30-20）唯一已施工的分批实现，止盈止损族可复用 |

**跨域可复用设施**（v1.6.0 源码核实，止损/止盈施工时不需从零造）：

| 设施 | 位置 | 现状 | 与本备忘关系 |
|---|---|---|---|
| 移动止损（trailing） | `src/zephyr/risk/implementations/default_stop_loss_engine.py`（method="trailing"，trailing_pct=0.03，`highest_since_entry × (1−trail_pct)`） | 🟦 已施工（risk 域简化版） | §3.3 Chandelier 止损是其升级——固定 trail_pct→ATR 自适应 M×ATR(14)，施工时替换/并存关系待定（见 §7 待定问题） |
| 时间止损（time_based） | 同上（method="time_based"，max_hold_days=20，`_check_time_based`） | 🟦 已施工（risk 域简化版） | §3.2 时间止损"5 天未移动 1×ATR"是其升级——固定天数→ATR 自适应阈值 |
| 波动率止损（volatility） | 同上（method="volatility"，vol × vol_multiplier × entry_price） | 🟦 已施工（最接近 ATR 止损，但未引用 ATR 指标） | §3.3 ATR 止损的直接前身，施工时以 ATR(14) 替换通用 vol 估计 |
| 持仓 Triage 消费方 | `src/zephyr/position/core/position_drift_monitor.py`（TriageLevel 枚举，注释"来自 SELL-00"） | 🟦 已施工（消费方） | §3.2 Triage 分级的生产方 MOD-SELL-000 待施工，消费方已就位 |

**未施工清单**（本 spec 的施工对象，v1.6.0 全 src grep 确认无实现）：

| 环节 | blueprint_id | 本 spec 章节 | 伪代码状态 |
|---|---|---|---|
| 持仓 Triage 分级（生产方） | MOD-SELL-000 | §3.2 | ✅ 已补全（triage_position） |
| 止盈策略（移动止盈 Chandelier 盈利区） | MOD-SELL-004 | §3.4 | ✅ 已补全（compute_exit_price） |
| 止损策略（ATR+移动 Chandelier 统一） | MOD-SELL-005 | §3.3 | ✅ 已补全（compute_stop_loss） |
| 策略止损范式 | MOD-SELL-014 | §2.3/§4.1 | 映射规则已定型（趋势宽/均值回归中/高频紧），代码待施工 |
| 分批退出 | MOD-SELL-017 | §3.7 | ✅ 演进路径已补全（simple_scaling_out 三步法） |
| 连续亏损熔断 | —（未登记） | §3.10 | ✅ 已补全（TradeLevelCircuitBreaker） |
| 时间止损算法（ATR 自适应） | —（收集器第⑦类信号枚举已建） | §3.2 | ✅ 已补全（check_time_stop） |
| 跌停板排队优先级 | —（执行层落地） | §3.8 | ✅ 已补全（rank_limit_down_orders） |
| Kill Switch 清仓排序 | —（执行层落地） | §3.9 | ✅ 已补全（rank_kill_switch_liquidation） |

> **与执行层（40 号）的落地边界**：本 spec 伪代码（止损/止盈/Triage/排队/排序）落地后产出卖出信号/目标权重，经 [40_execution_broker](40_execution_broker.md) §2.11 订单分解→§2.15 PricingPolicy 挂单价→MiniQmtBroker 发出；跌停板排队优先级与 Kill Switch 清仓排序的最终执行依赖 40 号 OpenOrderResolver/PricingPolicy（均已施工，40 号 §1.4）。

**施工落地（v1.7.0，AI-SELL-001，2026-08-13）**：上表 9 项中 7 项已落码为 4 个模块（65 单元测试全绿，含既有 7 模块 162 测试无回归）：

| 模块 | 路径 | 承载伪代码 | 测试 |
|---|---|---|---|
| MOD-SELL-000 持仓 Triage | `src/zephyr/sell_decision/core/position_triage.py` | §3.2 triage_position（含 BM-POS-09 threshold_delta 硬封顶 ±0.10；ATR 缺失降级 MONITOR 中间档） | tests/sell_decision/test_position_triage.py（14） |
| MOD-SELL-005 止损策略族 | `src/zephyr/sell_decision/core/stop_loss_strategy.py` | §3.3 compute_stop_loss（Chandelier 统一，策略类型 M±0.5）+ §3.2 check_time_stop（第⑦类信号源） | tests/sell_decision/test_stop_loss_strategy.py（17） |
| MOD-SELL-004 止盈策略族 | `src/zephyr/sell_decision/core/take_profit_strategy.py` | §3.4 compute_exit_price（自动 phase 判定，委托 005 核心真源唯一） | tests/sell_decision/test_take_profit_strategy.py（10） |
| MOD-SELL-019 卖出执行编排（新登记） | `src/zephyr/sell_decision/core/sell_execution_planner.py` | §3.8 schedule_sell_order（含 T+1/跌停硬约束落地）+ rank_limit_down_orders + §3.9 rank_kill_switch_liquidation | tests/sell_decision/test_sell_execution_planner.py（24） |

施工对 spec 伪代码的三处工程修正（均数学等价或补 spec 未覆盖路径，不改变 spec 决策语义）：①triage 改绝对价格距离比较（与伪代码同乘 entry 消去除法，消浮点尾差）；②triage ATR 缺失降级 MONITOR（spec 未给降级参数，取 §3.2"正常持仓"最保守中间档）；③schedule_sell_order 落地 §3.8 表格的 T+1/跌停硬约束（伪代码未覆盖：当日买入任何信号 BLOCKED_T1——含 Kill Switch（交易所物理约束），非强制清仓遇跌停 LIMIT_DOWN_QUEUE 排队次日）。未施工 3 项维持 spec 裁定：MOD-SELL-014（MVP 用 005 phase 切换+M±0.5 替代）/ MOD-SELL-017（MVP 一次性退出）/ TradeLevelCircuitBreaker（Phase 2 候选，G04 未校准）。施工登记见 #ARCH-SELL-001。commit 清单见 §9 修订记录 v1.7.0 行。

## 3. 决策：止损(ATR+移动)+止盈(移动)+破位(突破成败)+猎杀防护 四族 MVP，分批/密度感知/逻辑止损族降级

### 3.1 卖出流总览

```
[持仓Triage分级]     [BM-SELL-03 收集评分]      [BM-SELL-04 止盈止损族]      [BM-SELL-02 融合仲裁]    [BM-SELL-06 冲突仲裁]   [执行]
Watch秒级/Monitor5min → 7类信号+多TF共振  →  止损(ATR+移动)/止盈(移动)  →  综合意愿0~1+紧迫度  →  卖出优先+风控优先  →  限价/市价
Hold事件驱动           L2-B/C/D注入             +破位(突破成败)+猎杀防护      强制清仓绕过融合          跌停板不卖排队        T+1口径
                                                分批/密度感知=降级
```

> **顺序理由**：先分级（不是所有持仓都需同等监控）→ 收集评分（7 类信号加权）→ 止盈止损族生成退出决策 → 融合仲裁算综合意愿 → 冲突仲裁（买卖同标时卖出优先）→ 执行。强制清仓（风控/黑天鹅/第K次突破失败）绕过融合直接执行——这是资金安全最高优先级。

### 3.2 ① 卖出时序 —— 持仓分级驱动 + 强制清仓绕过融合

持仓 Triage 分级（BM-SELL-03，MOD-SELL-000 设计态）决定扫描频率：

| 分级 | 触发条件 | 扫描频率 | MVP 可用性 |
|---|---|---|---|
| 🔴 Watch List | 亏损接近止损/主力异常/突破关键位/量价背离 | 秒级 | 降级为分钟级（实时风控未就绪） |
| 🟡 Monitor List | 正常持仓 | 5 分钟级 | ✅ 可用 |
| 🟢 Hold List | 深度盈利+远离止损+长期持有 | 事件驱动 | ✅ 可用 |

**强制清仓绕过融合**（最高优先级，BM-SELL-02）：
- 风控触发（35 Kill Switch：单日-6%/回撤>25%）
- 黑天鹅事件（L2-D）
- 第 K 次突破失败（K≥3，BM-SELL-01）
- 主力弃庄（L2-B）
→ 紧迫度 1.0 → 市价单快速执行，**不经过融合仲裁**

> **时间止损**（持仓 N 天未达预期→触发退出评估）：属 BM-SELL-03 第⑦类信号，MVP 纳入收集评分，阈值按策略类型定（待 G04 校准：打板 1-2 天/多因子 5-10 天/事件 2-3 天）。

**时间止损施工算法**（2026-08 行业前沿，journalplus ATR Trailing Stop）：

```python
def check_time_stop(position, atr_value, holding_days):
    """ATR 自适应时间止损：N 天内未移动 1×ATR 有利方向→强制退出评估"""
    favorable_move = position.current_price - position.entry_price
    atr_threshold = atr_value * 1.0  # 1×ATR 有利方向
    max_stagnation_days = 5  # MVP 默认 5 交易日（journalplus 2026）
    if favorable_move < atr_threshold and holding_days >= max_stagnation_days:
        return "FORCE_EXIT_EVALUATION"  # 喂给 BM-SELL-03 收集评分加权
    return None
```

> **为何用"1×ATR / 5 天"而非固定"N 天"**（选项之外更好的答案）：固定"N 天"忽略波动率——高波动股 5 天可能已翻倍（不该时间止损），低波动股 5 天可能只动 0.5%（该止损但 N 天未到）。用"1×ATR 有利方向"作移动阈值，ATR 自带波动率调整：高波动股阈值自动抬高（给更多时间），低波动股阈值自动降低（更快触发）。journalplus 2026 实证：5 个交易日内未移动 1×ATR 的持仓，后续盈利概率低于 35%。

**Triage 分级判定算法**（施工伪代码已补全）：

```python
def triage_position(position, atr_value, stop_loss_price):
    """持仓 Triage 分级→决定扫描频率"""
    unrealized_pnl_pct = (position.current_price - position.entry_price) / position.entry_price
    distance_to_stop = abs(position.current_price - stop_loss_price) / position.entry_price
    # Watch: 亏损接近止损（<1.5×ATR 距离）或盈利回撤接近止损
    if distance_to_stop < atr_value * 1.5 / position.entry_price:
        return "WATCH"  # → 分钟级扫描
    # Hold: 深度盈利（>3×ATR）且远离止损
    if unrealized_pnl_pct > atr_value * 3.0 / position.entry_price:
        return "HOLD"   # → 事件驱动
    return "MONITOR"     # → 5 分钟级扫描
```

| 判定条件 | 分级 | 扫描频率 |
|---|---|---|
| 距止损 < 1.5×ATR \| 盈利回撤接近止损 \| 量价背离 | 🔴 Watch | 分钟级（MVP 降级） |
| 正常持仓（距止损 1.5-3×ATR） | 🟡 Monitor | 5 分钟级 |
| 深度盈利（>3×ATR）且远离止损 | 🟢 Hold | 事件驱动 |

### 3.3 ② 止损触发 —— MVP: ATR 止损 + 移动止损，固定% 降级，密度感知待裁定

止损策略族（BM-SELL-04-B，MOD-SELL-005 设计态）MVP 取舍：

| 止损方式 | MVP | 参数 | 降级/演进 |
|---|---|---|---|
| **ATR 波动率止损** | ✅ 主选 | 日内 1.5-2×ATR / 波段 3-4×ATR（[battle_map_07](../battle_map/battle_map_07_sell_flow.md) BM-SELL-04-B） | ATR 缺失→降级固定% |
| **移动止损（trailing）** | ✅ 主选 | 跟踪最高价回撤 5-10%（趋势策略宽/波段中） | 盈利后启动，锁定利润 |
| 固定%止损 | 降级源 | 短线 3-5% / 中长线 8-15%（eastmoney 2026-07） | ATR 缺失时兜底 |
| 密度感知止损 | 待裁定 | 止损位=条件 PDF 5%分位数 | 待 BM-SEL-13 密度 PDF 就绪 |

**ATR 倍数选择**（对标 quantstock 2026 / algovestiq 2026）：
- 日内/短线：1.5-2×ATR（紧，快速认错）
- 波段/趋势：3-4×ATR（宽，防被震出，与 BM-SELL-04-C 趋势策略宽止损一致）
- 14 周期 ATR（行业标准），与 [31_position_sizing](31_position_sizing.md) σ 估计 60 日窗口错峰（ATR 短期波动率，σ 长期波动率）

**Chandelier Exit 施工公式**（2026-08 行业共识，volatilitybox / journalplus / tradersunion）：

ATR 止损与移动止损统一为 Chandelier Exit（Chuck LeBeau），避免两套独立%参数：

```
止损线 = Highest_Close(N) - M × ATR(14)

# MVP 参数（按持仓阶段切换 M 值）：
# 亏损区（入场后未盈利）：N=10, M=3.0（宽，防噪声扫出）
# 盈利区（盈利超 1×ATR）：N=22, M=2.0（紧，锁定利润→统一为止盈/止损）
# 趋势策略：M 上浮 +0.5；均值回归：M 下调 -0.5
```

| 参数 | MVP 值 | 范围 | 来源 |
|---|---|---|---|
| ATR 周期 | 14 | 7-50 | Wilder 行业标准 |
| 亏损区 M 值 | 3.0 | 2-4 | volatilitybox 2026-03：波段 2-3× |
| 盈利区 M 值 | 2.0 | 1.5-3 | journalplus 2026：盈利后收紧 |
| Highest_Close 回看 N | 亏损区 10 / 盈利区 22 | 10-22 | tradersunion 2026-08：默认 22 周期 |

> **为何 Chandelier 统一优于两套独立%参数**（选项之外更好的答案）：原方案"移动止损回撤 5-10%"是固定%回撤，高波动股被噪声扫出、低波动股止损过宽。Chandelier 用 ATR 自适应波动率——volatilitybox 2026-03 回测 595+ 标的 2018-2025 显示 ATR 倍数止损比固定%**减少 34% 过早止损**。亏损区/盈利区只切 M 值不切公式，实现"一套公式两个参数"的极简统一。

**ATR 缺失降级算法**：

```python
def compute_stop_loss(position, atr_value, highest_close_fn, phase):
    """Chandelier Exit 止损计算，ATR 缺失时降级固定%
    v1.5.2 修：删除未使用的 symbol 参数（死参数，函数体从不引用）。
    highest_close_fn: Callable[[int], float]——传入回看 N 日最高收盘价。
        施工方注入，来源：K线数据 close 列 rolling max（如 lambda N: close_series[-N:].max()）。
    phase: "loss"（亏损区，宽 trailing N=10/M=3.0）或 "profit"（盈利区，紧 trailing N=22/M=2.0）。
        与 compute_exit_price（§3.4）自动判定 phase 不同——本函数由调用方显式传入 phase，
        适用于调用方已持有 phase 上下文的场景（如扳机清单 SELL_ATR_STOP 按 phase 分支）。
    """
    if atr_value is None or atr_value <= 0:
        # 降级：固定%止损（MVP 兜底值，eastmoney 2026-07）
        fallback_pct = 0.04 if position.strategy_type == "short_term" else 0.08
        return position.entry_price * (1 - fallback_pct)
    M = 3.0 if phase == "loss" else 2.0
    N = 10 if phase == "loss" else 22
    return highest_close_fn(N) - M * atr_value
```

**止损位偏移防猎杀**（BM-SELL-04-D，MOD-SELL-015 **已建生产态**）：
- 止损位偏移 1-2% 防做市商猎杀
- 软止损模式：到达止损位→不立即执行→进入 OBSERVING 观察期→收盘价<止损位确认→执行 / 收回→解除
- **MVP 保留**（已建，无需额外施工）

> **对标**（algovestiq 2026-05）：止损设在"论点失效位"而非随机百分比。ATR 自适应波动率，避免低波动股止损过宽、高波动股被噪声扫出。本项目 ATR 为主 + 偏移防猎杀，符合行业共识。

> **结构位 + ATR 复合止损实证**（TradeZella 2026-07，100 笔回测）：固定%止损胜率 48%/PF 1.38 < ATR 1.5×止损胜率 52%/PF 1.41 < **结构位止损（支撑/阻力下方）胜率 55%/PF 1.68**。Chandelier Exit = `Highest_Close(N)` 结构位 + `M×ATR` 波动率带，恰好是"结构位+ATR"复合——融合两法优势，理论 PF 应介于 1.41-1.68 之间且偏向 1.68（结构位锚定论点失效，ATR 自适应噪声）。markettriage 2026-04 position trading 实证进一步背书：3-ATR Chandelier Exit 是持仓周期 4-26 周的最优止损锚，优于固定 5% 和纯移动平均。

**卖出阈值双向反馈契约（BM-POS-09 卖出仓位反馈链路，MOD-POS-016，v1.6.1 作战地图全覆盖补丁补登）**：

- **定位**：BM-POS-09 是卖出侧与仓位侧的**双向链路**（L3.5）——卖出决策到达 / 买入后即时验证窗口 / 仓位状态变更三类触发下，仓位域把持仓盈亏状态回灌给 D-SELL-DECISION，使卖出阈值随盈亏动态调整（"盈利放宽 / 亏损收紧"）。链路 source_ref：D-POSITION §1.4 POS-16 Sell-Position Bidirectional Link(v6.0)。
- **裁定（采纳既有设计，补 why 层）**：止损/止盈阈值不是静态参数——持仓处于盈利状态时放宽卖出阈值（给利润奔跑空间，防过早止盈），处于亏损状态时收紧卖出阈值（快速认错，防过晚止损）。**理由**：① 与 §3.3/§3.4 Chandelier 双 M 值设计同源——亏损区 M=3.0（宽）/盈利区 M=2.0（紧）本质是"阈值随盈亏分区切换"的离散实现，本契约是其连续化/显式化表达，二者不冲突（Chandelier 管退出价位计算，本契约管信号触发阈值松紧）；② 行为金融学背书——处置效应（disposition effect）使人/策略倾向过早止盈过晚止损，双向反馈用规则强制反向校正；③ 个人系统无人工盯盘，阈值松紧必须由仓位状态机自动驱动而非盘感。**重评条件**：若实盘复盘发现双向反馈导致"亏损收紧"与 §3.10 连续亏损熔断叠加过度减仓（同因双重惩罚），则评估将收紧幅度与 circuit_breaker_scale 解耦。
- **契约**（PositionStateFeedback → D-SELL-DECISION 阈值动态调整，字段与方向规则）：

| 字段 | 类型 | 方向规则 |
|---|---|---|
| `pnl_state` | enum(profit/breakeven/loss) | 盈利→卖出信号触发阈值**放宽**（如综合意愿阈值 0.6→0.65，需更强信号才卖）；亏损→**收紧**（0.6→0.55，更弱信号即卖） |
| `unrealized_pnl_pct` | float | 幅度调制输入：盈利越深放宽越多（封顶，防"永远不卖"）；亏损越深收紧越多（封底，防"一跌就割"噪声扫出） |
| `threshold_delta` | float ∈ [-0.10, +0.10] | 最终阈值调整量，消费方=D-SELL-DECISION 融合意愿触发线；正值=放宽，负值=收紧 |
| `feedback_window` | enum(intraday/daily) | 盘中即时验证窗口（见下）走 intraday；日终盈亏状态走 daily |
| `source_position_id` | str | 关联 BM-POS-01/03 仓位状态机持仓实例 |

  **方向规则汇总**：`profit → +delta（放宽）` / `loss → -delta（收紧）` / `breakeven → 0（不动）`；`|delta|` 随 `|unrealized_pnl_pct|` 单调递增但**硬封顶 ±0.10**（防阈值漂移出可解释范围）；风控强制清仓（§3.2 强制清仓绕过融合）**不经本契约**——生存底线不接受阈值放宽。
- **买入后即时验证窗口**（本链路 intraday 分支，参数以作战地图登记为准）：5min 跌破买入价 >1% 且放量 → 转入 OBSERVING 观察期（与本节软止损四态机衔接）；15min 跌破分时均线 → 减仓 50%；30min 反向运动 >2ATR → 全部止损。三级递进与本节软止损/猎杀防护共用四态机，不新建状态机。
- **降级**：双向链路未就绪 → 卖出阈值固定不随盈亏调整（退回 §3.3/§3.4 静态 Chandelier 参数，可能过早止盈或过晚止损）。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-RC-05-A | 六种A股止损模式 | §2.4 已施工设施盘点（止损 4 法：trailing/time_based/volatility/固定%兜底）+ §3.3 ATR/Chandelier 止损 | production 已建 |

### 3.4 ③ 止盈逻辑 —— MVP: 移动止盈，固定/分批/时间加权待裁定

止盈策略族（BM-SELL-04-A，MOD-SELL-004 设计态）MVP 取舍：

| 止盈方式 | MVP | 参数 | 降级/演进 |
|---|---|---|---|
| **移动止盈（trailing TP）** | ✅ 主选 | 跟踪最高价回撤 X%（与移动止损统一为 trailing） | 盈利超阈值后启动 |
| 固定止盈 | 待裁定 | 到价即卖（如+8%/+10%） | 待 G04 策略类型校准 |
| 分批止盈 | 待裁定 | 分档卖出（1/3-1/3-1/3） | 待 MOD-SELL-017 分批退出就绪 |
| 时间加权止盈 | 待裁定 | 持有越久止盈线越低 | 待 G04 校准 |
| 密度感知动态止盈 | 待裁定 | 止盈位=条件 PDF 75%分位数 | 待 BM-SEL-13 就绪 |

**移动止盈与移动止损统一为 Chandelier Exit**（§3.3 公式的盈利区延伸）：MVP 阶段，盈利后的 trailing 既是止盈（锁定利润）也是止损（保护盈利）。用 §3.3 Chandelier Exit 统一，不维护两套独立%参数：

```python
def compute_exit_price(position, atr_value, highest_close_fn):
    """统一止盈止损：亏损区用宽 Chandelier，盈利区切换紧 Chandelier
    v1.5.2 修：ATR 缺失时降级固定%（原仅 atr_pct 兜底但 return 行仍用 None*float 会崩溃，
        与 §3.3 compute_stop_loss 的 ATR 缺失降级逻辑对齐）。
    """
    # ATR 缺失降级：与 §3.3 compute_stop_loss 一致的兜底逻辑
    if atr_value is None or atr_value <= 0:
        fallback_pct = 0.04 if position.strategy_type == "short_term" else 0.08
        return position.entry_price * (1 - fallback_pct)
    unrealized_pnl_pct = (position.current_price - position.entry_price) / position.entry_price
    atr_pct = atr_value / position.entry_price  # ATR 缺失已在上方 guard 返回，此处安全
    # 盈利超 1×ATR → 切换为盈利区参数（紧 trailing，锁定利润）
    phase = "profit" if unrealized_pnl_pct >= atr_pct else "loss"
    M = 2.0 if phase == "profit" else 3.0
    N = 22 if phase == "profit" else 10
    return highest_close_fn(N) - M * atr_value
```

- 亏损区：Chandelier(N=10, M=3.0)——宽 trailing，锚 10 日最高收盘价
- 盈利超 1×ATR：切换 Chandelier(N=22, M=2.0)——紧 trailing，锚 22 日最高收盘价，锁定利润
- **切换点用 ATR 而非固定+5%**：高波动股 ATR 大→切换阈值自动抬高（防过早锁利）；低波动股 ATR 小→切换阈值自动降低（快速进入保护模式）

> **对标**（vibetrader 2026-03 / fairmontequities 2026-07）：trailing stop 不封顶上涨、自动锁定利润、消除决策疲劳，是交易 bot 理想止盈工具。趋势策略 trailing 宽（5-10%），波段中（3-5%）。

### 3.5 ④ 情绪退潮卖出 —— 退潮加权卖出信号，与 regime 协同但分工

情绪周期 5 阶段（[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) ①：冰点/反核/主升/疯狂/退潮）中，**退潮阶段**触发卖出信号加权：

| 情绪阶段 | 卖出端响应 | MVP 可用性 |
|---|---|---|
| 冰点 | 不主动卖出（底部区域） | 降级为 regime ⑦阴跌判断 |
| 反核 | 正常 | — |
| 主升 | 持有（趋势中） | — |
| 疯狂 | 减仓预警（顶部风险） | 降级为 regime ②动量牛市 |
| **退潮** | **卖出信号加权**（BM-SELL-03 L2-B 注入，主力出货信号加权） | 降级为 regime ⑧加速下跌 |

**与 regime CRISIS/RECOVERY 协同边界**：
- regime（[10_regime_detector_spec](10_regime_detector_spec.md)）管**市场状态风险**→给 Shrinkage 缩 budget（仓位上限降）
- 情绪退潮（28）管**择时卖出**→给卖出信号加权（策略内，不改仓位算法）
- **两者正交**：regime 降仓位上限，退潮加卖出信号强度，不冲突
- MVP 降级：28 未就绪时，退潮卖出信号加权降级为 regime ⑧加速下跌/⑨恐慌崩盘触发（regime 已含情绪维度）

> **过度工程审查**：不新建独立的"情绪退潮卖出模块"。退潮信号通过 BM-SELL-03 收集评分的 L2-B 注入路径实现（已设计），28 active 后校准注入权重。避免卖出侧堆叠情绪专用逻辑。

### 3.6 ⑤ 破位卖出 —— BM-SELL-01 突破成败（已建），与止损族联动

破位卖出由 **BM-SELL-01 突破成败信号**（MOD-SELL-003 **已建生产态**）驱动：

| 突破状态 | 动作 | 联动 |
|---|---|---|
| 突破成功（N日站稳+放量） | 持有/加仓 | — |
| 突破失败（回落>阈值） | 止损卖出 | 喂给 BM-SELL-04-B 止损族 |
| 第 K 次挑战失败（K≥3） | **强制清仓**（最高优先级） | 绕过融合，紧迫度 1.0，市价单 |

**支撑位破位降级**（BM-SELL-01 降级路径）：突破成败判定未就绪→降级为支撑位破位立即清仓（§8.2 支撑位破位→立即清仓）。MVP BM-SELL-01 已建，无需降级。**与 41_buy_flow 联动**：[41_buy_flow](41_buy_flow.md) §3.3 突破失败降级——买入侧只"停"（暂停后续批次），卖出侧 BM-SELL-01 执行止损"卖"，分工清晰（符合三维度解耦）。

### 3.7 ⑥ 分批卖出 —— MVP 降级为一次性执行，分批退出待 MOD-SELL-017

分批退出（BM-SELL-04-E，MOD-SELL-017 设计态）MVP 取舍：

| 模式 | MVP | 说明 |
|---|---|---|
| 一次性退出 | ✅ MVP 默认 | 止盈/止损决策一次性全部执行 |
| 等分退出（1/3-1/3-1/3） | 待裁定 | 待 MOD-SELL-017 施工 |
| 倒金字塔（50-30-20） | 待裁定 | 置换再平衡 BM-SELL-05 已用（生产态），止盈止损族待复用 |
| 混合退出 | 待裁定 | 止盈第一批+移动止损第二批 |
| 逆向中止 | 待裁定 | 第一批卖出后反弹超 X%→暂停剩余 |

> **过度工程审查结论**：止损/止盈/破位/分批四种——**MVP 必需前三**（止损+止盈+破位），分批卖出降级为一次性。理由：分批卖出增加择时复杂度（批次间隔/逆向中止/反弹判定），MVP 先保证"该卖能卖掉"，分批作为演进路径。置换再平衡（BM-SELL-05 已建）的分批倒金字塔可复用，但止盈止损族 MVP 不强求分批。

**简单分批演进路径**（2026-08 行业前沿，arrowalgo Scaling In and Out）：MVP 降级为一次性退出，但阶段 2 不需等完整 MOD-SELL-017，可用"1/3 止盈 + 保本 + trailing"三步法快速实现分批退出：

```python
def simple_scaling_out(position, atr_value, highest_close_fn):
    """简单三步分批退出：1/3 止盈→保本→剩余 trailing
    v1.4.1 修：①删除冗余参数 risk_reward_ratio（函数体用 position.risk_reward 属性，参数未被引用）；
              ②补全 compute_exit_price 的 highest_close_fn 参数（原 ... 省略导致调用不完整）。
    highest_close_fn: 参见 §3.3 compute_stop_loss 签名说明——Callable[[int], float]，传入回看 N 日最高收盘价。
    """
    # Step 1: 1:1 风险回报时卖出 1/3 锁定利润
    if position.risk_reward >= 1.0:
        return ("SELL", position.quantity * 0.33, "TAKE_PROFIT_1")
    # Step 2: 止损上移至保本价（entry_price），剩余仓位零风险
    if position.risk_reward >= 1.0 and not position.stop_at_breakeven:
        return ("MOVE_STOP", position.entry_price, "BREAKEVEN")
    # Step 3: 剩余 2/3 用 Chandelier Exit trailing（§3.3/§3.4 统一公式）
    return ("HOLD_WITH_TRAILING", compute_exit_price(position, atr_value, highest_close_fn))
```

> **为何"1/3+保本+trailing"是 MVP→阶段 2 的最优过渡**（选项之外更好的答案）：完整 MOD-SELL-017 含等分/倒金字塔/混合/逆向中止 4 模式，施工复杂度高。arrowalgo 2026-03 实证：1/3 在 1:1 止盈 + 移动止损到保本 + 剩余 trailing 的三步法，在回测中捕获了 85% 的完整分批退出收益，但只需 1 个函数（非 4 模式状态机）。这是"先 80/20 再精细化"的工程路径。

### 3.8 ⑦ T+1 卖出约束 —— 跌停板不卖排队，做T 例外

| 约束 | 对 sell_flow 的影响 |
|---|---|
| 当日买入次日才能卖 | 当日新建仓标的不可止损卖出（除非走做T BM-SELL-08 底仓回补） |
| 跌停板不卖 | 当前价=跌停价时不提交卖出订单（无法成交），标记"跌停待执行"排队次日集合竞价（BM-SELL-06 SURV-005） |
| 做T 例外 | BM-SELL-08 做T 是唯一日内卖出例外——先卖后买（高位卖底仓→低位买回），底仓净数量不变，T+0 套利 |
| 涨跌停排队预案 | BM-SELL-07 情景预案：封死涨跌停→次日集合竞价卖出方案+排队优先级 |
| 卖出资金 T+1 可用 | 卖出资金次日才可买入，换仓分两天（见 [41_buy_flow](41_buy_flow.md) §3.8） |

**跌停板排队优先级算法**（施工伪代码已补全）：多标的同时跌停时，次日集合竞价挂单顺序：

```python
def rank_limit_down_orders(positions_in_limit_down):
    """跌停排队优先级：亏损越大→风控优先级越高→越先排队"""
    return sorted(positions_in_limit_down, key=lambda p: (
        -p.urgency_score,           # 1. 紧迫度降序（Kill Switch 强制清仓 > 风控减仓 > 止损 > 止盈）
        p.unrealized_pnl_pct,        # 2. 亏损升序（亏损最大的先排）
        -p.position_value,           # 3. 仓位金额降序（大仓先排，减少暴露）
    ))
```

| 优先级 | 场景 | 挂单价格 |
|---|---|---|
| P0 | Kill Switch 强制清仓标的 | 跌停价（确保成交） |
| P1 | 回撤 Protocol Level 3/4 减仓标的 | 跌停价 |
| P2 | ATR 止损触发标的 | 跌停价 |
| P3 | 止盈/换仓标的 | 次日开盘价-0.5%（不一定跌停价，留空间） |

**做T 与止损的优先级**（BM-SELL-06 冲突仲裁，MOD-SELL-008 **已建生产态**）：
- C-012 做T vs C-004 风控→标的在风控减仓名单→做T 信号直接丢弃（风控优先）
- C-012 做T vs C-035 庄家→庄家出货/弃庄阶段→做T 信号自动丢弃（庄家优先）
- 流动性不足 vs C-012 做T→做T 信号丢弃（流动性优先）

**卖出执行时序算法**（施工伪代码已补全，对齐 [41_buy_flow](41_buy_flow.md) §3.4 + 上交所 2026 修订规则）：卖出与买入不同——止损/止盈触发需**盘中立即执行**（不等尾盘），但须区分"可撤单连续竞价"与"不可撤单收盘集合竞价"两段：

```python
def schedule_sell_order(signal_type, current_time, position):
    """卖出执行时序：止损/止盈盘中立即执行，强制清仓市价单，止盈/换仓可尾盘集中"""
    # 强制清仓（Kill Switch/黑天鹅/第K次突破失败）：任何时段市价单立即执行
    if signal_type in ("KILL_SWITCH", "BLACK_SWAN", "BREAKOUT_FAIL_K"):
        return ("MARKET_ORDER_NOW", "市价单立即执行，绕过融合，紧迫度 1.0")
    # 止损触发（ATR/Chandelier/支撑破位）：盘中触发立即挂限价单
    if signal_type in ("ATR_STOP", "CHANDELIER_STOP", "SUPPORT_BROKEN"):
        if current_time < time(14, 57):
            return ("LIMIT_ORDER_NOW", "限价单锚跌停价/止损价，14:57 前可撤改挂")
        else:
            return ("CLOSING_AUCTION_LIMIT", "14:57 后不可撤单，挂收盘竞价单吃唯一收盘价")
    # 止盈/换仓/退潮减仓：可尾盘集中执行（与买入窗口错峰，避免自我对冲）
    if signal_type in ("TRAILING_TP", "REBALANCE", "SENTIMENT_EBB"):
        return ("TAIL_BATCH_14_50", "14:50-14:57 尾盘集中挂限价单，与 41 号建仓同窗口但方向相反")
    return ("HOLD", "无信号，继续持有")
```

| 信号类型 | 执行时序 | 订单类型 | 理由 |
|---|---|---|---|
| 强制清仓（Kill Switch/黑天鹅/第K次突破失败） | 盘中任何时点立即 | 市价单 | 生存底线，确保成交，绕过融合 |
| 止损触发（ATR/Chandelier/支撑破位） | 盘中触发立即 | 限价单（锚止损价/跌停价） | 认错要快，14:57 前可撤改挂，14:57 后吃收盘价 |
| 止盈/换仓/退潮减仓 | 14:50-14:57 尾盘集中 | 限价单 | 非紧急，与建仓同窗口相反方向，U 型高流动性段成交好 |

> **为何止损盘中立即而止盈尾盘集中**：止损是"认错"——价格已破位，每多持有一秒风险增加，须立即执行（algovestiq 2026-05"论点失效位"立即退出）；止盈是"锁定利润"——trailing 止盈是被动触发，不急于一时，尾盘集中可获 U 型高流动性段更优成交价（CSDN 2026-08-08 A 股日内波动研究：14:00-14:57 成交量逐渐走高）。两者时序分离，避免止损单被尾盘集中执行延迟。

> **合规约束**（上交所 2026 修订 §2.4.2，2026-07-06 生效）：14:57-15:00 收盘集合竞价**不可撤单**，止损单若在 14:57 前挂出但未成交，14:57 后无法撤改——须在 14:55-14:57 窗口检查未成交止损单并决定"改挂收盘竞价"或"接受未成交"。与 [41_buy_flow](41_buy_flow.md) §3.4 执行时序算法对称设计。**与 41 号建仓窗口错峰**：41 号建仓在 14:50-14:57，42 号止盈/换仓也在 14:50-14:57——方向相反不冲突（卖 A 买 B 是置换再平衡 BM-SELL-05 已建）；止损盘中立即执行不与建仓窗口冲突；做T（BM-SELL-08）另走 9:45-10:15 卖/13:30-14:30 买回的 U 型节奏（CSDN 2026-08-08），与建仓/止损/止盈全错峰。

### 3.9 ⑧ 与回撤 Protocol 联动 —— 35 四级阈值触发卖出端响应

[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 四级阈值（框架在 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5 已定）触发时，卖出端响应：

| 回撤级别 | 阈值 | 卖出端响应 | MVP 可用性 |
|---|---|---|---|
| Level 1 警告 | 回撤>8% | 新仓风险敞口降至 75%（单笔 2%→1.5%） | ✅ 30 §2.5 框架已定 |
| Level 2 减仓 | 回撤>15% | 仓位缩减至 75%，**停开新仓（仅允许平仓和调仓）**→ 卖出端正常运作 | ✅ |
| Level 3 停仓 | 回撤>20% | 停止所有新开仓，review framework → 卖出端正常运作（可平仓） | ✅ |
| Level 4 清仓 | 回撤>25% | **关闭所有仓位，强制休息**→ 卖出端强制清仓所有持仓 | ✅ |

**日度熔断**（30 §2.5.1）：
- 组合单日亏损>4%→暂停开仓 1 天（卖出端正常）
- 单策略单日亏损>5%→该策略暂停 1 天（卖出端正常）

**Kill Switch**（30 §2.5.5，**不可覆盖**）：
- 单日亏损>6%→立即平仓所有持仓，暂停交易 3 天
- 回撤>25%→清仓+强制休息 5 天+人工 review
- 连续 5 天亏损→降仓至 50%
- 流动性危机（价差>正常 5×）→立即停止开仓，仅允许平仓

**Kill Switch 强制清仓排序算法**（施工伪代码已补全）：Kill Switch 触发时需快速清仓所有持仓，多标的清仓顺序影响最终回收资金（流动性差标的先卖防封死跌停）：

```python
def rank_kill_switch_liquidation(positions):
    """Kill Switch 强制清仓排序：流动性差的先卖（防封死跌停无法成交）"""
    return sorted(positions, key=lambda p: (
        p.liquidity_score,           # 1. 流动性升序（流动性差→成交量小→先卖，防封跌停）
        -p.position_value,           # 2. 仓位金额降序（大仓先卖，快速降低暴露）
        p.unrealized_pnl_pct,        # 3. 亏损升序（亏损最大的先卖）
    ))
```

| 清仓顺序 | 判据 | 订单类型 |
|---|---|---|
| 1 | 流动性差（20日均量后 25%）| 市价单（确保成交） |
| 2 | 大仓位（>总仓位 5%）| 市价单 |
| 3 | 亏损最大标的 | 市价单 |
| 4 | 流动性好+小仓位+盈利 | 市价单（最后清） |

> **为何流动性优先而非亏损优先**：Kill Switch 是生存底线，首要目标是"全部成交"而非"卖好价"。流动性差的标的如果后卖，可能被封死跌停无法成交→暴露无法消除。先卖流动性差的确保全部能成交，再卖流动性好的（即使跌停也能排队成交）。

> **联动边界**：drawdown 是**账户级**风险（35），regime 是**市场级**风险（G15），卖出逻辑在**策略内**（42）。35 触发时通过 budget 节流（G15 Shrinkage）+ 卖出端响应（42 强制清仓/停新仓）协同，三者正交。**35 已 active v1.37.0**：本表四级阈值=30 §2.5 外层框架口径，35 号 §3.2 另有内层代码阈值（5/10/15% 更紧，A/B/C 三层模块）双轨运行，卖出端响应动作不变。

### 3.10 ⑨ 连续亏损熔断 —— 策略级 Circuit Breaker（2026-08-10 四次审查补充，选项外更优算法）

> **施工算法缺失补全**：§3.9 的日度熔断（单日亏损>4%/5%→暂停 1 天）和 Kill Switch（连续 5 天亏损→降仓 50%）都是**时间维度**（按天计数）的熔断。但缺少**交易维度**（按笔计数）的熔断——策略连续亏损 N 笔时，说明策略与当前市场节奏失配，应在时间熔断触发前就递减减仓。

**行业实证**（[Li, Laryea & Ihlamur 2026 arXiv:2604.27150](https://arxiv.org/abs/2604.27150)，Oxford + Vela Research，900+ 历史交易反事实模拟，8960 配置全网格搜索）：

> 核心发现：exit design matters meaningfully——更强的配置改善风险调整收益，普遍倾向**更紧的亏损上限 + 更早的止盈 + 更近的 trailing 保护**。最强配置为 ATR 1.0× 止损 + 2.0× 止盈 + **连续 2 笔亏损后 circuit-breaker 减仓因子 0.25**（即降至 75% 仓位）。论文将 exit-rule tuning 重新定义为校准问题（calibration problem）而非启发式选择。

**三层熔断分工**（时间 vs 交易 vs 账户，正交不重叠）：

| 层级 | 触发条件 | 响应动作 | 响应速度 | 现有覆盖 |
|---|---|---|---|---|
| **交易级**（本节新增）| 连续 N 笔亏损（N=2~3）| 仓位 ×(1-reduction_factor)，递减 | 最快（按笔） | ❌ 缺失 |
| **日度熔断**（§3.9）| 单日亏损>4%/5% | 暂停开仓 1 天 | 中（按天） | ✅ 30 §2.5.1 |
| **Kill Switch**（§3.9）| 连续 5 天亏损 / 回撤>25% | 降仓 50% / 清仓+休息 5 天 | 最慢（按天累计）| ✅ 30 §2.5.5 |

> **为何需要交易级熔断**：时间熔断（日度/Kill Switch）在"每天小亏、连续多天"场景下反应迟钝——策略可能连续 5 笔亏损但每天亏损<4% 不触发日度熔断，等 Kill Switch 连续 5 天触发时已积累可观亏损。交易级熔断在**第 2 笔亏损**就递减减仓，是时间熔断的**前馈补充**（CUSUM §5.2 检测结构性衰减，circuit breaker 是结构性衰减前的即时响应）。

**施工算法**（伪代码）：

```python
class TradeLevelCircuitBreaker:
    """策略级连续亏损熔断：连续 N 笔亏损→递减减仓，盈利→重置"""

    def __init__(self, consecutive_loss_threshold=2, reduction_factor=0.25,
                 min_scale=0.25, reset_on_win=True):
        self.consecutive_losses = 0
        self.consecutive_loss_threshold = consecutive_loss_threshold  # Li 2026: N=2
        self.reduction_factor = reduction_factor  # Li 2026: 0.25 per step
        self.min_scale = min_scale  # 最低降至 25%（4 步到底）
        self.reset_on_win = reset_on_win  # 盈利一笔即重置（快速恢复）

    def on_trade_close(self, trade_pnl_pct):
        """每笔交易收盘后更新连续亏损计数"""
        if trade_pnl_pct < 0:
            self.consecutive_losses += 1
        elif self.reset_on_win and trade_pnl_pct > 0:
            self.consecutive_losses = 0  # 盈利重置

    def get_position_scale(self):
        """返回当前仓位缩放因子 [0.25, 1.0]"""
        if self.consecutive_losses < self.consecutive_loss_threshold:
            return 1.0  # 未触发
        # 每超 1 笔减 reduction_factor，最低 min_scale
        excess = self.consecutive_losses - self.consecutive_loss_threshold
        scale = max(1.0 - (1 + excess) * self.reduction_factor, self.min_scale)
        return scale

    def is_blocked(self):
        """连续亏损超阈值×3→暂停该策略开新仓（只允许平仓）"""
        return self.consecutive_losses >= self.consecutive_loss_threshold + 3
```

| 连续亏损笔数 | 仓位缩放 | 动作 | 来源 |
|---|---|---|---|
| 0-1 笔 | 1.0（满仓）| 正常交易 | — |
| 2 笔 | 0.75 | 递减减仓（Li 2026 reduction_factor=0.25）| arXiv:2604.27150 |
| 3 笔 | 0.50 | 继续递减 | 同上延伸 |
| 4 笔 | 0.25 | 最低仓位 | 同上延伸 |
| ≥5 笔 | 0.25 + block | **暂停开新仓**（is_blocked=True），已有仓位仍按 0.25 缩放（非清仓，等 CUSUM §5.2 判定是否结构性衰减）| 与 §5.2 联动 |

**参数校准依据**（Li 2026 实证 + A 股适配）：

| 参数 | Li 2026 (crypto) | A 股适配 | 理由 |
|---|---|---|---|
| `consecutive_loss_threshold` | 2 | **2-3** | A 股 T+1 换手低，2 笔连亏信号噪声比 crypto 高，打板策略可用 2（高频试错），多因子用 3（低频需更多样本）|
| `reduction_factor` | 0.25 | **0.25** | 直接采用 Li 2026 实证最优值 |
| `min_scale` | — | **0.25** | 最低 25% 防完全空仓（与 Kill Switch 清仓区分——circuit breaker 是"减速"非"停车"）|
| `reset_on_win` | — | **True** | 盈利一笔即重置，快速恢复（与 §3.9 Kill Switch 的"强制休息 5 天"形成"快恢复 vs 慢恢复"梯度）|

> **与 CUSUM 策略衰减检测（§5.2 阶段 8）的关系**：CUSUM 检测的是**结构性衰减**（alpha 长期失效，需停策略重研），circuit breaker 检测的是**短期失配**（策略与当前市场节奏不合，减仓等节奏恢复）。CUSUM 是"诊断"（是否结构性失效），circuit breaker 是"急救"（先减仓止血再说）。两者正交：circuit breaker 触发≠策略失效，可能只是短期 noise；CUSUM 触发=策略确实失效需停。

> **与 §3.9 回撤 Protocol 联动边界**：circuit breaker 是**策略级**（每个 sleeve 独立计数），回撤 Protocol 是**账户级**（全组合统一）。circuit breaker 减仓的是单策略仓位，回撤 Protocol 减的是全组合 budget。两者乘性叠加：实际仓位 = budget（regime Shrinkage）× position_cap（回撤 Protocol recovery_factor）× **circuit_breaker_scale（本节）** × conformal_scale（35 §3.19）。

> **过度工程审查**：circuit breaker 仅 1 个类（~30 行）+ 1 个仓位乘数，非独立模块。它是对现有 Kill Switch / 日度熔断的**精细化补充**（填时间熔断与 Kill Switch 之间的响应空档），不是新增风控层。MVP 可选施工——若 G04 策略类型校准后发现"连续小亏不触发日度熔断但积累可观亏损"实盘证据，则施工；否则 Phase 2 候选。

### 3.11 ⑩ 卖出闭环优化（BM-SELL-09）—— 复盘编排复用 55 §3.6，显著性复用 54 §3.9

> **作战地图全覆盖补丁（v1.6.1 补登）**。BM-SELL-09 是 battle_map_07 拓扑的收口环节（卖出执行→复盘→回调权重），MOD-SELL-010+011+012 设计态（草图§1.4 SELL-10/11/12 + §7第四层）。本备忘前文各环节定"怎么卖"，本节定"卖完怎么评、评完怎么改"。

- **定位**：卖出执行完成 N 天后，用"卖出后价格走势"反评卖出决策质量——信号准不准、执行好不好、权重该不该调。触发=卖出执行完成 + 复盘窗口到达；消费=卖出执行回报（BM-EXE-02）+ 卖出决策记录（BM-SELL-02）+ 卖出后 N 天价格（BM-SEL-01）；下游=D-REPORTING → 学习系统 → BM-SELL-03 信号权重 / BM-SELL-04 策略参数 / BM-EXE 执行策略。
- **裁定（采纳既有设计，补 why 层）**：卖出是交易最难决策，没有事后度量的卖出系统永远无法自我修正。四件套：① **卖后 N 天价格追踪窗口**——记录卖出后 N 日价格路径，回答"卖对了没有"（卖后继续大涨=过早，卖后继续大跌=正确，横盘=中性）；② **按信号类型 × 策略分组的准确率统计**——ATR 止损/Chandelier 止盈/破位清仓/退潮减仓 × 打板/多因子/事件，分组样本独立统计（不分组的汇总准确率会被主导组掩盖）；③ **A/B 显著性检验（p<0.05）**——权重/参数调整必须过统计门槛才生效，防"按噪声调参"；④ **执行质量评分**——卖出滑点/排队成交率/跌停未成交率喂回执行层。**理由**：与 §3.10 交易级熔断、§5.2 阶段 8 CUSUM 同一哲学——"exit-rule tuning 是校准问题非启发式选择"（Li 2026）；个人系统无投研团队复盘，闭环必须自动化。**重评条件**：首批策略 6+ 月实盘 track record 积累后，校准复盘窗口 N 与显著性检验的分组最小样本量；若分组样本长期不足（格子稀疏），降级为仅信号类型单维分组。
- **契约/参数**（建设项，待施工）：
  - 复盘窗口：N 天（默认 5 交易日，校准项；与 §3.2 时间止损 5 天窗口口径对齐，便于"该卖未卖"与"卖错"两类误差对照）
  - 分组维度：信号类型 × 策略类型（两组各 3-4 桶，单格样本 <30 时该格不出调整建议）
  - 显著性阈值：p<0.05（A/B 检验，对照组=调整前权重）
  - 产出契约 **E-SELL-04 SellLoopFeedback**：`{signal_type, strategy_type, window_n, accuracy_post_sell, avg_opportunity_cost, exec_quality_score, weight_adjustment, significance_p, verdict}` → 回调 **BM-SELL-03 信号权重**（weight_adjustment 仅在 significance_p<0.05 时生效，且单次调整幅度 ±20% 封顶防振荡）
  - 降级：闭环未就绪 → 跳过复盘，卖出策略参数保持静态不动态调整
- **调度与框架复用（不新造）**：① **调度复用 [55_monitoring_review](55_monitoring_review.md) §3.6 复盘编排器**——卖出复盘作为一个复盘源挂入 daily→weekly→monthly 链路，产出走 ReportPublisher 归档（周复盘"阈值与参数变更"段消费），不自建调度；② **显著性框架复用 [54_reconciliation_attribution](54_reconciliation_attribution.md) §3.9 deflated-alpha**——`audit()` 4 类检验 + LIKELY_REAL/INCONCLUSIVE/LIKELY_OVERFIT 三态判定直接复用为"信号权重调整建议是否可信"的验证层，日常轻量检验（p<0.05）+ 月/季重量检验（deflated-alpha）分层，与 54 号月/季归因同节奏。
- **边界**：BM-SELL-09 调的是**卖出侧权重/参数**（BM-SELL-03/04 与执行策略），不调仓位（归 BM-POS 族）、不调选股（归 G04/G05）；与 §5.2 阶段 8 CUSUM 的分工——CUSUM 管 sleeve 级"策略该不该停"，本环节管信号级"卖出权重该不该调"，粒度不同不重叠。

## 4. 考虑过的替代方案（拒绝理由）

### 4.1 四族全上（止损+止盈+破位+分批+逻辑止损族+密度感知）—— 拒绝（MVP）
- **拒绝理由**：battle_map BM-SELL-04 止盈止损族含止盈 4 类+止损 4 类+逻辑止损 4 类+策略止损范式 5 类+猎杀防护+分批退出 4 模式，全上是研究课题不是工程任务。MVP 复杂度过高，且密度感知依赖 BM-SEL-13（未就绪）
- **采用**：MVP = 止损(ATR+移动) + 止盈(移动) + 破位(突破成败) + 猎杀防护(已建) + 策略止损范式(设计态待施工，v1.6.0 订正——MVP 先用 §3.3 Chandelier 按持仓阶段切 M 值的简化分工，策略类型差异化随 MOD-SELL-014 施工启用)；分批/密度感知/逻辑止损族(除主力出货)降级为演进路径

### 4.2 固定%止损为主 —— 拒绝
- **拒绝理由**：固定%忽略标的波动率差异，低波动股止损过宽、高波动股被噪声扫出（quantstock 2026 / algovestiq 2026）。A 股波动大，硬性 5% 易被正常波动扫出
- **采用**：ATR 止损为主（自适应波动率），固定%仅作 ATR 缺失时降级兜底

### 4.3 止盈用固定目标价 —— 拒绝（MVP）
- **拒绝理由**：固定止盈封顶上涨空间，趋势策略会错失大行情（vibetrader 2026-03）。"卖太早看股票再涨 25%"是交易最痛场景
- **采用**：移动止盈（trailing）为主，不封顶，自动锁定利润。固定止盈待 G04 策略类型校准后按策略差异化（均值回归可固定，趋势用 trailing）

### 4.4 新建独立情绪退潮卖出模块 —— 拒绝
- **拒绝理由**：[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) 退潮阶段是骨架未定义，新建独立模块会导致 42 ← 28 循环阻塞。退潮信号通过 BM-SELL-03 收集评分 L2-B 注入路径即可实现（已设计）
- **采用**：退潮信号注入 BM-SELL-03（L2-B 主力出货加权），不新建模块。28 active 后校准注入权重

### 4.5 分批卖出 MVP 必需 —— 拒绝
- **拒绝理由**：分批卖出增加择时复杂度（批次间隔/逆向中止/反弹判定），MVP 先保证"该卖能卖掉"。止损/止盈/破位已覆盖退出需求，分批是优化非必需
- **采用**：MVP 一次性退出，分批退出（MOD-SELL-017）作为演进路径。置换再平衡（BM-SELL-05 已建）的倒金字塔分批可复用

### 4.6 卖出侧内置 regime 切换 —— 拒绝
- **拒绝理由**：与 [31_position_sizing](31_position_sizing.md) §2.7 一致。regime 只通过 Shrinkage 缩 budget 间接影响仓位上限，卖出逻辑不读市场态。退潮信号通过 28 注入（策略内），不绕过 regime
- **采用**：卖出侧只收 budget 数字 + 退潮信号注入，regime 节流归 G15

### 4.7 Keltner Channel 止损 —— 拒绝（MVP），记为 Chandelier Exit 替代参考
- **拒绝理由**：Keltner Channel（`EMA(20) ± 2×ATR`）与 Chandelier Exit 都基于 ATR，但 Keltner 锚 EMA 中轨（非最高收盘价），趋势跟踪性弱于 Chandelier。volatilitybox 2026-03 对比显示 Chandelier Exit 在趋势市场中表现更优（stay-in-trend 更久），Keltner 更适合震荡市
- **采用**：Chandelier Exit（§3.3）为 MVP 主选；Keltner Channel 记为震荡市替代参考，待 G04 策略类型校准后按策略差异化（趋势→Chandelier / 震荡→Keltner）

## 5. 上限定义

### 5.1 参数上限汇总

| 参数 | MVP 值 | 上限/范围 | 性质 |
|---|---|---|---|
| ATR 止损倍数（日内） | 1.5-2×ATR | 1-3 | 短线紧 |
| ATR 止损倍数（波段） | 3-4×ATR | 2-5 | 趋势宽，防震出 |
| ATR 周期 | 14 | 7-50 | 行业标准 |
| 移动止损回撤 | Chandelier 统一（见下） | — | 已统一为 ATR-based，不再用固定% |
| Chandelier Exit 亏损区 M | 3.0 | 2-4 | 宽 trailing，防噪声扫出 |
| Chandelier Exit 盈利区 M | 2.0 | 1.5-3 | 紧 trailing，锁定利润 |
| Chandelier Exit 回看 N | 亏损区 10 / 盈利区 22 | 10-22 | Highest_Close 周期 |
| 时间止损 | 5 天未移动 1×ATR | 3-10 天 | ATR 自适应阈值 |
| 止损位偏移防猎杀 | 1-2% | 1-3 | MOD-SELL-015 已建 |
| Watch 扫描频率 | 分钟级（降级） | 秒级（目标） | 实时风控未就绪降级 |
| 强制清仓紧迫度 | 1.0 | — | 绕过融合，市价单 |
| 单笔风险 | 2%（Level1 降至 1.5%） | ≤2% | 与 35 联动 |
| Kill Switch 单日亏损 | 6% | — | 不可覆盖，平仓+暂停 3 天 |

### 5.2 演进路径

| 阶段 | 内容 | 触发条件 |
|---|---|---|
| **MVP（当前）** | 止损(ATR+移动)+止盈(移动)+破位(突破成败)+猎杀防护(已建)+策略止损范式(设计态待施工，MVP 用 Chandelier 阶段切换替代，v1.6.0 订正)；分批一次性；28 未就绪用 regime 降级，35 已 active 1.37.0 可直接联动（v1.6.0 订正） | 本备忘定稿即可施工 |
| **阶段 2** | [28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) 定稿，退潮信号 L2-B 注入权重校准 | 28 active |
| **阶段 3** | [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 定稿，四级阈值与卖出端响应正式联动 | **已满足**（35 已 active 1.37.0）——35 §3.2 三层映射（外层 8/15/20/25% + 内层代码 5/10/15%）与 §3.9 卖出端响应可直接对接，联动代码施工后本阶段关闭 |
| **阶段 4** | BM-SEL-13 密度 PDF 就绪，密度感知止损/止盈启用 | BM-SEL-13 施工完成 |
| **阶段 5** | MOD-SELL-017 分批退出施工，分批卖出启用 | 各策略 track record 积累（量化口径随 G04 校准产出补录，v1.7.1） |
| **阶段 5b（v1.7.1 补登）** | MOD-SELL-014 策略止损范式施工，按策略类型差异化止损（趋势宽/均值回归中/高频紧/Carry 宽/套利无）启用 | G04 按策略类型的参数校准产出（同 §7 三项待定问题依赖） |
| **阶段 6（待裁定）** | 逻辑止损族（基本面/技术面/事件）除主力出货外逐步启用 | 各信号源就绪 |
| **阶段 7（远期·待裁定）** | ML 风控远期：Conformal Kelly drawdown dial——conformal prediction 区间 downside miss 时自动降杠杆（模型失效信号），MaxDD 27.7%→20.3%；替代手工回撤四级阈值的自适应风控 | 各策略 12+ 月 track record + conformal 预测模型校准通过 |
| **阶段 8（远期·待裁定）** | CUSUM 策略衰减检测——实时监控策略 alpha 是否发生结构性衰减（区分"正常回撤"与"策略已死"），触发 sleeve 级降仓/暂停而非单仓位止损 | 各策略 6+ 月实盘 track record（CUSUM 需 OOS 均值 μ₀ 基线） |

**阶段 7 ML 风控远期实证**（出处见 §8.3）：**Conformal Kelly drawdown dial**（[arXiv:2608.01494](https://arxiv.org/html/2608.01494v1)）——conformal 区间 downside miss（实际收益低于预测区间下界）频率显著超历史校准率→判模型失效→自动降杠杆；6 年回测 MaxDD 27.7%→20.3% 且 Sharpe 提升，timing beat 全部 40 个 placebo（rank-based p=1/41≈0.024）；slow/unweighted/per-asset rolling 优于 locally adaptive（区间稳定性>局部锐度，与 35 稳定阈值防过拟合哲学一致）。35 四级阈值（8/15/20/25% 手工）可演进为 conformal drawdown dial——用模型失效信号替代手工阈值。

> **为何 MVP 不做 ML 风控**：Conformal Kelly 需 6+ 月校准数据（75% 覆盖率）；35 四级阈值（8/15/20/25%）+ Kill Switch 不可覆盖已构成完整风控红线（§3.9）。阶段 7 属远期演进，用 ML 自适应阈值替代手工阈值。

**阶段 8 CUSUM 策略衰减检测**（[mathandmarkets 2026-02 Part 81](https://mathandmarkets.com/p/detecting-decay-in-real-time-when)，E.S. Page 1954 工业质控经典工具）：策略回撤与结构性衰减早期肉眼不可区分，CUSUM 实时累积偏离证据，可在 alpha 衰减 **50 个交易日内告警**（远优于滚动 Sharpe 需 6+ 月）。

- **算法**：单侧统计量 `S⁺ₜ = max(0, S⁺ₜ₋₁ + (μ₀ - xₜ) - k)`，μ₀=OOS 验证期策略日均收益（H₀="策略健康"），xₜ=观察日收益，k=0.5σ（allowance slack），h=4σ（balanced，~0.5 次/年误报）。实证：Sharpe~1 策略真实变点 day 200（alpha ~15%→-5% 年化），CUSUM day 250 告警。
- **与 35 回撤 Protocol 的分工**：35 四级阈值管"组合级回撤止血"（8/15/20/25%→降仓/暂停），CUSUM 管"策略级 alpha 衰减诊断"（区分"回撤 vs 已死"）——35 是 symptom treatment，CUSUM 是 root cause diagnosis，正交。CUSUM 告警可联动 [30 §2.5](30_multi_strategy_concurrency.md) PerformanceScore 下调该 sleeve budget（比纯回撤驱动更精准）。
- **四检验对比**（mathandmarkets 2026-02）：
  | 检验 | 原理 | 优点 | 缺点 | 适用场景 |
  |---|---|---|---|---|
  | **CUSUM** | 累积偏离 μ₀ 的证据 | 简单可解释；参数少（k, h）；工业标准 | 需预设 μ₀；二元告警非概率 | **首选**（策略衰减检测） |
  | Page-Hinkley | 累积偏离运行均值的偏差 | 自适应均值；无 μ₀ 假设 | 对缓慢漂移敏感度低 | 备选（μ₀ 难定时） |
  | Bayesian 变点 | 后验 P(changepoint) | 概率输出；可量化不确定性 | 需指定先验；实现复杂 | 与 CUSUM 叠加验证 |
  | 滚动 Sharpe | 滑窗 Sharpe 比率 | 直觉；行业通用 | 滞后大（6+ 月）；窗口选择敏感 | 基线（不推荐单独用） |
- **A 股适配**：衰减主因=crowding（策略拥挤度上升）+ regime 切换（[10](10_regime_detector_spec.md)）+ 监管变化（如 2026-04 程序化新规）。μ₀ 取 OOS walkforward 验证期均值（[11 C1 验证](11_regime_backtest_validation_plan.md)），不用全回测均值（含待检测衰减期）；k=0.5σ/h=4σ 为 balanced 设置，首批策略实盘 6+ 月后按误报率校准。
- **与 BM-SELL-03 收集评分的关系**：CUSUM 是 sleeve 级 meta 信号（非单仓位信号），不注入 BM-SELL-03（那会混淆"仓位该不该卖"与"策略该不该停"）；告警走 [30 §2.5](30_multi_strategy_concurrency.md) PerformanceScore → RegimeMetaAllocator budget 下调路径，是 sleeve 级降仓而非仓位级卖出。

### 5.3 为何这是上限而非妥协
- 止损(ATR+移动)+止盈(移动)+破位+猎杀防护是 2026 年行业共识（quantstock / vibetrader / algovestiq / fairmontequities）
- 不硬依赖 28 骨架（35 已 active 1.37.0，v1.6.0 订正），保证 MVP 可独立施工——避免循环阻塞
- 已建模块（突破成败/收集器/融合/紧迫度/冲突仲裁/猎杀防护/置换再平衡 7 个业务生产态）直接复用，MVP 只需施工止盈(MOD-SELL-004)/止损(MOD-SELL-005)/持仓Triage(MOD-SELL-000)；策略止损范式(MOD-SELL-014)为设计态待施工（v1.6.0 订正，此前"已建"有误——68 域文档标 planned 无代码无蓝图、源码目录无实现文件，battle_map"generated"仅包入口级）
- 真正的上限 = 在 ATR+trailing 框架内把退出做到极致，而不是堆密度感知/分批/逻辑止损族等未就绪信号

## 6. 待裁定（暂缓项）

> 以下项目暂不施工，**非永久禁止**。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **密度感知止损/止盈** | 依赖 BM-SEL-13 密度 PDF（未就绪） | BM-SEL-13 施工完成 |
| **分批卖出** | MOD-SELL-017 设计态；MVP 一次性退出已满足退出需求 | 各策略 track record 积累 |
| **逻辑止损族（基本面/技术面/事件）** | MVP 只做主力出货（复用 L2-B）；其余信号源未就绪 | 各信号源施工完成 |
| **固定止盈/分批止盈/时间加权止盈** | MVP 用移动止盈统一；差异化待 G04 校准 | G04 按策略类型的参数校准产出（非"策略类型定稿"——20 号已 active，校准依赖首批回测/实盘，v1.7.1 措辞勘正） |
| **退潮信号 L2-B 注入权重** | 28 退潮阶段判定未定义 | [28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) active |
| **Watch List 秒级扫描** | 实时风控未就绪，降级分钟级 | 实时风控施工完成 |
| **CUSUM 策略衰减检测** | 需各策略 6+ 月 OOS 实盘 track record 标定 μ₀ 基线；MVP 阶段 35 四级回撤阈值已提供组合级止血 | 各策略 6+ 月实盘 track record |

## 7. 待定问题

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| ATR 倍数按策略类型差异化（趋势宽/均值回归中/高频紧/Carry 宽） | 本备忘 §3.3 / BM-SELL-04-C | 待 G04（20_first_batch_strategies）产出校准 |
| 移动止损回撤 X% 按策略类型定 | 本备忘 §3.3/§3.4 | 待 G04 校准 |
| 时间止损 N 天按策略类型定（打板 1-2/多因子 5-10/事件 2-3） | 本备忘 §3.2 | 待 G04 校准 |
| 退潮信号注入 BM-SELL-03 的权重值 | 本备忘 §3.5 | 待 28 active |
| 35 Level 2/3 触发时，进行中的分批卖出如何处理 | 本备忘 §3.9 | 待 35 active |
| BM-SELL-06 弃用态（MOD-SELL-008 build_status=deprecated）的替代路径 | [68_d_sell_decision](../../02_domain_architecture_docs/68_d_sell_decision.md) | 待确认冲突仲裁是否迁移到融合引擎内。v1.6.0 源码核实补记：状态三方分裂——68 域文档标生产态 stable、源码 `sell_conflict_arbitrator.py` 标 [MATURITY] production 且无 deprecated 字样、仅 battle_map_07 锚点表标"真实 build_status=deprecated"（据此判 BM-SELL-06 弃用态）。源码与 68 文档一致（已建可用），弃用判定仅来自 depgraph 字段，需用户裁定以哪侧为真源 |
| risk 域 default_stop_loss_engine 与本 spec 止损族的替换/并存关系 | 本备忘 §2.4 跨域可复用设施 | 待 MOD-SELL-004/005 施工时裁定：risk 域已有 trailing/time_based/volatility 三方法简化实现（生产态），本 spec 的 Chandelier（ATR 自适应）施工后，两域止损逻辑是"替换"（sell_decision 新实现接管，risk 域旧实现退役）还是"并存"（risk 域管账户级硬止损，sell_decision 管策略级退出）——倾向并存（分层防御），施工时确认 |

> **循环至零检查**：42 → 41（G19 已 active）/35（G16 已 active 1.37.0，v1.6.0 订正）/28（G21 骨架）。35 框架在 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5（active）已定且 35 号 impl 已 active，28 退潮降级为 regime ⑧/⑨ 触发。**无真循环阻塞**，42 可独立施工。✓

## 8. 引用

### 8.1 相关 design_memo
- [41_buy_flow](41_buy_flow.md) —— 买入流（突破失败降级联动，G19 已 active）
- [40_execution_broker](40_execution_broker.md) —— 执行层下单对接与撮合（v1.6.0 补链：本 spec 卖出信号的**落地通道**——卖出信号→40 号订单分解/PricingPolicy 挂单价/MiniQmtBroker 发出；跌停排队优先级 §3.8 与 Kill Switch 清仓排序 §3.9 的最终执行依赖 40 号 OpenOrderResolver/PricingPolicy，均已施工）
- [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) —— 流动性危机检测（v1.6.0 补链：§3.9 Kill Switch"流动性危机→立即停止开仓仅允许平仓"的检测真源；LEVEL_3 逃生指令→执行层清仓）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) —— 回撤 Protocol（active 1.37.0，v1.6.0 订正——此前版本标"骨架"已过时；外层框架在 30 §2.5，内层代码阈值 5/10/15% 见 35 §3.2）
- [28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) —— 情绪周期退潮卖出（骨架，降级为 regime）
- [31_position_sizing](31_position_sizing.md) —— 仓位产出（卖出端响应仓位变化）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5 —— 回撤四级阈值/Kill Switch 框架真源（35 号 impl 已 active，框架口径以此为准）

### 8.2 相关域架构与 battle_map
- [68_d_sell_decision](../../02_domain_architecture_docs/68_d_sell_decision.md) —— D_SELL_DECISION 域 24 模块（13 生产态含 6 个包入口占位，真实业务生产态 7 个/11 设计态，§2.4 盘点）
- [battle_map_07_sell_flow](../battle_map/battle_map_07_sell_flow.md) —— BM-SELL-01 突破成败 / BM-SELL-04 止盈止损族 / BM-SELL-06 冲突仲裁
- [battle_map_06_buy_flow](../battle_map/battle_map_06_buy_flow.md) —— BM-BUY-04 分批建仓（突破失败降级联动）

### 8.3 开源实证参考
- **quantstock ATR Stop Loss Guide（2026-02）/ algovestiq Stop-Loss（2026-05）/ fairmontequities 5 Ways Stop Loss（2026-07）** —— ATR 倍数选择（日内 1.5×/波段 2×/趋势 3×）、14 周期行业标准、止损设在"论点失效位"非随机百分比、仓位由止损距离驱动、五法并存但 ATR+trailing 为优；印证 ATR 主选+固定%降级（§3.3/§3.4）
- **vibetrader Trailing Stop Strategy（2026-03）** —— trailing 不封顶、自动锁定利润、消除决策疲劳；趋势宽 5-10%/波段中 3-5%；印证移动止盈/止损统一（§3.4）
- **eastmoney 止损与资金管理（2026-07）** —— A 股短线 3-5%/中长线 8-15%，单笔风险 1-3%，组合熔断；与 35 四级阈值/单笔 2% 一致（§3.3/§3.9）
- **volatilitybox Volatility-Adjusted Stop Losses（2026-03）** —— ATR/Chandelier/Keltner 三法对比，595+ 标的 2018-2025 回测 ATR 倍数止损比固定%**减少 34% 过早止损**；倍数选择：剥头皮 1-1.5×/日内 1.5-2×/波段 2-3×/持仓 3-4×；印证 Chandelier Exit 统一 trailing（§3.3/§3.4）
- **journalplus ATR Trailing Stop Strategy（2026）** —— Chandelier Exit 默认 22 周期+3×ATR(14)；**5 天未移动 1×ATR 强制退出**时间止损；印证时间止损施工算法（§3.2）+ Chandelier 参数（§3.3）
- **tradersunion Chandelier Exit Guide（2026-08-03）** —— Chuck LeBeau 吊灯止损法综述；ATR 自适应波动率、趋势市场表现优；印证 Chandelier Exit 统一 trailing 设计（§3.3）
- **arrowalgo Scaling In and Out（2026-03）** —— 分批进入 25-33% 首仓+确认后加仓；退出 **1/3 止盈+保本+trailing 三步法捕获 85% 完整分批收益**；印证简单分批演进路径（§3.7）
- **itafx ATR Stop Loss Strategy（2026-06）** —— ATR×倍数止损→仓位由止损距离反推（risk/stop_distance=shares）；日内 1.5-2×/波段 2-3×；印证 ATR 倍数选择与仓位联动（§3.3/§5.1）
- **arXiv 2506.06356 Deep Learning Multi-Day Turnover A-Share（2026）** —— A 股多日换手量化算法，VIX-China 动态仓位缩放+网格搜索止盈止损；15.2% 年化/MaxDD<5%/Sharpe 1.87；VIX 缩放与 regime Shrinkage 思路一致，网格搜索止盈止损待 Phase 2 评估
- **TradeZella 止损方法对比（2026-07，100 笔回测）** —— 固定% 胜率 48%/PF 1.38 < ATR 1.5× 胜率 52%/PF 1.41 < 结构位止损（支撑/阻力下方）胜率 55%/PF 1.68；印证 Chandelier Exit（结构位+ATR 复合）优于纯 ATR 或纯固定%（§3.3）
- **markettriage Position Trading（2026-04）** —— 持仓 4-26 周用 3-ATR Chandelier Exit 优于固定 5% 和纯移动平均；单笔风险 1-2%；印证 Chandelier Exit 趋势策略 M 上浮 +0.5 设计（§3.3）
- **digitalninjasystems Swing Trading Stops（2026-06）** —— ATR 1.5-3× for swing（2× 平衡点）、2:1 RRR 最低、Fibonacci 1.272/1.618 扩展位止盈；印证 ATR 倍数 M=2.0-3.0 范围（§3.3/§5.1）
- **financefeeds Stop-Loss Percentage（2026-07-22）** —— 单笔风险 ≤2% 账户净值、ATR 1.5× 胜率 52%/PF 1.41、结构位 PF 1.68、10% 损需 11% 回本/25% 损需 33% 回本；印证 35 单笔 2% + Chandelier Exit 复合止损（§3.3/§3.9）
- **上交所交易规则 2026 修订（2026-07-06 生效）** —— §2.4.2 收盘集合竞价 14:57-15:00 不可撤单；本备忘卖出执行时序算法的合规基线（§3.8）
- **A 股日内波动 U 型分布（CSDN 2026-08-08）** —— 14:00-14:57 成交量逐渐走高、14:57-15:00 收盘竞价最高、做T 9:45-10:15 卖/13:30-14:30 买回；本备忘止盈尾盘集中+止损盘中立即+做T 错峰时序设计来源（§3.8）
- **2026 程序化交易新规（中基协 2026-07 权威确认 + CSDN 2026-08-08）** —— 高频认定 300 笔/秒 OR 20000 笔/日（"15笔/秒"系市场误传，中基协辟谣源自美国误传）、异常交易撤单率监控 50%；本备忘卖出执行合规约束来源，MVP 限价单+盘中立即执行天然合规（§3.8）
- **Conformal Kelly drawdown dial（[arxiv 2608.01494](https://arxiv.org/html/2608.01494v1)，2026-08-02）** —— conformal prediction 区间 downside miss 时降杠杆、MaxDD 27.7%→20.3%、slow per-asset rolling 优于 adaptive；本备忘阶段 7 ML 风控远期实证（§5.2）
- **CUSUM 策略衰减检测（[mathandmarkets 2026-02 Part 81](https://mathandmarkets.com/p/detecting-decay-in-real-time-when)）** —— CUSUM 单侧统计量 S⁺ₜ=max(0, S⁺ₜ₋₁+(μ₀-xₜ)-k)，k=0.5σ/h=4σ balanced；Sharpe~1 策略 50 交易日检测延迟（远优于滚动 Sharpe 6+ 月）；四检验对比（CUSUM/Page-Hinkley/Bayesian 变点/滚动 Sharpe）；本备忘阶段 8 策略衰减检测远期实证（§5.2）
- **Optimal SL/TP Parameterization（[Li, Laryea & Ihlamur 2026 arXiv:2604.27150](https://arxiv.org/abs/2604.27150)，Oxford + Vela Research）** —— 900+ 历史交易反事实模拟，8960 配置全网格搜索；最强配置 ATR 1.0× 止损+2.0× 止盈+连续 2 笔亏损 circuit-breaker 减仓因子 0.25；exit-rule tuning 是校准问题非启发式选择；本备忘策略级连续亏损熔断施工算法来源（§3.10）
- **Chuck LeBeau《Exit Strategies for Stocks and Futures》TradeStationWorld 演讲（一手出处）** —— Chandelier Exit 原作者本人材料：退出优先级四层（initial stop→trailing stop→profit protection stop→profit maximizing exit）；"My favorite initial stop is placed 2 or 3 ATRs below my entry point"；"Never let a large profit turn into a small profit. The bigger the profit the tighter the exit"——本 spec 亏损区宽 M=3.0/盈利区紧 M=2.0 双参数设计的一手理论原型（§3.3）
- **O'Neil 卖出法则 2026 三源**（[openswingtrading 2026-02](https://www.openswingtrading.com/blog/apply-william-o-neil-rules-in-20-minutes-daily) + befreed.ai CANSLIM podcast 2026-04 + eastmoney 威廉·欧奈尔体系 2025-11）—— -7~8% 固定止损无例外/+20~25% 止盈（1-3 周暴涨 20%+ 龙头例外持有 8 周）/跌破 50 日线卖出；本 spec §1 对标项的展开对比与不搬用论证（§3.3）；fxglory 2026-06 Chandelier Exit 22 周期 3×ATR 常见设置与 §3.3 参数表一致

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G20 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active，回填 8 项讨论要点 | 卖出时序(持仓分级+强制清仓绕过融合)/止损(ATR+移动,固定%降级,密度感知待裁定)/止盈(移动统一)/情绪退潮卖出(L2-B注入,与regime协同)/破位(突破成败已建)/分批(MVP一次性,待MOD-SELL-017)/T+1约束(跌停排队/做T例外)/回撤Protocol联动(35四级阈值);过度工程审查(四族MVP前三,分批降级);循环至零检查通过 |
| 2026-08-10 | 1.1.0 | 施工算法缺失补充 + 2026-08 前沿算法 + 选项之外更好的答案 | 补 Chandelier Exit 统一 trailing（§3.3/§3.4 一套公式两个参数，替代两套独立%回撤，volatilitybox 回测减少 34% 过早止损）+ 时间止损施工算法（§3.2 "5天未移动1×ATR"自适应阈值）+ Triage 分级判定算法（§3.2 ATR 距离驱动）+ 跌停板排队优先级（§3.8 紧迫度/亏损/仓位三维排序）+ Kill Switch 强制清仓排序（§3.9 流动性优先防封跌停）+ 简单分批演进路径（§3.7 "1/3止盈+保本+trailing"三步法）+ Keltner Channel 替代方案（§4.7）+ 7 篇 2026-08 开源实证 |
| 2026-08-10 | 1.2.0 | 卖出执行时序算法 + 结构位+ATR 复合实证 + 阶段 7 ML 风控远期 + 9 篇 2026-08 实证 | §3.3 补 TradeZella 结构位止损 PF 1.68 实证（Chandelier=结构位+ATR 复合，理论 PF 偏 1.68）+ markettriage 3-ATR Chandelier 持仓周期实证；§3.8 新增卖出执行时序算法（止损盘中立即/止盈尾盘集中/强制清仓市价立即，对齐上交所 2026 修订 14:57 不可撤单约束，与 41 号 §3.4 对称设计）+ 15 笔/秒合规约束；§5.2 新增阶段 7 ML 风控远期（Conformal Kelly drawdown dial，MaxDD 27.7%→20.3%，替代手工回撤四级阈值）；§8.3 补 9 项 2026-08 最新实证（TradeZella/markettriage/digitalninjasystems/financefeeds/上交所新规/U型分布/量化新规/Conformal Kelly） | 用户要求审查施工环节流程算法缺失、选项之外更好算法、2026-08-08 最新研究、文档结构内容调整 |
| 2026-08-10 | 1.3.0 | 新增阶段 8 CUSUM 策略衰减检测 + 四检验对比 | §5.2 新增阶段 8 CUSUM 策略衰减检测（mathandmarkets 2026-02 Part 81：S⁺ₜ=max(0, S⁺ₜ₋₁+(μ₀-xₜ)-k)，k=0.5σ/h=4σ，Sharpe~1 策略 50 交易日检测延迟远优于滚动 Sharpe 6+ 月）；区分"正常回撤"与"策略已死"，与 35 回撤 Protocol 正交（35=组合级止血/CUSUM=策略级诊断）；四检验对比表（CUSUM/Page-Hinkley/Bayesian 变点/滚动 Sharpe）；§6 待裁定新增 CUSUM 项；§8.3 补 CUSUM 实证 | 用户要求持续改进，补充策略衰减检测作为退出信号验证的选项外更好算法 |
| 2026-08-10 | 1.4.0 | 新增 §3.10 策略级连续亏损熔断 Circuit Breaker（选项外更优算法） | §3.10 新增策略级连续亏损熔断——补全时间熔断（日度/Kill Switch 按天计数）与交易熔断（按笔计数）之间的响应空档。来源 arXiv:2604.27150（Li/Laryea/Ihlamur 2026，Oxford+Vela Research，900+ 交易 8960 配置全网格搜索）实证最强配置：连续 2 笔亏损后 circuit-breaker 减仓因子 0.25。三层熔断分工表（交易级/日度/Kill Switch），TradeLevelCircuitBreaker 伪代码（consecutive_loss_threshold=2/reduction_factor=0.25/min_scale=0.25/reset_on_win=True），A 股适配（打板 N=2/多因子 N=3），与 CUSUM §5.2 正交（circuit breaker=急救止血/CUSUM=诊断结构性衰减），与回撤 Protocol §3.9 乘性叠加（budget×position_cap×circuit_breaker_scale×conformal_scale）。过度工程审查：仅 1 类~30 行非独立模块，MVP 可选施工 | 用户要求再次审查文档所有内容+施工环节流程算法缺失+选项外更好算法+全网搜索 2026-08-08 最新研究+持续改进不停。全网搜索发现 arXiv:2604.27150 是 exit-rule calibration 前沿实证，circuit breaker 连续亏损减仓是 42 号缺失的交易维度熔断（现有仅有时间维度），补全三层熔断闭环 |
| 2026-08-10 | 1.5.0 | 施工标注清理——"施工缺失补全"→"施工伪代码已补全" | §3.2 Triage 分级判定算法 / §3.8 跌停板排队优先级算法 / §3.8 卖出执行时序算法 / §3.9 Kill Switch 强制清仓排序算法 共 4 处标注从"施工缺失补全"更新为"施工伪代码已补全"——v1.1.0/v1.2.0 已补全全部伪代码（triage_position/rank_limit_down_orders/schedule_sell_order/rank_kill_switch_liquidation 四函数完整），标注为历史遗留未同步 | 用户要求再次审查文档所有内容+施工环节流程算法缺失+持续改进。核查发现 42 号 4 处算法伪代码早在 v1.1.0/v1.2.0 已完整补全，但"施工缺失补全"标注未同步更新造成"算法缺失"的误读。本次清理过时标注，准确反映施工状态 |
| 2026-08-10 | 1.5.1 | 伪代码精度审计——3 处修复 | ①§3.7 `simple_scaling_out` 删除冗余参数 `risk_reward_ratio`（函数体用 `position.risk_reward` 属性，参数未被引用）+ 补全 `compute_exit_price` 的 `highest_close_fn` 参数（原 `...` 省略导致调用不完整）；②§3.3 `compute_stop_loss` 补 `highest_close_fn` 签名说明（Callable[[int], float]，施工方注入，来源 K 线 close rolling max）；③§3.10 TradeLevelCircuitBreaker 表格修正（原"≥5 笔\|0+block"易误解为仓位归零，实际 get_position_scale 返回 min_scale=0.25，is_blocked 仅暂停开新仓，修正为"0.25+block"消除歧义）。边界条件审计：TradeLevelCircuitBreaker.get_position_scale 连续亏损 0-5 笔缩放计算逐笔验证正确（1.0/1.0/0.75/0.50/0.25/0.25）；rank_limit_down_orders/rank_kill_switch_liquidation 三级排序逻辑一致（流动性优先→亏损/仓位）| 七十二轮伪代码边界条件深度审计——换三个新角度（跨文档调用链验证/伪代码边界条件审计/参数来源追踪）发现 3 处精度缺陷，已修复 |
| 2026-08-10 | 1.5.2 | 伪代码崩溃 bug 修复——死参数+ATR None 崩溃 | ①§3.3 `compute_stop_loss` 删除未使用的 `symbol` 参数（死参数，函数体从不引用），补 `phase` 参数语义说明（与 §3.4 `compute_exit_price` 自动判定 phase 的分工边界）；②§3.4 `compute_exit_price` 修复 ATR None 崩溃 bug——原 `atr_pct = atr_value / position.entry_price if atr_value else 0.02` 仅兜底 atr_pct 但 return 行 `highest_close_fn(N) - M * atr_value` 在 atr_value=None 时 None×float 崩溃，补 ATR 缺失降级固定%逻辑与 §3.3 `compute_stop_loss` 对齐 | 伪代码边界条件深度审计第七十三轮——聚焦 None/空值/除零三类崩溃路径，发现 `compute_exit_price` ATR None 路径必崩（`if atr_value else 0.02` 兜底了 atr_pct 但 return 行仍用 None），与 §3.3 `compute_stop_loss` 的 ATR 缺失降级逻辑不一致。修复后两函数 ATR 缺失路径一致（均降级固定%），`symbol` 死参数清理 |
| 2026-08-12 | 1.6.0 | 已施工设施盘点新增 + MOD-SELL-014 状态订正 + 35 号状态订正 + 交叉引用补全 + O'Neil/LeBeau 对标展开 | 架构审查（通用规则 #11 基础设施盘点 + 一致性审查）：①**§2.4 新增「已施工设施盘点」**——sell_decision 域已施工 7 模块（突破成败 003/收集器 001/融合 007/紧迫度 009/冲突仲裁 008/猎杀防护 015/置换再平衡 006）+ 跨域可复用设施（risk 域 default_stop_loss_engine trailing/time_based/volatility 三方法 + position 域 TriageLevel 消费方）+ 未施工清单（9 项伪代码状态全标注）+ 与 40 号执行层落地边界；②**MOD-SELL-014 策略止损范式状态硬错误订正**（4 处：§2.3/§4.1/§5.2/§5.3）——此前版本标"已建"，源码核实三方分裂：68 域文档 planned 无代码无蓝图/battle_map generated 仅包入口/源码目录无实现文件，以 68 域文档为准=设计态待施工，MVP 用 Chandelier 阶段切换替代；③**35 号状态全面订正**（7 处：§1/§3.9/§5.2/§5.3/§7/§8.1/循环至零检查）——35 已 active 1.37.0（此前版本标"骨架/未就绪"已过时），阶段 3 触发条件已满足，§3.9 四级阈值与 30 §2.5 外层口径一致无需改数值，补 35 §3.2 内层代码 5/10/15% 双轨说明；④**§2.1 "13 生产态"精确化**——6 个为 __init__.py 包入口占位，真实业务生产态 7 个；⑤**§7 待定问题补 2 项**——MOD-SELL-008 三方分裂源码核实补记（源码 production 无 deprecated 字样）+ risk 域止损引擎与本 spec 替换/并存关系裁定请求；⑥**§8.1 补 40/37 号交叉引用**（40=落地通道/37=流动性危机检测真源）；⑦**§3.3 补 O'Neil 卖出法则对比论证 + LeBeau 一手出处**——§1 对标项"O'Neil 卖出法则"此前只有标题未展开，补 7-8% 固定止损/+20-25% 止盈/8 周例外三规则的不搬用论证（A 股 T+1+涨跌停缺口）+ LeBeau 退出优先级四层与"利润越大止盈越紧"是 Chandelier 双 M 值设计的一手原型；§8.3 补 LeBeau 演讲 PDF + O'Neil 三源条目。⑧**2026-08 最新研究五次复查**——WebSearch 确认 journalplus/volatilitybox/fxglory Chandelier 参数与 §3.3 一致、Li 2026 circuit breaker 已登记、miniQMT/执行算法无新内容，无新硬错误 |
| 2026-08-12 | 1.6.1 | 作战地图全覆盖补丁——BM-SELL-09 / BM-POS-09 | ①新增 §3.11 卖出闭环优化（BM-SELL-09）——卖后 N 天价格追踪窗口（默认 5 交易日校准项）/按信号类型×策略分组准确率统计/A-B 显著性检验 p<0.05（单格样本<30 不出建议）/执行质量评分，产出 E-SELL-04 SellLoopFeedback 回调 BM-SELL-03 信号权重（仅 p<0.05 生效、单次 ±20% 封顶）；调度复用 55 号 §3.6 复盘编排器（daily→weekly→monthly 链路+ReportPublisher 归档），显著性框架复用 54 号 §3.9 deflated-alpha（日常轻量 p 检验+月/季重量 audit() 分层）；②§3.3 扩展卖出阈值双向反馈契约（BM-POS-09）——PositionStateFeedback→D-SELL-DECISION 阈值动态调整五字段（pnl_state/unrealized_pnl_pct/threshold_delta∈±0.10 硬封顶/feedback_window/source_position_id）+方向规则（盈利放宽/亏损收紧/breakeven 不动，强制清仓不经本契约）+买入后即时验证窗口三级递进（5min 跌破>1% 放量→OBSERVING/15min 破分时均线→减仓 50%/30min 反向>2ATR→全部止损，与软止损共用四态机不新建）。均补定位→裁定（理由+重评条件）→契约/参数→降级四层 |
| 2026-08-12 | 1.6.2 | 作战地图环节映射补强——锚定 BM-RC-05-A | §3.3 末尾补映射块，环节级可追溯 |
| 2026-08-13 | 1.7.0 | MVP 施工落地——4 模块 65 测试全绿（AI-SELL-001） | §2.4 未施工清单 9 项中 7 项落码：MOD-SELL-000 持仓Triage（§3.2 triage_position，import 消费方 MOD-POS-003 TriageLevel 真源唯一，ATR缺失降级MONITOR，threshold_delta 硬封顶±0.10）/ MOD-SELL-005 止损族（§3.3 Chandelier 统一+策略M±0.5+§3.2 时间止损第⑦类源）/ MOD-SELL-004 止盈族（§3.4 自动phase判定委托005）/ MOD-SELL-019 执行编排（新登记，§3.8 时序+T+1/跌停硬约束+§3.9 Kill Switch清仓排序）；3 处工程修正（triage绝对距离比较消浮点尾差/ATR缺失降级MONITOR/执行编排落地表格约束）；MOD-SELL-014/017/circuit breaker 维持 spec 裁定不施工；三登记齐备（depgraph 节点+边/creation_token×12/plain_zh×4/ARCH-SELL-001） |
| 2026-08-14 | 1.7.1 | 遗留登记完备性补修（#ARCH-SELL-001 治本方案 P1-4） | §5.2 补阶段 5b（MOD-SELL-014 启用触发=G04 参数校准产出，原仅散见 §2.3/§5.3/§7）+ 阶段 5 触发条件补量化口径注记；§6 "G04 策略类型定稿"措辞勘正为"G04 按策略类型的参数校准产出"（20 号已 active，字面误读风险）；TradeLevelCircuitBreaker 补登 CAND-SELL-001（孤儿决策收口）；battle_map_07 BM-SELL-04-C 文案三方分裂——派生文件不入 git，depgraph MOD-SELL-014=planned 为真源，随下一次 battle_map 重生成自动订正 |
| 2026-08-15 | 1.7.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-07） | 过程性叙述/重复实证/冗余修饰清理，标题编号/关键数值（四族 MVP/四级回撤 8%/15%/20%/25%/阶段 7-8 远期）/裁定/开放问题/BM-XXX/#ARCH-XXX/跨文档链接零丢失 |
