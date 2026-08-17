---
ttl: permanent
doc_type: architecture_view
title: 流动性危机处理
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.1"
date: 2026-08-17
topic: liquidity_crisis_protocol
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-14 第三批施工（会话 AI-LIQ-001，4 笔提交合并回 dev），MOD-RK-21 六算法 + 54 测试，本档升 v1.1.0（3 处文档缺陷同步修复）。
>
> **最终成果**：MOD-RK-21 生产态；54 测试经统筹独立复跑全绿；买卖价差监控、危机响应（停止开仓仅允许平仓）全链落地。
>
> **未做事项及原因**：
> - ~~LEVEL_3（最高级危机处置）生产接线未做——P0 风控接线批遗留，待后续批次。~~ **✅ 已闭环（2026-08-17 AI-LVL3-001，v1.2.0）**——`detector.check()` 嵌入 `risk_layer_orchestrator.evaluate_intraday`（与 VaR/ES/回撤同层），LEVEL_3 → `build_escape_directive` → `_engage_kill_switch` 单一仲裁点 → `execute_kill_switch_liquidation` 真实清算全链接通；§3.6 降级机接线（LEVEL_3→LEVEL_2 冷却 30min+信号≤2+spread<0.3%，复用 MOD-RK-21 `check_recovery`/`LiquidityRecoveryState`，降级只迁移警报级别不解除熔断闩锁——35 号 KILL 态人工复位不变式保持）。红队三向量非 mock 实证 16 项全绿（多信号 LEVEL_3 全链/情绪断路器 0.85 强制升级/冷却期逐级降级+非 LEVEL_3 逃逸守卫）。
> - ~~IPO 数据源接入未做~~ **✅ 已闭环（2026-08-17 AI-IPO-001，tracker #114）**——akshare `ipo_calendar` capability 落地（巨潮 `stock_new_ipo_cninfo` 替代源），c1_market.ipo_calendar 日快照表 + 盘后调度任务 + DS-105/JOB-086 数据资产登记；消费侧 `compute_ipo_liquidity_drain` 按 list_date+raise_amount 读取最新快照即可注入 IPOEvent。
> - ~~编排层接入 35 号 §3.13 调用方~~ **✅ 并入 AI-LVL3-001 闭环**——35 号 §3.13 盘中循环的生产载体即 trading_session 调仓循环 + orchestrator.evaluate_intraday，systemic 评估已内嵌同 tick（tracker #42① 重叠项并入施工）。

# 流动性危机处理

> 本备忘记录"流动性危机识别→响应"的选型推理与上限定义。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 上游：[30_multi_strategy_concurrency §2.5.5](30_multi_strategy_concurrency.md) Kill Switch 流动性危机触发条件（买卖价差 > 正常 5x → 立即停止开仓，仅允许平仓）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G18 流动性危机处理 |
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5.5 |
| 依赖 | G16（[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)，active v1.0.0，§3.5 Kill Switch 触发条件已填，含流动性危机行反向引用本备忘） |
| 对标 | tradingwyckoff Kill Switch / 机构流动性风控 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P3 |
| 状态 | active 1.2.0（5 项讨论要点定型 + G16 对齐 + 涨跌停算法断裂修复 + 逃生执行器 + 危机恢复算法 + sell_pressure/spread/涨跌停形式化 + §3.7.x 前沿评估 16 项（Hawkes/VPIN/Crumbling/SaR/Latent build-up/ExsdHawkes/Liquidation Cascade/Multiplex Hawkes/临界性异质性/Weng 羊群/Zhou 操纵周期/LRISK/欧洲 ML/AdjPIN/Kyle λ/流动性尾部/跨市场传染 BM-RC-12-B）+ §3.8 施工流程总览 + §2.4 指数熔断澄清与 LAN 通道关闭交叉引用 + **v1.1.0 施工落地**：MOD-RK-21 承载六项算法（检测委托 MOD-RK-10），修 §3.1.1 公式 + §3.8 涨跌停 spread 矛盾 + §3.2a 数据源虚标 + v1.1.2 第二轮循环压缩（AI-DC2-05）+ **v1.2.0 LEVEL_3 生产接线闭环**（AI-LVL3-001：detector.check 嵌入 orchestrator 盘内评估链+逃生链接通 Kill Switch+§3.6 降级机接线，红队三向量实证）） |

## 2. 背景

### 2.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道），资金体量小
- 多策略并发架构 Model A 已定稿（30_multi_strategy_concurrency）：各 StrategyBook 输出 target_portfolio → FirmRiskAggregator 求和裁剪 → firm_target_portfolio → 下单
- 流动性风控基础设施**已 production**，本备忘不是从零设计，而是给已有实现补 why 层 + 对齐 §2.5.5 spec

### 2.2 现有资产盘点（施工前已实现，本备忘为其补 why 层）

| 层次 | 模块 | path | 状态 | 职责 |
|---|---|---|---|---|
| 盘内紧急 | AshareSystemicRiskDetector | `src/zephyr/risk/core/ashare_systemic_risk_detector.py` | 🟦 production | 5 大信号扫描（含 LIQUIDITY_CRISIS）+ 三级警报 + LEVEL_3 联动 Kill Switch |
| 日频结构 | LiquidityMonitor | `src/zephyr/risk/core/liquidity_monitor.py` | 🟦 production | Amihud 非流动性指标 + 成交量萎缩比率 |
| Kill Switch | （BM-RC-03） | `src/zephyr/risk/stop_loss.py` 等 | 🟦 production | 回撤/VaR/Owner 触发，冷却 30 分钟 |
| 盘前拦截 | BM-RC-02-E | `src/zephyr/risk/implementations/` | 🟦 production | Kill Switch 状态检查，拉闸时拒新单 |
| 盘内编排+恢复+预警 | LiquidityCrisisManager | `src/zephyr/risk/core/liquidity_crisis_manager.py` | 🟦 production（MOD-RK-21，2026-08-13 施工，commit d53693a1，测试 54 项） | §3.1.1 卖压/§3.1.2 价差/§3.5.1 涨跌停检测/§3.6 危机恢复/§3.8 盘中编排/§3.2a IPO 抽离预警——检测委托 MOD-RK-10（真源唯一） |

### 2.3 核心问题
流动性危机要回答 5 个问题（§7 讨论要点）：
1. 买卖价差怎么监控（>正常 5x 触发）？
2. 流动性危机来了做什么（停开仓仅平仓）？
3. 流动性指标怎么定义（换手率/成交额/盘口深度）？
4. 与 Kill Switch 是什么关系？
5. A 股涨跌停的流动性失效怎么处理？

### 2.4 约束条件
- **§2.5.5 spec**（30_multi_strategy_concurrency）：流动性危机（买卖价差 > 正常 5x）→ 立即停止开仓，仅允许平仓。Kill Switch 原则：宁可错杀不可漏放，触发即执行不允许人工覆盖延迟。
- **A 股涨跌停流动性失效**：涨停板买单堆积排不上、卖单稀缺；跌停板卖单堆积卖不出、买单稀缺——涨跌停时盘口退化为单价位，spread 监控失效。
- **A 股无市场级指数熔断**：A 股指数熔断机制于 2016 年 1 月 7 日暂停实施（仅运行 4 个交易日因磁吸效应加剧暴跌而废止），现行波动控制依赖**个股涨跌停板**（主板±10%、创业板/科创板±20%、北交所±30%、ST±5%）及**盘中临时停牌**（新股上市首日/盘中异常波动）。本协议中的"熔断"（如 BM-RC-03 Kill Switch 熔断）指**策略级**流动性危机响应，非市场级指数熔断——策略须自建断路器而非依赖交易所熔断机制。
- **个人小资金**：多数订单远小于 1% ADV，自身交易不构成流动性冲击；流动性危机是**市场级**事件（融资盘平仓潮/量化踩踏），不是自身容量问题。
- **AI 开发**：故障隔离是生存项——流动性危机检测必须有兜底，不能依赖单一数据源。
- **2026-07-31 交易所 LAN 通道关闭（v1.0.9 新增交叉引用）**：上交所关闭机房内局域网交易行情线路统一切换广域网，硬约束：广域网线路双向时延 ≥2ms（含存量+新增，旧机房内网直连 0.13ms-10μs），物理链路层抹平微秒级抢跑优势；首日成交 2.56 万亿→2.01 万亿（缩 5488 亿），纯超高频量化超额 14%→3% 以内，量化行业从"拼网速"→"拼研究"。**对流动性的直接影响**：① 流动性收缩使大额强裁冲击成本上升——[33_budget_change_handler](33_budget_change_handler.md) §3.2.3 `TWAP_LARGE_ORDER_THRESHOLD` 从总资产 5% 下调至 3-4%（保守自限，留冲击余量）；② 高频做市商超额压缩退场、盘口深度可能变薄——§3.1.2 Quoted Spread 阈值 0.5% 须在上线后 3 个月重新校准（旧阈值基于高频做市商活跃盘口，新结构下 spread 中枢可能上移）；③ §3.7 Hawkes"高活跃期延续趋势"判定（[arXiv:2512.08000](https://arxiv.org/abs/2512.08000) A 股实证）需在新流动性结构下重新拟合基线。与 [00_index §3 G22⑨](00_index_trading_decision.md) + [40_execution_broker](40_execution_broker.md) + [33_budget_change_handler §3.2.3](33_budget_change_handler.md) 三方对齐。

## 3. 决策

### 3.1 决策①：盘内流动性危机检测——复用 MOD-RK-10 LIQUIDITY_CRISIS 信号

**决策**：复用已实现的 [AshareSystemicRiskDetector](file:///d:/ZephyrAlpha/src/zephyr/risk/core/ashare_systemic_risk_detector.py)（MOD-RK-10，production）的 LIQUIDITY_CRISIS 信号，作为盘内流动性危机检测主路径。**不新建**独立 LiquidityCrisisProtocol 模块。

**已实现能力**（代码已实现）：
- `_check_liquidity_crisis(sell_pressure, bid_ask_spread)`：**双条件 AND** 触发——卖盘压力 `>= 0.65` 且买卖价差 `>= 0.005 (0.5%)`，两者同时满足才判定流动性危机
- `bid_ask_spread` / `sell_pressure` 作为 `detect()` 的**输入参数**由上游数据层提供（MOD-RK-10 不自行计算 spread，只做阈值判定）
- 三级警报按触发信号数递进：1 信号 → LEVEL_1 停开仓 / 2 信号 → LEVEL_2 降仓 30% / ≥3 信号 → LEVEL_3 清仓 + 联动 Kill Switch
- 情绪断路器：情绪指数超阈值（0.85）→ 强制升级至 LEVEL_3

**为何双条件 AND + §2.5.5 "5x" 与 "0.5% 绝对" 的对齐**：单看 spread 扩大可能是低流动性票常态（误报高），单看卖压可能是正常调仓，两者同时出现才是流动性正在枯竭（与 §2.5.5"价差 > 正常 5x"方向一致：价差异常扩大是必要条件，叠加卖压是充分条件）；§2.5.5 的"5x"是方向性 spec（需维护 N 日均价差基准），代码用绝对阈值 0.5%（简单稳健）——A 股正常票 spread 通常 0.01-0.05%（1-5 个 tick），0.5% 已是 10-50 倍正常水平，与"5x"量级吻合；MVP 用绝对阈值，Phase 1.5 可上推相对阈值（spread / N 日均价差 > 5x）若误报多（§4.4）。

#### 3.1.1 sell_pressure 形式化定义（v1.0.3 补全）

> ✅ 已施工（`liquidity_crisis_manager` MOD-RK-21 `compute_sell_pressure`，54 测试全绿，2026-08-13）——接口：`sell_pressure(bid_volumes, ask_volumes) -> float`，公式定义如下（算法语义真源在本文档）。

**定义与算法——OBI 反转**（Order Book Imbalance，[Polymarket 2026-06](https://polymarket.com) 流动性监控引擎）：sell_pressure 衡量盘口卖方主导程度，范围 [0, 1]，1 = 纯卖压。

```python
def sell_pressure(bid_volumes: list[float], ask_volumes: list[float]) -> float:
    """卖盘压力 = 卖方挂单占比（OBI 反转）
    
    OBI = (ΣVolBid - ΣVolAsk) / (ΣVolBid + ΣVolAsk)
    sell_pressure = ΣVolAsk / (ΣVolBid + ΣVolAsk) = (1 - OBI) / 2
    
    v1.1.0 修：原文写作 "sell_pressure = 1 - OBI = 2 × ΣVolAsk/(ΣVolBid+ΣVolAsk)"——
    代数错误（1-OBI 值域 [0,2]、均衡点 1.0，与本节声明的值域 [0,1]、均衡点 0.5、
    0.65 阈值语义均不自洽）。施工按正确口径 ΣVolAsk/(ΣVolBid+ΣVolAsk) 落码，
    与阈值语义自洽（0.65 = 卖单占 65%/买盘仅占 35%）。
    
    Args:
        bid_volumes: 多档买盘挂单量（如 5 档买一至买五）
        ask_volumes: 多档卖盘挂单量（如 5 档卖一至卖五）
    Returns:
        sell_pressure ∈ [0, 1]：0=纯买压，1=纯卖压，0.5=均衡
    """
    total_bid = sum(bid_volumes)
    total_ask = sum(ask_volumes)
    total = total_bid + total_ask
    if total == 0:
        return 0.5  # 无盘口数据，返回中性值不触发
    return total_ask / total  # = (1 - OBI) / 2
```

**为何用 OBI 反转而非成交量比率**：OBI 基于盘口挂单（限价单队列），是**瞬时**流动性画像；成交量比率是**滞后**指标（成交已发生，来不及预警）；miniQMT `xtdata.get_full_tick` 提供 5 档买卖盘挂单量可直接计算；0.65 阈值 = OBI 0.35（买盘仅占 35%），与 Polymarket `<0.40 卖压主导`阈值量级一致。**替代算法——OFI 一阶差分**（[ClusterLOB 2026-06](https://clusterlob.com)，Phase 1.5 储备）：`OFI_t = Δ(Q_bid_t) - Δ(Q_ask_t)`，正=买压升、负=卖压升——sell_pressure 衡量静态存量，OFI 衡量动态变化趋势，两者互补（静态超阈值触发 + 动态急剧恶化提前预警）。

#### 3.1.2 spread 形式化定义（v1.0.3 补全）

> ✅ 已施工（`liquidity_crisis_manager` MOD-RK-21 `compute_bid_ask_spread`，54 测试全绿，2026-08-13）——接口：`bid_ask_spread(bid_price, ask_price) -> float | None`，公式定义如下。

**定义与算法——Quoted Spread**（最基础、与代码阈值同量纲）：bid_ask_spread 衡量盘口即时交易成本，与 0.5% 阈值量纲一致。

```python
def bid_ask_spread(bid_price: float, ask_price: float) -> float | None:
    """买卖价差 = (ask - bid) / mid
    
    Args:
        bid_price: 买一价（最优买价）
        ask_price: 卖一价（最优卖价）
    Returns:
        spread ∈ [0, +∞)：0=无价差（理想流动性），>0.005=流动性危机阈值
        None: 盘口缺失（涨跌停/停牌），由调用方按 §3.5 规则处理
    """
    if bid_price is None or ask_price is None or bid_price <= 0:
        return None  # 盘口缺失，§3.5 涨跌停处理接管
    mid = (bid_price + ask_price) / 2
    if mid <= 0:
        return None
    return (ask_price - bid_price) / mid
```

**为何用 Quoted Spread 而非 Effective Spread**：Quoted Spread = (ask-bid)/mid 直接从盘口读取**零延迟**；Effective Spread = 2×|成交价-mid|/mid 需等成交后计算**滞后**——危机检测需要领先信号（盘口 spread 扩大先于成交价恶化）；miniQMT `get_full_tick` 直接提供买一/卖一价。**涨跌停特殊处理**（与 §3.5 对齐）：跌停板 `bid_price` 可能缺失（无买单）→ spread 置 **1.0**（大值，使 AND 条件可满足）；涨停板 `ask_price` 可能缺失（无卖单）→ spread 置 **None**（跳过检查，涨停不触发危机）；停牌两者均缺失 → spread 置 None。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-RC-06-A | 五大信号扫描 | §3.1 决策① 盘内流动性危机检测（MOD-RK-10 五信号扫描+三级警报） | production 已建 |

### 3.2 决策②：日频结构性流动性监控——复用 MOD-RK-08 LiquidityMonitor

**决策**：复用已实现的 [LiquidityMonitor](file:///d:/ZephyrAlpha/src/zephyr/risk/core/liquidity_monitor.py)（MOD-RK-08，production）的 Amihud 非流动性指标 + 成交量萎缩比率，作为日频结构性流动性恶化监控。

**已实现能力**（代码已实现）：
- `compute_amihud(closes, volumes)`：Amihud ILLIQ = |r_d| / V_d 的 N 日均值（r_d=日收益率，V_d=日成交额），ILLIQ 越高越不流动
- `compute_volume_shrinkage(volumes)` + `assess(symbol, ohlcv, bid_ask_spread)`：V_ratio = V_t / MA(V, N)（<1=萎缩，<0.5 判定萎缩）；is_illiquid = Amihud 超阈值(1e-8) OR 成交量萎缩(<0.5)；`bid_ask_spread` 为可选外部输入（MOD-RK-08 不自行计算）；纯机制零参数，阈值/窗口为 C 类参数可在构造时覆盖

**与 MOD-RK-10 的互补关系**：MOD-RK-10 管盘内紧急（卖压+价差扩大），MOD-RK-08 管日频趋势（Amihud+成交量萎缩）——时间尺度互补不重叠。**为何需要日频层**：盘内检测只能抓"正在发生的危机"，日频监控提前发现"流动性正在恶化"的趋势，给策略层调整持仓的时间窗口（逐步减仓流动性变差的票，而非等危机爆发才被动停开仓）。

### 3.2a IPO 流动性抽离预警（v1.0.15 新增——前瞻性流动性监控）

> ✅ 已施工（`liquidity_crisis_manager` MOD-RK-21 `compute_ipo_liquidity_drain` + `IPOEvent`，54 测试全绿，2026-08-13）——接口：`compute_ipo_liquidity_drain(upcoming_ipos, market_avg_volume_20d) -> (drain_ratio, drain_level, position_cap_adjustment)`；数据源接入待裁定，见 §6。

> **缺口背景**：final_report_0724 实证 2026-07-27 长鑫科技（688825）科创板上市（募资 579-666 亿，吸金 500 亿+）——此类**事件型流动性抽离**无法被 Amihud/spread/sell_pressure 事后检测捕获（等 spread 扩大时 IPO 已吸完），需**前瞻性**预警（上市日前已知 IPO 日历+募资规模）提前调整仓位上限。

**为何 IPO 虹吸不同于常规流动性危机**：

| 维度 | 常规流动性危机（§3.1-§3.2） | IPO 流动性抽离（§3.2a） |
|---|---|---|
| 检测方式 | 事后（spread 扩大/Amihud 飙升/OBI 反转） | **前瞻**（IPO 日历+募资规模上市日前已知） |
| 时间尺度 | 秒级-日频（突发性） | 日级-周级（可预知性） |
| 影响范围 | 个股或板块 | **全市场**（大型 IPO 吸金影响全市场流动性） |
| 响应动作 | 停开仓仅平仓（被动） | **提前布局+保留现金**（主动） |
| 可逆性 | 危机后逐步恢复 | IPO 虹吸 day 5 后自然衰减 |

**算法：IPO 流动性抽离预警**

```python
def compute_ipo_liquidity_drain(upcoming_ipos, market_avg_volume_20d):
    """计算未来 N 日 IPO 流动性抽离预警

    Args:
        upcoming_ipos: list[IPOEvent], 未来 5 个交易日内即将上市的 IPO
        market_avg_volume_20d: float, 全市场 20 日均成交额（亿元）

    Returns:
        drain_ratio: float, 未来 5 日 IPO 募资总额 / 全市场日均成交额
        drain_level: str, "NEGLIGIBLE" / "MODERATE" / "SEVERE" / "EXTREME"
        position_cap_adjustment: float, 仓位上限调整系数（1.0=不变, 0.75=降至75%）
    """
    total_raise = sum(ipo.raise_amount for ipo in upcoming_ipos if ipo.listing_date <= today + 5)
    drain_ratio = total_raise / market_avg_volume_20d

    if drain_ratio < 0.01:
        drain_level = "NEGLIGIBLE"
        position_cap_adjustment = 1.0    # 无需调整
    elif drain_ratio < 0.02:
        drain_level = "MODERATE"
        position_cap_adjustment = 0.90   # 微降 10%
    elif drain_ratio < 0.03:
        drain_level = "SEVERE"           # 长鑫 666/27000≈2.5%
        position_cap_adjustment = 0.75   # 降 25%，保留现金（final_report "保留25%现金"纪律化）
    else:
        drain_level = "EXTREME"
        position_cap_adjustment = 0.60   # 降 40%，极端虹吸

    return drain_ratio, drain_level, position_cap_adjustment
```

**与 [26_event_driven §2.5a](26_event_driven_strategy_detail.md) 的联动**：26 号管"alpha 方向+仓位策略"（IPO 上市前主仓位布局+保留现金+上市后存量板块降仓），37 号管"流动性检测+仓位上限节流"（drain_level→position_cap_adjustment）——互补：26 号是事件驱动 sleeve 主动策略，37 号是 firm 层被动仓位上限。

**与 §3.2 的区别及数据源**：§3.2 Amihud/成交量萎缩是**事后**检测（流动性已恶化），§3.2a 是**事前**预警（上市日前已知募资规模→提前算 drain_ratio），时间轴正交。✅ 数据源 v1.2.1 已接入（2026-08-17 AI-IPO-001，tracker #114）——v1.1.0 施工核查曾实证原文声称的 `stock_ipo_info` capability 不存在；本版以替代源巨潮 `stock_new_ipo_cninfo`（匿名、沪深北全市场）落地 `ipo_calendar` capability：c1_market.ipo_calendar 日快照（trade_date 锚定 PIT strict，list_date=NULL=未定档，raise_amount 亿元=发行价×总发行数量/1e4 派生），tasks.yaml `ipo_calendar_daily` 盘后调度。消费侧从最新快照构造 IPOEvent 列表注入即可。科创板/创业板前 5 日无涨跌幅限制是规则硬编码。

### 3.3 决策③：流动性危机响应——停开仓仅平仓（对齐 §2.5.5 + LEVEL_1）

**决策**：流动性危机触发后，响应动作 = **立即停止开仓，仅允许平仓**，对齐 §2.5.5 spec 与 MOD-RK-10 LEVEL_1 警报。**响应动作映射**（MOD-RK-10 三级警报）：

| 警报级别 | 触发条件 | position_cap | 响应动作 | 与 §2.5.5 对齐 |
|---|---|---|---|---|
| LEVEL_1 | 1 信号（含 LIQUIDITY_CRISIS 单独触发） | 1.0（现有仓位不动）+ 新开仓 0% | **停开仓仅平仓** | ✅ 对齐"流动性危机→停止开仓仅允许平仓" |
| LEVEL_2 | 2 信号 | 70%（降仓 30%） | 减仓 30% | 比 §2.5.5 更严（叠加多信号时升级） |
| LEVEL_3 | ≥3 信号 或 情绪断路器 | 0%（清仓） | 清仓 + 撤单 + 暂停 + Kill Switch | 对齐 Kill Switch"宁可错杀"原则 |

> **注**：LEVEL_1 的 `position_cap=1.0`（代码字段值），"新开仓 0%"是独立的动作位（`halt_new_orders` 语义），不改变 position_cap。即：现有仓位不受强制减仓，但禁止新建仓。

**为何 LEVEL_1 是"停开仓"而非"清仓"**：§2.5.5 明确"停开仓仅平仓"；危机时强行清仓会踩踏（卖在最低点）扩大损失；停开仓+允许平仓 = 不加新仓但允许策略主动减仓（平仓是策略决策非强制）；只有 ≥3 信号（系统性崩盘）才升级清仓（LEVEL_3，"跑得快"比"卖得好"重要）。LEVEL_1"仅允许平仓"是**允许**不是**强制**——强制平仓会剥夺策略决策权且必然踩踏（直接清仓的拒绝理由见 §4.3）。

**逃生执行器（LEVEL_3 专属，已实现 + 已接线）**：LEVEL_3 触发时 `AshareSystemicRiskDetector.build_escape_directive(alert)` 产出逃生指令字典，供 RK-17 Kill Switch 执行：

> ✅ **生产接线已落地**（2026-08-17 AI-LVL3-001，v1.2.0）：`risk_layer_orchestrator.evaluate_intraday` 内嵌 `detector.check()`（systemic_detector+systemic_input_provider 成对注入即生效），迁移进入 LEVEL_3 时 `build_escape_directive` → `_engage_kill_switch` 单一仲裁点 → `execute_kill_switch_liquidation`（以券商实时持仓为准，15 笔/秒限频）——逃生指令语义（liquidate_all+cancel+halt）与仲裁点既有动作一一对应，重复触发仲裁点幂等。

```python
{
    "directive": "escape",              # 指令类型：逃生
    "action": "liquidate_all",          # 动作：全部清仓
    "position_cap": 0.0,                # 仓位上限：0%（清仓）
    "cancel_pending_orders": True,      # 撤销所有未成交挂单
    "halt_new_orders": True,            # 暂停新下单
    "kill_switch_required": True,       # 需联动 Kill Switch
    "reason": alert.action,             # 触发原因（人类可读）
    "triggered_signals": [...],         # 触发的信号列表
    "timestamp": alert.timestamp.isoformat(),
}
```

- **守卫/消费者/数据流**：非 LEVEL_3 调用 `build_escape_directive` 抛 `InvalidSystemicRiskInputError`（逃生指令仅 LEVEL_3 可产出）；RK-17 Kill Switch（MOD-RK-17）接收逃生指令 → 执行清仓+撤单+暂停+冷却 30 分钟；链路：`check()` → `SystemicRiskAlert(LEVEL_3)` → `build_escape_directive(alert)` → RK-17 执行

### 3.4 决策④：与 Kill Switch 的关系——流动性危机不直接触发 Kill Switch

**决策**：流动性危机（LIQUIDITY_CRISIS 信号）**单独触发时为 LEVEL_1（停开仓），不联动 Kill Switch**；只有 ≥3 信号同时触发（LEVEL_3）才联动 Kill Switch 清仓。

**Kill Switch 触发条件**（battle_map_09 BM-RC-03，production）：回撤超 Emergency 阈值 / VaR 超限且无法减仓 / Owner 手动。

**差异对齐**：⚠️ BM-RC-03 触发条件中**不直接包含"流动性危机"**——危机通过 MOD-RK-10 的 LEVEL_3（≥3 信号）间接联动 Kill Switch 而非直接触发，与 §2.5.5 存在细微差异但属合理细化、不违反 spec 精神：

- **§2.5.5 spec**：流动性危机列为 Kill Switch 4 触发条件之一（单日亏损>6% / 回撤>25% / 连续5天亏损 / 流动性危机）
- **代码实现（更精细）**：危机单独 = LEVEL_1 停开仓（对应 §2.5.5"停开仓仅平仓"）；危机+其他 ≥2 信号 = LEVEL_3 清仓+Kill Switch（对应"宁可错杀"原则）——危机单独时清仓会踩踏，叠加多信号才升级
- **G16 已对齐**：[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) §3.5 多源触发表"流动性危机"行反向引用本备忘（买卖价差 > 正常 5x → G18），双向引用已建立，确认危机经 LEVEL_3 间接联动 Kill Switch 与本节一致

**为何不直接 Kill Switch**：Kill Switch = 清仓+暂停+冷却 30 分钟（BM-RC-03-B），是核按钮；危机单独发生（如某票突发利空 spread 扩大）时停开仓已足够保护，Kill Switch 留给"系统性崩盘"（≥3 信号）——分级响应比一刀切更合理。

### 3.5 决策⑤：A 股涨跌停流动性失效处理

**决策**：A 股涨跌停时 spread 监控**失效**（盘口退化为单价位），涨跌停本身即流动性危机子类，由执行层 [40_execution_broker](40_execution_broker.md) 决策⑥⑭处理，不在 G18 重复定义。**涨跌停流动性失效机制**：

| 场景 | 盘口状态 | spread 监控 | 流动性含义 |
|---|---|---|---|
| 涨停板 | 只有涨停价一个买价位，卖单稀缺/消失 | 失效（无卖一价，spread=∞ 或未定义） | 买不进（排队），可卖（有人挂涨停买） |
| 跌停板 | 只有跌停价一个卖价位，买单稀缺/消失 | 失效（无买一价，spread=∞ 或未定义） | 卖不出（排队），可买（有人挂跌停卖） |
| 接近涨停 | 买一/卖一价差正常但买一堆积巨量 | 正常但失真（spread 小但不代表流动性好） | 即将买不进 |
| 接近跌停 | 买一/卖一价差正常但卖一堆积巨量 | 正常但失真 | 即将卖不出 |

**与执行层的协同**（40_execution_broker 已覆盖）：决策⑥拒单分类——涨停(50)/跌停(51)拒单不重试直接放弃（排不上，重试无意义）；决策⑭挂单价——涨停板卖单挂涨停价、跌停板买单挂跌停价（唯一可成交价位）；决策⑮临时停牌——跨日停牌核查移除目标+释放资金预占。

**G18 的补充约束**（执行层未覆盖的）：
- **涨跌停时 MOD-RK-10 的 bid_ask_spread 输入处理**：跌停时（卖压≈1.0）应将 `bid_ask_spread` 置为**大值（如 1.0=100%）**而非 None——双条件 AND（`sell_pressure >= 0.65` AND `spread >= 0.005`）才可满足，LIQUIDITY_CRISIS 正常触发。**若置 None 则代码跳过检查（`if sell_pressure is not None and bid_ask_spread is not None`），信号无法触发**——这是 v1.0.2 修复的算法断裂。涨停时（买压主导，卖压低）不触发危机，spread 置 None 跳过检查即可。
- **持仓票跌停 = 流动性危机子类**：跌停时卖不出，等同"平仓通道冻结"——LIQUIDITY_CRISIS 在跌停时触发（卖压≈1.0 + spread=1.0 满足 AND），联动 LEVEL_1 停开仓（跌停时开仓=接飞刀）。
- **涨跌停监控数据源**：miniQMT `xtdata.get_full_tick` 可取实时盘口（买一/卖一/涨停价/跌停价），用于判定涨跌停状态。

#### 3.5.1 涨跌停状态检测算法（v1.0.3 补全）

> ✅ 已施工（`liquidity_crisis_manager` MOD-RK-21 `detect_limit_status` + `resolve_effective_spread`，54 测试全绿，2026-08-13）——接口：`detect_limit_status(last_price, limit_up_price, limit_down_price, bid_price, ask_price, tolerance=1e-6) -> str`，五状态定义如下。

```python
def detect_limit_status(last_price: float, limit_up_price: float, 
                        limit_down_price: float, bid_price: float, 
                        ask_price: float, tolerance: float = 1e-6) -> str:
    """涨跌停状态检测
    
    Args:
        last_price: 最新成交价
        limit_up_price: 涨停价（当日涨停基准）
        limit_down_price: 跌停价（当日跌停基准）
        bid_price: 买一价（None=无买单）
        ask_price: 卖一价（None=无卖单）
        tolerance: 价格比较容差（浮点精度）
    Returns:
        "limit_up" | "limit_down" | "near_up" | "near_down" | "normal"
    """
    # 1. 涨停判定：最新价达涨停价 + 卖一缺失（无卖单=买不进）
    if abs(last_price - limit_up_price) < tolerance and ask_price is None:
        return "limit_up"
    
    # 2. 跌停判定：最新价达跌停价 + 买一缺失（无买单=卖不出）
    if abs(last_price - limit_down_price) < tolerance and bid_price is None:
        return "limit_down"
    
    # 3. 接近涨停：距涨停 <0.5%（即将封板，提前预警）
    if last_price >= limit_up_price * 0.995:
        return "near_up"
    
    # 4. 接近跌停：距跌停 <0.5%（即将封板，提前预警）
    if last_price <= limit_down_price * 1.005:
        return "near_down"
    
    return "normal"
```

**涨跌停价获取**：miniQMT `xtdata.get_full_tick` 返回的 tick 数据含 `limit_up` / `limit_down` 字段（交易所每日计算 = 前收盘价 × (1±涨跌幅限制)），ST/*ST 股 ±5%、主板 ±10%、创业板/科创板 ±20%、北交所 ±30%。**与 §3.1.1/§3.1.2 的联动**：

| 涨跌停状态 | sell_pressure | bid_ask_spread | LIQUIDITY_CRISIS 触发？ |
|---|---|---|---|
| limit_up（涨停） | 低（买压主导） | None（跳过检查） | ❌ 不触发（涨停≠流动性危机，是买盘过剩） |
| limit_down（跌停） | ≈1.0（纯卖压） | 1.0（大值，使 AND 可满足） | ✅ 触发（跌停=平仓通道冻结=流动性危机子类） |
| near_up（接近涨停） | 正常 | 正常 | 按正常逻辑判定 |
| near_down（接近跌停） | 偏高 | 偏大 | 可能触发（视实际 sell_pressure/spread 值） |

### 3.6 决策⑥：危机恢复算法——滞后-恢复双阈值（Hysteresis）

> ✅ 已施工（`liquidity_crisis_manager` MOD-RK-21 `check_recovery` + `LiquidityRecoveryState`，54 测试全绿，2026-08-13）——接口与参数矩阵如下（算法语义真源在本文档）。
>
> ✅ **systemic 层降级机接线已落地**（2026-08-17 AI-LVL3-001，v1.2.0）：`risk_layer_orchestrator` 持有 `LiquidityRecoveryState` 作系统性降级机状态，每轮 `detector.check()` 后按本节恢复条件矩阵经 `check_recovery` 门禁逐级迁移（3→2→1→0；升级立即迁移+重置计时，平级停留不重置）；触发阈值从 `detector.config` 读取、恢复阈值为 orchestrator C 类参数（spread 半阈值 0.5/卖压 0.50/最短持续 {1:10,2:15,3:30}），spread/sell_pressure 未提供按 0.0 处理（MOD-RK-21 涨停缺失先例）。**降级只迁移警报级别（systemic_cap/halt），不解除 Kill Switch 熔断闩锁**——35 号 KILL 态人工复位不变式保持（§3.8「35 号 KILL 态禁止 37 号恢复」）。

**核心原则**：触发阈值与恢复阈值**不对称**（hysteresis 双阈值），避免在临界状态反复震荡（触发→恢复→再触发→再恢复的 thrashing）。**恢复条件矩阵**（对称于 §3.3 触发条件，但阈值更宽松）：

| 警报级别 | 触发条件（§3.3） | **恢复条件** | 恢复动作 | 最短持续时间 |
|---|---|---|---|---|
| LEVEL_1 → 正常 | spread ≥ 0.5% AND sell_pressure ≥ 0.65 | spread < **0.25%**（半阈值）AND sell_pressure < **0.50** 持续 **N=5 分钟** | 恢复开仓权限（`halt_new_orders=False`） | 触发后至少 **10 分钟**才可恢复 |
| LEVEL_2 → LEVEL_1 | 2 信号 | 信号数降至 **1 个** AND spread < 0.3% 持续 N=5 分钟 | position_cap 从 70% → 100% | 至少 **15 分钟**才可降级 |
| LEVEL_3 → LEVEL_2 | ≥3 信号 或 情绪断路器 | Kill Switch 30 分钟冷却期满 AND 信号数降至 **≤2** AND spread < 0.3% | 从清仓状态→允许重建仓 70% | Kill Switch 冷却 30 分钟 |

**恢复算法步骤**（CUSUM 式，对齐 §3.1 检测器的 CUSUM 框架）：

```python
def check_recovery(current_spread, current_sell_pressure,
                   trigger_threshold_spread, recovery_threshold_spread,
                   trigger_threshold_pressure, recovery_threshold_pressure,
                   min_hold_minutes, elapsed, current_level, active_signals=0):
    """危机恢复判定——滞后双阈值 + 持续时间门控
    
    Args:
        current_spread: 当前有效买卖价差（已过 §3.5.1 涨跌停检测处理）
        current_sell_pressure: 当前卖压（§3.1.1 OBI 反转）
        trigger_threshold_spread: spread 触发阈值（0.005 = 0.5%）
        recovery_threshold_spread: spread 恢复半阈值（0.0025 = 0.25%，触发阈值的一半）
        trigger_threshold_pressure: 卖压触发阈值（0.65）
        recovery_threshold_pressure: 卖压恢复半阈值（0.50，触发阈值的 ~77%）
        min_hold_minutes: 当前级别最短持续时间（分钟，由 {1:10,2:15,3:30}[level] 注入）
        elapsed: 距触发已过时间（分钟，recovery_state.elapsed）
        current_level: 当前警报级别（1/2/3）
        active_signals: 当前活动触发信号数（§3.1 双条件计数：sell_pressure 超阈值 + spread 超阈值，范围 0-2；默认 0）
    Returns:
        target_level: 恢复后的目标级别（0=正常 / 1=LEVEL_1 / 2=LEVEL_2），或 None（不恢复）
        ⚠️ 返回 0（正常态）是有效恢复结果，调用方须用 `is not None` 判定，不可用真值检查
            （`if recovered:` 在 target_level=0 时为 False，会跳过 LEVEL_1→正常的恢复）
    """
    # 1. 最短持续时间门控（防 thrashing）—— LEVEL_3 的 30 分钟已覆盖 Kill Switch 冷却期
    if elapsed < min_hold_minutes:
        return None  # 持续时间不足，不恢复
    
    # 2. 半阈值 hysteresis 检查（恢复阈值 < 触发阈值，制造稳定缓冲带）
    spread_ok = current_spread < recovery_threshold_spread
    pressure_ok = current_sell_pressure < recovery_threshold_pressure
    
    # 3. 分级恢复条件（各级别恢复目标递进，信号数要求递减宽松）
    if current_level == 1 and spread_ok and pressure_ok and active_signals == 0:
        # LEVEL_1 → 正常：所有信号归零 + spread/pressure 降至半阈值
        return 0  # 正常态（⚠️ 调用方须用 is not None 判定）
    
    if current_level == 2 and active_signals <= 1 and current_spread < recovery_threshold_spread * 1.2:
        # LEVEL_2 → LEVEL_1：信号降至≤1 + spread < 半阈值×1.2（0.3%，略宽于正常恢复）
        return 1
    
    if current_level == 3 and active_signals <= 2 and current_spread < recovery_threshold_spread * 1.2:
        # LEVEL_3 → LEVEL_2：Kill Switch 冷却期满（min_hold=30 覆盖）+ 信号降至≤2
        return 2
    
    return None  # 不满足恢复条件
```

**恢复执行动作**（与触发动作同由 FirmRiskAggregator 消费 alert 时执行）：

| 恢复路径 | 执行动作 |
|---|---|
| LEVEL_1 → 正常 | `halt_new_orders=False`（恢复开仓权限）；position_cap 保持 1.0；通知日志"流动性危机解除，恢复开仓" |
| LEVEL_2 → LEVEL_1 | position_cap 从 0.70 → 1.00；`halt_new_orders=False`；通知日志"多信号降级，恢复满仓权限" |
| LEVEL_3 → LEVEL_2 | Kill Switch 冷却期满后，position_cap 从 0.00 → 0.70；`halt_new_orders=False`（允许重建仓至 70%）；通知日志"系统性危机降级，允许重建仓 70%" |

**为何半阈值（hysteresis）+ 最短持续时间门控**：

- 恢复阈值若=触发阈值（0.5%），spread 在 0.49%-0.51% 间波动会反复触发/恢复（thrashing）；半阈值（0.25%）制造稳定缓冲带（降到 0.25% 才恢复、升到 0.5% 才再触发——控制论迟滞回线标准应用，恒温器/施密特触发器同原理）
- 危机恢复非瞬时——spread 短暂回到 0.25% 以下可能只是盘中波动间隙，N=5 分钟持续窗口确保恢复条件**持续满足**；LEVEL_1 10 分钟/LEVEL_2 15 分钟是 A 股日内波动节奏经验估计（MVP 先定，实盘校准）
- **与 MOD-RK-10 的集成**：恢复判定由 `AshareSystemicRiskDetector.check()` 在每次 `detect()` 时顺带执行（输出 `SystemicRiskAlert(level=current_state)` 或 `SystemicRiskAlert(level=0, recovered_from=prev_state)`）
- **待校准**：阈值与最短持续时间为经验初始值，重评条件见 §6 恢复阈值实盘校准行

### 3.7 决策⑦：2026 前沿算法评估——Hawkes / VPIN 重评 / Crumbling Labeler

#### 3.7.1 Hawkes 自激励过程——储备（Phase 1.5 候选）

**算法**：Hawkes 过程建模流动性事件的**聚集性**——一次大单冲击后后续冲击概率短期升高（自激励），λ(t) = μ + Σ α·exp(-β(t-t_i))（[stockalpha.ai 2026-02](https://stockalpha.ai)；[arxiv 2310.09273](https://arxiv.org/abs/2310.09273)），μ=基线强度、α=激励幅度、β=衰减率。MOD-RK-10 是阈值触发无聚集性建模，Hawkes 强度持续升高 = 事件正在聚集，比单次阈值触发更早预警（典型：融资盘平仓潮第一笔抛售未超阈值但强度已升）。**2026-08 研究更新（v1.0.8）**：① A 股直接实证（[arXiv:2512.08000](https://arxiv.org/abs/2512.08000)）——自激+抑制型 Hawkes 拟合上证/深证/创业板指，高活跃期行业延续趋势、低活跃期强行业轮动，同时解释"行业轮动"与"踩踏传染"；② 图熵领先 7-12 天预警（[An & Dai 2026, Entropy 28(8):887](https://www.mdpi.com/1099-4300/28/8/887)，2026-08-06）——transfer entropy + 多元 Hawkes，Von Neumann 图熵在回撤峰值前 7-12 个交易日达极端值，预警从分钟级升级到日级，激发分量在 COVID-19/2022 欧洲能源危机使传染强度高基线 35%-58%；③ 2026-07 A 股量化危机验证（edgen 2026-07-21，CSI300 -5.81%/科创50 -17.46%，两周蒸发 10 万亿）——"止损→下跌→更多止损"级联在中小盘无量跌停精确体现。**判定：储备（Phase 1.5 候选）**——需 tick 级事件流 + μ/α/β 用历史危机拟合（2015 股灾/2024 小盘股危机，成本中等）；图熵发现将价值扩展到日级预警（可能上调 Phase 1 候选），但跨资产事件网络管道成本高（中→高），维持储备；远期实施优先 `tick` 库（Marcel Gauthche 2026-05：order-flow toxicity 3σ 阈值+清算级联预警+财报成交量爆发检测）。**重评条件**：MOD-RK-10 实盘 3 月发现阈值触发滞后时上推为前置预警层，或需日级提前预警而非分钟级。

#### 3.7.2 VPIN 重评——维持拒绝（2026 证据不改变结论）

**§4.6 原拒绝理由**：VPIN 需 tick 级时间桶成交量分类；个人小资金不做市不受 toxic flow 直接伤害；MOD-RK-10 卖压+spread 已等价覆盖。**2026 新证据**：[theplugg 2026-07](https://theplugg.com) 将 VPIN 与 OBI、Depth-to-Volatility Decay 并列闪崩三大预警，但其核心价值是做市商视角（toxic flow 吃掉做市商库存）；[ClusterLOB 2026-06](https://clusterlob.com) 实证 VPIN 与 OBI 相关性 0.85+，额外信息量有限。**重评结论：维持拒绝**——信息冗余（0.85+）+ 不做市价值不适用 + 双条件已覆盖同类信号。**重评条件不变**：策略扩展到做市/提供流动性场景时。

#### 3.7.3 Crumbling Labeler——储备（Phase 2 远期候选）

**算法**：[ICLR 2026](https://iclr.cc) Crumbling Labeler——神经网络分类器区分"机械性流动性撤退"（做市商批量撤单，价格会恢复）与"信息驱动重定价"（基本面变化，不恢复），用于决定是否清仓（[theplugg 2026-07](https://theplugg.com) 引用）。**对 G18 的增益**：LEVEL_3 清仓从"≥3 信号一刀切"进化到"≥3 信号 + 信息重定价判定才清仓"（机械撤退→维持持仓等恢复）。**判定：储备（Phase 2 远期候选）**——需人工标注历史危机"机械 vs 信息"标签训练（成本高）+ ICLR 2026 无开源实现/工业部署案例；MVP"≥3 信号清仓"保守安全（误清仓代价仅错过反弹而非本金亏损）。**重评条件**：① 论文开源实现 ② AUM 增长到清仓成本显著（错过恢复代价 > 训练成本）。

#### 3.7.4 Slippage-at-Risk (SaR) 框架——储备（Phase 2 候选，选项之外更好的答案算法）

**算法**：[arXiv:2603.09164](https://arxiv.org/abs/2603.09164) Sepper 2026-03 SepperLabs 提出 Slippage-at-Risk (SaR)，从**当前盘口微结构**推导**前瞻性**清算执行风险（区别于 VaR 等回溯性指标），含三个互补度量：

```
SaR(α)   = inf{s : P(slippage > s) ≤ 1-α}    # 横截面滑点分位数（α 置信下最坏滑点）
ESaR(α)  = E[slippage | slippage > SaR(α)]    # 尾部期望滑点（类 ES 的尾部均值）
TSaR(α)  = Q × ESaR(α) × notional            # 美元计总尾部滑点（组合层级）
```

**集中度调整**（Concentration Haircut，关键创新）：`SaR_adj = SaR_base × (1 + HHI^η)`——HHI = 盘口各做市商深度份额平方和 ∈(0,1]（→1 单一垄断极脆弱，→0 高度分散），η≈1.5（Sepper 2026 实证）；hhi=1 → 因子 2（SaR 翻倍），hhi=0.1 → ≈1.03。**典型场景**：5 档深度看似充足（spread/sell_pressure 正常）但集中于 1-2 个做市商——现有检测不触发，SaR 集中度调整给出高值（HHI→1 → SaR 翻倍），提前预警"纸糊深度"；随后做市商撤离→spread 暴扩（MOD-RK-10 才触发，已晚 1-3 分钟）。**实证支撑——强平级联两类型分类**（[arXiv:2608.03616](https://arxiv.org/abs/2608.03616)，2026-08，7 起加密强平级联 2022-2025）：级联起始是突变（order parameter 跳变 1.6-4.4σ）；**内生累积型**（有 critical slowing down 前兆，Hawkes 适配）vs **外生冲击型**（突发新闻无前兆，SaR 识别脆弱结构但不预测冲击）；88% 强平在起始后 30 分钟内、63% 被场外 backstop 吸收。A 股融资盘平仓潮≈内生型、突发利空≈外生型；MVP 双条件 AND 是两类型的统一回溯响应。**对 G18 的增益**——与双条件 AND 维度互补：

| 维度 | 现有（MOD-RK-10 双条件 AND） | SaR 框架 |
|---|---|---|
| **时间方向** | 回溯性（价差已扩大+卖压已出现才触发） | **前瞻性**（从当前盘口微结构预测未来清算滑点） |
| **输入** | sell_pressure（OBI）+ bid_ask_spread | 完整盘口多档深度 + 做市商集中度 |
| **输出** | 布尔触发（危机/非危机） | 连续滑点分布分位数（风险量化） |
| **做市商结构** | 不感知（只看总量） | **感知**（HHI 调整，识别"单一做市商撤离即崩溃"的脆弱结构） |
| **组合层级** | 单标的判定 | TSaR 聚合到组合美元滑点 |

**A 股适配与判定**：✅ miniQMT `get_full_tick` 5 档盘口可算 HHI（无做市商席位标识，用"挂单量集中度"近似如前 3 大挂单/总挂单）；⚠️ 原论文针对永续合约清算级联（A 股无杠杆清算，但融资盘平仓潮机制类似：跌破维持担保比例→强平→cascading）+ A 股个股无指定做市商（科创板做市 2023 才引入）——HHI 重定义为"挂单量集中度"；✅ 前瞻滑点+集中度两项核心增益不依赖永续特有机制。**判定：储备（Phase 2 候选）**——与 Hawkes 正交互补（Hawkes 预警事件聚集、SaR 预警结构脆弱），可叠加 Phase 2 双层前瞻预警。**重评条件**：① 实盘 6 个月盘口数据校准 HHI 阈值 ② AUM 增长到自身交易开始影响盘口（需 SaR 评估自身清算滑点）。

#### 3.7.5 Latent Microstructure Regime Detection（隐含微结构 regime 转变检测）——储备（Phase 2 候选，选项之外更好的算法）

**算法**：[arXiv:2604.20949](https://arxiv.org/abs/2604.20949)（Hiremath & Hiremath, 2026-04）三 regime 因果 DGP：**stable → latent build-up → stress**。核心洞察：OFI/spread/volatility 等标准信号**按构造是反应性的**（测量已发生压力的后果，τ ≥ σ，零/负 lead-time 是逻辑必然非调参失败）；latent build-up 在温和条件下可识别并保证严格正期望 lead-time（Proposition 1：充分 drift-to-noise 条件；Proposition 2：检测概率下界为 SNR 与 build-up 持续时间的函数）。触发检测器三组件：**MAX 聚合**（uncertainty/drift 双通道）+ **rising-edge 条件**（过滤已高位噪声）+ **自适应阈值**；触发通道 = **深度侵蚀（depth erosion）+ HMM 熵**（占 >99% 首次触发）。**实证性能**：仿真（200 runs）mean lead-time +18.6±3.2 timesteps、precision 1.00、coverage 0.54；实数据（BTC/USDT 1Hz，5 标注事件）+38±21 秒、precision 1.00、coverage 0.80——**优于 CUSUM/BOCPD/HMM thresholding/imbalance/volatility 基线**（基线均负 lead-time）；论文明确优于 BOCPD（检测已发生变点 vs 本方法检测前兆），与 35 号 §4.18 BOCD 场景不同（日级策略衰减 vs 盘中秒级流动性）不冲突。

**关系/A 股适配/判定**：Hawkes（§3.7.1，时间"事件聚集"）× SaR（§3.7.4，结构"盘口脆弱"）× Latent build-up（regime 转变"正在恶化"）三层正交可叠加。A 股适配：depth erosion 可用 miniQMT 5 档盘口快照近似，HMM 熵与 [10 号](10_regime_detector_spec.md) regime 检测器同类计算；适用融资盘平仓潮（担保比例渐降=build-up）/涨跌停前夕/尾盘（14:50-15:00）三场景；论文实数据仅 BTC/USDT（A 股无做市商/T+1/涨跌停差异大需独立验证）。**判定：储备（Phase 2 候选）**——① 1Hz 盘口在 miniQMT 非均匀可得需重采样 ② 多组件检测器盘中实时工程成本高于双条件 AND ③ 仅 5 标注事件验证不足 ④ MVP 已覆盖，增量"提前 30-60 秒"与 Hawkes"1-3 分钟"重叠。**重评条件**：① 实盘 6 个月盘口数据验证 depth erosion 通道 ② Hawkes 上线后 lead-time 仍不足（深度侵蚀更早）③ miniQMT 提供均匀采样 5 档盘口。**五算法评估汇总**：

| 算法 | 增益 | 成本 | 判定 | 重评条件 |
|---|---|---|---|---|
| Hawkes 自激励 | 提前 1-3 分钟预警聚集性危机 | 中（tick 事件流 + 参数拟合） | **Phase 1.5 储备** | 实盘 3 月发现阈值触发滞后 |
| VPIN 重评 | 与 sell_pressure 相关性 0.85+，信息冗余 | 高（tick 时间桶） | **维持拒绝** | 做市场景扩展时 |
| Crumbling Labeler | 区分机械撤退 vs 信息重定价，优化清仓决策 | 高（神经网络 + 标注数据） | **Phase 2 远期储备** | 开源实现 + AUM 增长 |
| **SaR 框架** | **前瞻性滑点预测 + 集中度感知（识别脆弱盘口结构）** | 中（HHI 重定义 + η 校准） | **Phase 2 储备** | 实盘 6 月盘口数据 + AUM 增长 |
| **Latent build-up 检测** | **正 lead-time regime 转变预警（depth erosion + HMM 熵），优于 CUSUM/BOCPD/HMM** | 高（1Hz 盘口 + HMM 熵 + 多组件检测器） | **Phase 2 储备** | 实盘 6 月盘口数据 + Hawkes lead-time 不足时 |
| **ExsdHawkes 状态消失扩展** | **物理约束下的 Hawkes（KKT 分离估计+状态消失处理），避免爆炸分支比** | 高（LOB 状态空间 + KKT MLE） | **Phase 2 储备** | Hawkes §3.7.1 上线后若标准 Hawkes 爆炸 |
| **Liquidation Cascade 三因子** | **推翻临界级联假设（亚临界 λ≈0.1-0.2），severity=冲击×路径×流动性撤回** | 中（三因子监测） | **Phase 2 储备** | A 股融资盘平仓数据可得时 |
| **Multiplex Network Hawkes** | **多层网络 Hawkes 通道分离（行业/偿付/盈利协变量），识别外向系统性风险源** | 高（MCMC + 多层网络） | **Phase 3 远期储备** | A 股股权质押/担保圈网络数据可得时 |

#### 3.7.6 ExsdHawkes 状态消失扩展——储备（Phase 2 候选，选项之外更好的算法）

**算法**：[Kimura 2026-04 arXiv:2604.23961](https://arxiv.org/abs/2604.23961)（Sophia University）Extended State-Dependent Hawkes（ExsdHawkes）：放宽传统约束允许**状态消失**（涨停无卖单/跌停无买单），KKT 条件证明 MLE 可分离（转移概率与 Hawkes 参数独立估计，即使某些转移被物理禁止）；唯一复现波动率签名图向上斜率（捕获"局部超临界"）；MLO（可成交限价单）是迫使 LOB 失稳的主要催化剂；缺物理约束的标准 SD-Hawkes 产生爆炸分支比（>1）无法维持模拟稳定——物理一致性是准确建模宏观波动率的先决条件。与 §3.7.1 关系：标准 Hawkes 无状态约束，ExsdHawkes 在 LOB 状态空间上定义、状态消失时"暂停"残差累积避免爆炸。**判定：储备（Phase 2）**——状态空间+KKT 分离估计复杂度高；实证用 MUFG 数据（日本），A 股涨跌停更频繁需独立验证；增量价值"避免爆炸分支比"，仅标准 Hawkes 实盘不稳定时升级。**重评条件**：① §3.7.1 上线后涨跌停时分支比爆炸致预警失效 ② miniQMT Level-2 支持 LOB 状态空间建模 ③ A 股涨跌停频繁票种独立验证。

#### 3.7.7 Liquidation Cascade 三因子框架——储备（Phase 2 候选，选项之外更好的算法）

**算法**：[Garcia Seuma 2026-08 arXiv:2608.03616](https://arxiv.org/abs/2608.03616)：7 次重大加密永续强平级联（2022-2025）三种估计器（结构比/放大记账/INAR-Hawkes 流式估计）一致显示**级联全程深度亚临界（λ≈0.1-0.2）**且流式估计在高潮时**下降**——**推翻临界级联假设**（Galton-Watson critical slowing down 预警在突发冲击中失效），一阶相变替代临界相变；**severity = 冲击 × 路径映射 × 流动性撤回**（非发散乘子）；88% 强平 30 分钟内完成、63% 被场外兜底吸收。**对 §3.7.1 的修正**：预警应监测三因子（冲击幅度+路径映射+流动性撤回）而非单一分支比；A 股迁移：融资融券平仓线+股权质押爆仓形成类似级联，监测两融余额变化率+平仓密度作代理。**判定：储备（Phase 2）**——① 加密实证，A 股无永续强平机制 ② 路径映射因子需定义（行业关联度/担保圈网络）③ 是"预警信号选择"升级非替代。**重评条件**：① A 股融资盘平仓数据（两融余额/平仓密度）可得 ② §3.7.1 上线后分支比预警失效。

#### 3.7.8 Multiplex Network Hawkes 系统性风险——储备（Phase 3 远期候选）

**算法**：[Zelvyte & Griffin 2026-06 arXiv:2606.15755](https://arxiv.org/abs/2606.15755)（University of Kent）：扩展 Linderman & Adams (2014) 网络 Hawkes 到**多层激励层**（权重依赖观测边+节点协变量），单一推断传输网络内**分离传染通道贡献**（行业相似性/偿付能力/盈利能力可直接比较）；MCMC 后验推断含不确定性量化；99 家北美/欧洲公司 CDS（2004-2022）实证：传染路径稀疏，系统性风险集中在**外向流**（少数有影响力机构）非相互反馈。与 §3.7.1 关系：单资产"事件聚集"→多机构网络"谁传染谁"的系统性升级。**A 股迁移**：股权质押网络/担保圈/行业供应链关联，周度/月度 MCMC 重估。**判定：储备（Phase 3 远期）**——① 需机构间关联网络数据（A 股公开数据有限）② MCMC 成本中等需定期重估 ③ 系统性传染是宏观级非个体级风险，MVP 优先级低。**重评条件**：① 股权质押/担保圈数据可得且质量足够 ② AUM 增长到需关注系统性传染 ③ 与 §3.7.6 同步评估（ExsdHawkes 管单资产 LOB，Multiplex 管跨机构网络）。

#### 3.7.7.1 Garcia Seuma 临界性预警异质性 —— 储备（Phase 2 候选，§3.7.7 Liquidation Cascade 配套）

**算法**（[Garcia Seuma 2026-07-29 arXiv:2607.27070](https://arxiv.org/abs/2607.27070)，§3.7.7 配套论文 Part I，7 次级联 × 39 种分析配置系统测试）：① **无事件不变量**——滚动方差+lag-1 自相关（critical slowing down 经典信号）在 5/7 事件出现，但 2 次突发新闻（关税）冲击中**完全缺失**（事件异质性是结构性的非噪声）；② **唯一存活规律**——吃单订单流方差压缩（taker order-flow variance compression），300 onset placebo test Fisher-combined p ≈ 5×10⁻⁶，但属**群体级前兆**（population-level）非**单事件警报**（per-event），不能直接用于个体级实时预警；③ **冲击类型识别约束**——突发新闻冲击与内生流动性冲击预警信号完全不同（前者无 critical slowing down，后者有）。**对 §3.7.7 三因子框架的约束**：

| 冲击类型 | critical slowing down | taker flow variance compression | §3.7.7 三因子预警 |
|---|---|---|---|
| 内生杠杆级联（5/7 事件） | ✅ 出现 | ✅ 出现 | 三因子（冲击×路径×流动性撤回）有效 |
| 突发新闻冲击（2/7 事件） | ❌ 缺失 | ✅ 出现 | 三因子需补充"新闻冲击"维度 |

**A 股迁移与判定**：内生杠杆级联（两融余额快速下降+平仓密度上升）→ 三因子适用；突发政策冲击（监管公告如 2024 国九条）→ 降权"路径映射"因子（无前置累积）主靠"冲击幅度+流动性撤回"双因子；吃单方差压缩可用 miniQMT Level-2 主动买/卖单流量方差代理（群体级前兆，需配合其他信号确认）。**判定：储备（Phase 2）**——① 群体级前兆单事件预测力弱 ② 加密实证需 A 股独立验证 ③ 本节是 §3.7.7 配套约束，与其同期评估非独立模块。**重评条件**：① §3.7.7 上线后突发新闻冲击预警失效 ② Level-2 主动买卖单流量数据可得 ③ 与 §3.7.7 同期 A 股实证。

#### 3.7.9 Weng A 股羊群效应 Johnson S_U 变换 —— 储备（Phase 2 候选，A 股专属）

**算法**（[Weng 2026-07-29 arXiv:2607.27063](https://arxiv.org/abs/2607.27063)，A 股专属 agent-based 网络模型 + Johnson S_U 变换羊群指标，填补 §3.7.x"A 股实证"空白）：① **异质高斯信念**（von Neumann/Moore 晶格、Erdős-Rényi、Watts-Strogatz 网络，按邻居修正行动概率）+ **有限速度信息扩散**——区分**信息调整**与**行为模仿**（基本面驱动合理跟随 vs 无信息纯模仿羊群）；② **Johnson S_U 变换**——CSAD/LSV 羊群度量的有界非正态分布转近似正态，消除牛/熊偏差（原始 CSAD 牛市偏高、熊市偏低），使滚动指标统计可比；③ **滚动尾端羊群指标**识别信息延迟+局部社会强化+羊群衰减三机制（A 股动量与反转的互补驱动）。**与 §3.7.1 标准 Hawkes 的关系**：

| 维度 | §3.7.1 标准 Hawkes | Weng Johnson S_U 羊群指标（§3.7.9） |
|---|---|---|
| 信号类型 | 事件聚集（event clustering） | 截面分散度（cross-sectional dispersion） |
| 数据需求 | tick 级事件流 | 日级 CSAD/LSV + 网络结构 |
| 时间尺度 | 分钟级 | 日级/周级 |
| A 股适配 | 通用（加密/美股实证为主） | **A 股专属**（直接 A 股实证） |
| 互补性 | 检测"事件何时聚集" | 检测"羊群何时形成" |

**32号递进与判定**：两者正交（时间×截面双维度预警）。**与 32号 §2.10.6 华泰金工风格拥挤度的关系**：32号是**风格级**羊群检测（哪个风格拥挤），Weng 是**市场级**（整体羊群度）——Weng 管市场整体、华泰管风格、§3.7.1 Hawkes 管事件聚集。**判定：储备（Phase 2）**——① 网络拓扑假设难观测需校准 ② S_U 参数（γ,δ,ξ,λ）需 A 股历史 CSAD/LSV 拟合（MVP 样本不足）③ §3.5 已有 HBI/CSAD 基础指标，增量价值须先验证牛/熊偏差显著。**重评条件**：① §3.5 HBI/CSAD 上线后牛/熊偏差显著影响羊群信号 ② CSAD/LSV 数据 ≥2 年 ③ 与 §3.7.1 同期评估（时间×截面双维度）。

#### 3.7.10 Zhou 平方根冲击操纵周期 —— 储备（Phase 3 远期，A 股专属）

**算法**（[Zhou, Chen & Wei 2026-07-06 arXiv:2607.05141](https://arxiv.org/abs/2607.05141)，Westlake University，A 股专属 ABM 证明**平方根价格冲击是内生操纵周期的必要条件**）：① **A 股专属机制**——单个进化优化机构 agent 对抗 20,000 个羊群散户 agent，实现 ±10% 涨跌停板+T+1 结算+隐形分配（机构卖出时有效羊群减半）；② **均场约化**为非线性振荡器——连续 Hopf 分岔（amplitude A ∝ (C-C_c)^½）+ 不连续 fold 转变；③ **平方根冲击必要性**——线性冲击消除 Hopf 分岔使市场无条件稳定（无操纵周期），平方根冲击引入非线性反馈使"卖出-触发羊群-低位回补"循环可获利。**对 §3.7.x 系列的理论支撑**：

| §3.7.x 算法 | 检测目标 | Zhou 理论支撑 |
|---|---|---|
| §3.7.1 Hawkes | 事件聚集 | 操纵周期的"卖出-羊群-回补"循环产生事件聚集 |
| §3.7.6 ExsdHawkes | LOB 状态失稳 | 涨跌停板使 LOB 状态消失，Zhou 模型直接建模此机制 |
| §3.7.7 Liquidation Cascade | 三因子级联 | "流动性撤回"因子对应 Zhou 的"隐形分配减半"机制 |
| §3.7.9 Weng 羊群 | 截面羊群度 | Zhou 的 20,000 散户 agent 是 Weng 羊群的微观基础 |

**40号联动与判定**：统一的 A 股内生操纵机制理论——所有预警信号本质都在捕捉"机构卖出-羊群跟风-流动性撤回-低位回补"循环的不同侧面。**对 [40号执行算法](40_execution_broker.md) 的启示**：[40号](40_execution_broker.md) §2.12 平方根冲击模型（已施工）不仅是执行成本建模，更是**操纵周期检测的输入**——冲击系数异常升高可能预示操纵周期启动，可联动 §3.7.1"冲击幅度"因子。**判定：储备（Phase 3 远期）**——① 理论模型非工程算法（价值是机制理解非直接部署）② 散户行为参数（跟风概率/信息延迟）需 A 股实盘校准 ③ 与 §3.7.1 重叠（Hawkes 已检事件聚集，Zhou 提供机制理解）。**重评条件**：① Hawkes 上线后需理解预警微观机制 ② 40号 §2.12 冲击系数实盘校准后验证"系数异常→操纵周期"假设 ③ A 股散户跟风参数实证可得。

#### 3.7.11 LRISK 系统性流动性风险前瞻指标 —— 储备（Phase 2+ 远期，系统级前瞻预警）

**算法**（[Jourde, Saillard & Van Dijk 2026-07-14 SSRN 7110978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7110978)，Banque de France/CREST，原稿 2026-01-05）：**LRISK** 前瞻性系统性流动性风险度量——"严重系统级赎回冲击下基金部门对市场的总价格压力"，补 §3.7.x**系统级前瞻预警层**。三大放大通道：① **流量共振**（flow commonality，flow beta 动态预测聚合基金流极端尾部）② **组合重叠**（portfolio similarity，持仓穿透映射卖出压力到具体资产）③ **流动性螺旋**（liquidity spirals，非线性反馈环，区别于 Duarte & Eisenbach 2021 线性假设）。**实证**：2011-2024 美国公司债基金，COVID-19 期间预测横截面收益，聚合 LRISK **提前两个季度预测市场承压**，并解释基金 in-kind redemption 差异；对比 CoVaR/SRISK（为银行设计），LRISK 专为开放基金"每日赎回承诺 vs 非流动证券"错配设计。**与 §3.7.x 系列的关系**：

| §3.7.x 算法 | 层级 | 时间尺度 | LRISK 关系 |
|---|---|---|---|
| §3.7.1 Hawkes / §3.7.6 ExsdHawkes | 微观（tick 事件聚集） | 分钟级 | LRISK 是**宏观前瞻**层，Hawkes 是**微观即时**层 |
| §3.7.7 Liquidation Cascade | 中观（级联机制） | 分钟-小时级 | LRISK 的"流动性螺旋"通道是 Liquidation Cascade 的系统级聚合 |
| §3.7.9 Weng 羊群 | 中观（截面羊群） | 日级 | LRISK 的"流量共振"通道是 Weng 羊群的资金流侧体现 |
| §3.7.10 Zhou 操纵周期 | 理论（机制） | — | LRISK 不涉及操纵周期，专注被动赎回→火售外溢 |

**Residual Supply 关系/A 股适配/判定**：微观/中观算法捕捉"危机已发生/正在发生"，LRISK 提前 1-2 季度预测"即将发生"。**与 §5.2 Residual Supply 的关系**：Residual Supply（[arXiv:2605.30672](https://arxiv.org/abs/2605.30672)）管单资产被迫卖出 premium，LRISK 管全市场系统性外溢（共振赎回→重叠持仓→火售螺旋）——递进。**A 股适配**：公募赎回率+北向净流出+融资余额下降的加权 z-score 近似 flow commonality，基金重仓股集中度近似组合重叠；公募持仓季度披露滞后、北向/融资日频；2026-07 量化危机（CSI300 -5.81%/科创50 -17.46%）实证 A 股赎回→集中卖出→流动性螺旋同样存在。**判定：储备（Phase 2+ 远期）**——① 系统级指标非个股检测，到 MVP 响应有层级跳跃 ② 季度披露滞后，"提前两季度"可能退化为"提前数周" ③ 与 Residual Supply 同需 fund flow 数据，须先验证单资产级边际价值。**重评条件**：① Residual Supply 上线后缺系统级聚合 ② 公募持仓数据频率提升（月频+）③ 与 Hawkes 日级预警（图熵 7-12 天）对比 lead-time。

#### 3.7.12 欧洲 ML 流动性预测对比 —— 储备（Phase 1.5 候选，Amihud 预测方法学）

**算法**（[Arakelia, Caporale, Gasparinatou & Karanasos 2026-07-16 SSRN 7125463 / CESifo WP 12829](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7125463)，欧洲五大股指 2010-2026 日频对数 Amihud 一步滚动预测，ARIMA/动态面板 vs RF/XGBoost/SVR 统一 walk-forward + SHAP）：① 流动性**高度持续**（滞后流动性是最强预测因子）② **动态面板预测误差最低且不输 ML**（Diebold-Mariano 无显著差异）③ SHAP 三大驱动因子：**成交活跃度+滞后流动性+市场不确定性**。**对 §3.1 / §5.2 的方法学启示**：

| 启示 | 应用到 37 号 |
|---|---|
| 流动性高度持续 | §3.1 静态阈值合理——高持续意味着今日 Amihud ≈ 昨日，阈值无需频繁更新 |
| 动态面板不输 ML | §5.2 Phase 1.5 阈值校准可用简单动态面板（Amihud_t = α + β·Amihud_{t-1} + γ·volume_t + δ·volatility_t + ε）而非重 ML 栈——符合 MVP 简化原则 |
| 三大驱动因子 | §5.2 Phase 1.5 特征工程：成交活跃度（换手率）+ 滞后 Amihud + 市场不确定性（A 股用波动率/期权 IV 近似）作为 Amihud 预测输入 |

**SaR 关系/A 股适配/判定**：§3.7.4 SaR 是前瞻性滑点预测（盘口微结构推导，管"下一笔清算滑点"），本条是前瞻性 Amihud 预测（时序计量推导，管"明日整体非流动性"）——正交。A 股适配：结论跨市场稳健（流动性时序普遍特征），动态面板可直接迁移（多股票×多日期）。**判定：储备（Phase 1.5 候选）**——① MVP Amihud 静态阈值已够（高持续→短期不失效，预测模型边际价值低）② 方法学参考非独立模块 ③ §3.7.5 微结构前瞻优先级更高。**重评条件**：① Phase 1.5 阈值校准选"动态面板+三特征"轻量方案 ② 实盘 6 月 Amihud 数据验证高持续 ③ 与 §3.7.5 对比 lead-time。

#### 3.7.13 AdjPIN 订单流信息/流动性分解 —— 储备（Phase 2 候选，§3.7.2 VPIN 配套细化）

**算法**（[Park 2026-07-14 SSRN 7119388](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7119388)，基于 Duarte & Young 2009 AdjPIN + Ghachem & Ersan 2025 ECM）：§3.7.2 拒绝 VPIN 留下 gap——**如何区分"信息驱动价格移动"与"纯流动性危机"**（§3.3 响应：信息驱动=跟随减仓，纯流动性=等待恢复）。AdjPIN 将订单流分解为 **AdjPIN（信息不对称成分**，知情交易概率）+ **PSOS（对称订单流冲击/流动性成分**，对称买卖双增，如做市商调仓/流动性提供者撤退）。Park 实证：ML 收益可预测性主要由**流动性成分（PSOS）**驱动——"能预测"≠"有信息含量"。估计方法（[Ghachem & Ersan 2025](https://www.tandfonline.com/doi/full/10.1080/14697688.2025.2515929)）：ECM 算法+对数似然分解，解参数空间大导致的数值不稳定+局部最优。**对 §3.7.2 VPIN 拒绝的补全**：

| 维度 | §3.7.2 VPIN（已拒绝） | §3.7.13 AdjPIN 分解（本条） |
|---|---|---|
| 检测目标 | 知情交易概率（单一指标） | 信息成分 + 流动性成分（分解） |
| 与 OBI 冗余 | 高（相关性 0.85+，ClusterLOB 实证） | 低——PSOS 流动性成分与 OBI 的卖压方向不同（PSOS 是对称双增，OBI 是单边卖压） |
| 对 §3.3 的价值 | 低（单一指标不分信息/流动性） | **高**——区分"信息驱动价格移动"（跟随减仓）vs"纯流动性冲击"（等待恢复，避免在流动性枯竭时交易） |

**sell_pressure 关系/A 股适配/判定**：§3.1.1 sell_pressure 是**单边卖压**度量，PSOS 是**对称双增**冲击度量——正交（前者检单边卖压危机，后者检做市商撤退型双边挂单同时消失）。A 股适配：tick 级买卖分类可用 Lee-Ready 规则或 tick rule；PSOS 在 A 股解释为"流动性提供者（含高频被动单）撤退的对称冲击"（A 股无正式做市商，科创板做市 2022 起）；ECM 每股每日迭代成本中等，全市场 ~5000 股不可行但可限定持仓股+观察池。**判定：储备（Phase 2）**——① §3.7.2 已拒 PIN 家族，须先验证 PSOS 相对 OBI 增量价值 ② ECM 计算成本 MVP 无预算 ③ 与 §3.7.5 Latent build-up 部分重叠（须先验证 §3.7.5 不够）。**重评条件**：① §3.3 实盘发现信息/流动性区分不足致响应失误（如纯流动性冲击中过度减仓）② §3.7.5 未覆盖对称流动性冲击 ③ tick 买卖分类管道+ECM 预算就绪。

#### 3.7.14 Signed Order Flow Kyle λ —— 有向订单流恢复方向性信息（Phase 2 候选，§3.1 流动性因子增强）

**算法**（[Aldridge 2026-07-01 arXiv:2607.01377](https://arxiv.org/abs/2607.01377)，"Liquidity Premium and Investment Horizons"）：从日度股票订单流估计 Kyle (1985) 价格冲击系数 **λ̂ = Cov(ΔP, OF_signed) / Var(OF_signed)**（OF_signed 有向：买发起为正、卖发起为负）——相比 Amihud ILLIQ = |r_d|/V_d（无向）恢复**方向性信息含量**。两种估计量：① 月内价格冲击回归（ΔP = λ·OF + ε，滚动月窗 OLS）② Amihud 式比率（日频 |ΔP|/|OF| 月均，有向 OF 替代无向 V）。CRSP 2020-2025 Fama-MacBeth：**有向订单流强预测当期与未来一月收益**，成交量波动预测较低未来收益（噪声交易方差扩大 λ、降低价格发现精度）；经逆向选择机制解 Constantinides (1986) 流动性溢价之谜。**与 §3.1 Amihud 的关系**：

| 维度 | §3.1 Amihud ILLIQ（已采纳） | §3.7.14 Signed Kyle λ（本条） |
|---|---|---|
| 方向性 | 无向（\|r\|/V） | 有向（OF_signed 回归） |
| 信息含量 | 仅流动性成本 | 流动性成本 + 信息含量 |
| 数据需求 | OHLCV（日频） | 需买卖分类（Lee-Ready/tick rule） |
| 计算成本 | 极低 | 中（需 tick 级买卖分类） |
| A 股数据 | 可得（日频 OHLCV） | 可得（miniQMT tick 数据） |

**A 股适配与判定**：signed OF 可从 Level-2 用 Lee-Ready/tick rule 重建；可作多因子模型流动性因子维度；A 股散户占比高噪声方差大，"噪声扩大 λ 降低价格发现"洞察尤其适配。**判定：储备（Phase 2）**——① §3.1 Amihud 无向 ILLIQ 已满足 MVP ② signed OF 需 tick 买卖分类管道（Phase 2 引入 Level-2 后评估）③ 与 §3.7.13 AdjPIN 同需 tick 分类可同期引入。**重评条件**：① miniQMT Level-2 tick 管道就绪 ② Amihud 实盘发现无向 ILLIQ 不足区分"信息驱动价格冲击"与"纯流动性成本" ③ 多因子模型需引入流动性因子维度。

#### 3.7.15 流动性尾部风险与价格发现 —— 大单非信息场景（Phase 2 候选，§3.3 LEVEL 响应理论支撑）

**算法**（[Çetin, Lin & Livieri 2026-07-21 arXiv:2607.01198](https://arxiv.org/abs/2607.01198)，LSE）：序贯 LOB 中流动性供给方只观测聚合订单流；非知情订单流重尾（Student-t, ν>2）时大单在更宽深度范围内仍"合理地非知情"，**压平价格冲击、减缓学习**。非线性不动点方程刻画边际成本计划均衡（证明存在性+后验一致性+尾部渐近）；AAPL 10 档实证：重尾大单后持续买卖价差与远端交叉诊断。**核心洞察——"大单 ≠ 信息"**：颠覆 Easley-O'Hara"大单=知情"传统假设，对 A 股尤其重要（大单常源于机构调仓/融资盘平仓/公募赎回）。**与 §3.3 LEVEL 响应的关系**：重尾下大单更可能非信息——倾向"等待恢复"而非"跟随减仓"；与 §3.7.13 AdjPIN 互补（AdjPIN 从订单流分解区分，Çetin 从价格发现学习速度区分）；T+1 下大单次日开盘反应可验证假设。**判定：储备（Phase 2）**——① 理论性强需不动点方程数值化 ② 与 AdjPIN 功能重叠（AdjPIN 更工程化有 ECM 实现）③ MVP 大单阈值+Amihud 双条件已够。**重评条件**：① 实盘大单后"减仓 vs 等待"决策失误频繁 ② AdjPIN 上线后分离仍不充分 ③ 需大单冲击定量预测模型。

#### 3.7.16 跨市场传导与传染模型（作战地图 BM-RC-12-B / BM-RC-12 闭合，design）

**定位**：BM-RC-12-B（跨市场传导与传染模型，L4 风控域，design，planned D_RISK/D_CROSS_ASSET 域）——黑天鹅事件发生后预测跨市场传导与二阶效应以提前防御：**一阶传导**（股市→债市/汇率/商品）+ **二阶效应**（流动性挤兑/信用利差走阔/波动率反馈循环）+ **传染强度与时滞估计**（Hawkes 多元版）。数据流：黑天鹅事件信号（RC-12-A）→ 传导路径预测 → 二阶效应评估 → 防御建议（对冲/降仓）→ RC-12-C 流动性危机模拟。**裁定：登记远期 + 激活条件（不就地施工）**。理由：① 传染强度/时滞定量估计是 §3.7.1 Hawkes 的跨市场扩展——多元 Hawkes 依赖跨市场行情数据管道（债/汇/商品指数日频），管道当前不存在，就地施工无数据承载；② MVP 已有布尔级覆盖——跨市场传导判定由 [36号 §3.5.2](36_var_es_monitoring.md) `EVENT_TO_BS_MODE["CONTAGION"] → BS005_CONTAGION` 事件映射承载（"有没有传导"布尔信号 → drawdown_controller 分级响应），本节增量是"多强、多快"定量层，属精度提升非生存底线；③ 与本备忘主线正交——§3.1-§3.6 管"传导到达后怎么响应"，本节管"会不会到达、以多强到达"。**激活条件（重评条件）**：① 跨市场行情数据管道就绪（国债期货/汇率/商品指数日频接入）② §3.7.1 Hawkes 上推 Phase 1.5 时同步评估多元扩展（共享事件流与 μ/α/β 拟合管线）③ 实盘跨市场传导误判（BS-005 触发但实际无传导，或未触发但组合受外围冲击）≥2 次。

**远期设计要点（登记，激活后细化）**：① 一阶传导路径——股市（组合持仓/沪深300）→ 债市（10Y 国债期货）、汇市（USDCNH）、商品（南华商品指数），路径判定用跨市场日频收益相关性突变（对齐 32号 §2.10.5 B short vs long window ρ 偏离度 shrinkage）；② 二阶效应——流动性挤兑（本备忘 §3.1/§3.2 信号在关联市场同步触发）、信用利差走阔（信用债指数-国债利差，数据源待建）、波动率反馈循环（对齐 §3.7.1 2026-07 A 股量化危机活体验证）；③ 多元 Hawkes 交叉激发项 α_ij + 时滞核（指数 β 或幂律），拟合样本=历史黑天鹅窗口（2015 股灾/2016 熔断/2020 疫情/2024 政策，BM-RC-12-A 模式库复用）；**退化策略**=传染模型失效按最坏情况假设（全市场同向下跌，BM-RC-12-B degradation 原值）。**父环节 BM-RC-12（极端事件与黑天鹅，design）随之闭合**：① BM-RC-12-A 黑天鹅模式库（7 模式）已由 [36号 §3.5.2](36_var_es_monitoring.md) BlackSwanMode（BS001-BS007）+ `EVENT_TO_BS_MODE` 覆盖（36号 production）② BM-RC-12-B 由本节承载 ③ BM-RC-12-C 流动性危机模拟由本备忘 §3.1-§3.6 覆盖（MVP production，§3.7.x 为前瞻增强层）——父环节无遗留未映射子环节，闭合。

### 3.8 施工流程算法总览（盘中流动性监控循环）

> ✅ 已施工（`liquidity_crisis_manager` MOD-RK-21 `run_intraday_liquidity_check`，54 测试全绿，2026-08-13；编排层调用方接入为后续会话工作）——检测→响应→恢复→涨跌停处理串成单循环，与 35 号 §3.13 / 36 号 §3.12 施工流程对齐。

**盘中流动性监控循环伪代码**（MOD-RK-10 `liquidity_monitor` 每 N 秒轮询，对齐 35 号 §3.13 的 30 秒轮询周期）：

```python
def intraday_liquidity_loop(market_data_snapshot, position_state, recovery_state,
                            poll_interval_seconds=30):
    """盘中流动性监控主循环——检测→涨跌停→响应→恢复 四阶段编排。
    
    编排顺序（关键）：
      1. 涨跌停检测（§3.5.1）先行——涨跌停时 spread 失效须置 1.0 才能进入 §3.1 AND 条件
      2. 流动性危机检测（§3.1）——sell_pressure ≥ 0.65 AND spread ≥ 0.5%
      3. 响应执行（§3.3）——按 LEVEL_1/2/3 分级，停开仓仅平仓
      4. 恢复判定（§3.6）——hysteresis 半阈值 + CUSUM 持续时间门控
    
    A 股 T+1 约束：LEVEL_1/2 响应中"仅平仓"受 T+1 限制——当日买入不可卖，
    故平仓只能减已持仓（T-1 及更早），新建仓被 halt_new_orders 阻断。
    """
    # ── 阶段 1：涨跌停检测（§3.5.1）——须先于 §3.1，因 spread 在涨跌停时失效 ──
    limit_status = detect_limit_status(market_data_snapshot)  # NORMAL/NEAR_LIMIT/LIMIT_UP/LIMIT_DOWN/UNKNOWN
    effective_spread = market_data_snapshot.spread
    if limit_status == "LIMIT_DOWN":
        # 跌停时 spread 置 1.0 使 §3.1 AND 条件可满足（§3.5 算法断裂修复）
        effective_spread = 1.0
    elif limit_status == "LIMIT_UP":
        # 涨停时 spread 置 None 跳过检查（§3.5.1 联动表：买压主导非危机；
        # v1.1.0 修：原文涨跌停统一置 1.0，与 §3.5.1 表矛盾——涨停置 1.0 虽因
        # 卖压≈0 不会误触发，但置 None 语义更干净且阻断异常数据下的误触发）
        effective_spread = None
    
    # ── 阶段 2：流动性危机检测（§3.1）——双条件 AND ──
    sell_pressure = compute_sell_pressure(market_data_snapshot.order_book)  # §3.1.1 OBI 反转
    is_crisis = (sell_pressure >= 0.65) and (effective_spread >= 0.005)  # 0.5% = 0.005
    
    # ── 阶段 3：响应执行（§3.3）——分级，停开仓仅平仓 ──
    if is_crisis:
        level = classify_crisis_level(sell_pressure, effective_spread, limit_status)
        # LEVEL_1: halt new orders / LEVEL_2: reduce 30% / LEVEL_3: liquidate all + Kill Switch
        directive = build_escape_directive(level=level, position_state=position_state)
        # A 股 T+1：halt_new_orders=True 阻断新开仓；平仓仅作用于 T-1 及更早持仓
        execute_directive(directive)
        recovery_state.enter_crisis(level, timestamp=market_data_snapshot.timestamp)
    else:
        # ── 阶段 4：恢复判定（§3.6）——hysteresis 半阈值 + CUSUM 持续时间门控 ──
        if recovery_state.in_crisis:
            # §3.1 双条件活动信号计数（sell_pressure 超阈值 + spread 超阈值，范围 0-2）
            active_signals = (
                int(sell_pressure >= 0.65) + int(effective_spread >= 0.005)
            )
            recovered = check_recovery(
                current_spread=effective_spread,
                current_sell_pressure=sell_pressure,
                trigger_threshold_spread=0.005,      # 触发阈值
                recovery_threshold_spread=0.0025,    # 半阈值 0.25%
                trigger_threshold_pressure=0.65,
                recovery_threshold_pressure=0.50,    # 半阈值
                min_hold_minutes={1: 10, 2: 15, 3: 30}[recovery_state.level],
                elapsed=recovery_state.elapsed,
                current_level=recovery_state.level,
                active_signals=active_signals
            )
            # ⚠️ 用 is not None 判定而非真值检查——target_level=0（LEVEL_1→正常）是有效恢复
            #   （原 `if recovered:` 在 target_level=0 时为 False，会跳过恢复正常态，v1.0.11 修）
            if recovered is not None:
                recovery_state.exit_crisis(target_level=recovered)
                # 恢复后逐步放开（非立即满仓），对齐 35 号 §3.11 RECOVERY 阶梯
                notify_recovery_complete(recovery_state.level, target_level=recovered)
    
    # ── 日频结构性监控（§3.2）异步——盘后批量，不在盘中循环 ──
    # Amihud illiquidity + volume shrinkage 由 MOD-RK-08 LiquidityMonitor 日度执行
    
    return LiquidityLoopResult(
        limit_status=limit_status,
        sell_pressure=sell_pressure,
        effective_spread=effective_spread,
        is_crisis=is_crisis,
        recovery_state=recovery_state
    )
```

**编排顺序的设计理由**：

| 顺序 | 阶段 | 为什么在此位置 |
|---|---|---|
| 1 | 涨跌停检测（§3.5.1） | spread 在涨跌停时失效——须先检测涨跌停并置 effective_spread=1.0，否则 §3.1 的 `spread ≥ 0.5%` AND 条件在涨跌停时因 spread=None 而短路，LIQUIDITY_CRISIS 无法触发（§3.5 算法断裂修复的核心） |
| 2 | 危机检测（§3.1） | 用阶段 1 的 effective_spread（而非原始 spread）做双条件 AND 判定 |
| 3 | 响应执行（§3.3） | 检测到危机立即响应——halt_new_orders 须在下一笔订单前生效，故响应紧跟检测 |
| 4 | 恢复判定（§3.6） | 仅在非危机时检查恢复——危机中不检查恢复（防止"刚触发就恢复"的 thrashing），恢复须等危机信号消失后才评估 |

**与 35 号 §3.13 / 36 号 §3.12 的对齐**：
- **35 号 §3.13 盘中实时风控循环**：30 秒轮询回撤/VaR/仓位——37 号本循环与 35 号**并行**（同一 poll tick 内先跑 35 号回撤风控、再跑 37 号流动性风控），两者通过 `recovery_state` 状态共享（35 号 KILL 态禁止 37 号恢复，37 号 LEVEL_3 触发 35 号 Kill Switch）
- **36 号 §3.12 盘中 VaR/ES 重算**：三触发条件之一是"流动性危机"——37 号本循环检测到 LEVEL_2+ 时触发 36 号盘中重算（流动性恶化→VaR 失效→重算）
- **三循环编排**：35 号回撤风控（仓位上限）→ 36 号 VaR/ES（风险度量重算）→ 37 号流动性（执行约束）——三者乘性叠加，37 号是执行层最后一道门

**A 股 T+1 约束对循环的影响**：
- LEVEL_1/2 的"仅平仓"受 T+1 限制——当日买入不可卖，故平仓指令只对 T-1 及更早持仓生效，当日新建仓（若 halt_new_orders 未及时生效）需次日才能减
- LEVEL_3 清仓同理——Kill Switch 平仓指令分批拆单（每秒 ≤14 笔保守自限，远低于 300 笔/秒法规线留 20 倍余量，对齐 [33_budget_change_handler](33_budget_change_handler.md) §3.2.3 + 35 号 §3.5.1 A 股 2026 新规），当日买入部分次日补平
- 恢复后的"逐步放开"（RECOVERY 阶梯）受 T+1 限制较小——放开的是新开仓权限，T+1 只限制卖出不限制买入

## 4. 考虑过的替代方案（拒绝理由）

### 4.1 独立新建 LiquidityCrisisProtocol 模块 —— 拒绝
- **拒绝理由**：MOD-RK-10 已实现 LIQUIDITY_CRISIS 信号 + 三级警报 + Kill Switch 联动，重复造轮子违反 AI-dev 归因清晰度原则；G18 的价值是给已有实现补 why 层 + 对齐 §2.5.5 spec，不是新建基础设施；新建模块会制造"流动性危机检测有两个真相源"的歧义。

### 4.2 实时 tick 级 spread 监控 —— 拒绝（过度工程）
- **拒绝理由**：个人系统无需 tick 级监控基础设施（tick 盘口管道 + 实时 spread 计算 + 低延迟告警），投入产出比极低；MOD-RK-10 秒级/分钟级检测已足够（流动性危机是分钟级事件非微秒级）；机构做 tick 级是因为自身交易会影响流动性（大单冲击），个人小资金自身不影响。

### 4.3 流动性危机直接清仓 —— 拒绝
- **拒绝理由**：§2.5.5 明确是"停开仓仅平仓"不是清仓；危机时强制清仓会踩踏（卖在最低点）；只有 ≥3 信号（系统性崩盘）才清仓（LEVEL_3，"跑得快"比"卖得好"重要）——分级响应比一刀切更合理。

### 4.4 "价差 > 正常 5x" 相对阈值 —— 部分采纳（MVP 用绝对阈值）
- **拒绝理由（MVP）**：相对阈值需维护"N 日均价差"基准，每只票"正常 spread"不同（大盘股 0.01% vs 小盘股 0.3%），基准维护复杂；代码用绝对 0.5%（A 股正常票 0.01-0.05%，0.5% 已是 10-50 倍，与"5x"量级吻合，简单且误报低）。**重评条件**：实盘运行后若绝对阈值误报多（小盘股日常 spread 接近 0.5%），再上推相对阈值。

### 4.5 盘口深度实时监控 —— 拒绝（MVP 延后）
- **拒绝理由**：盘口深度（多档挂单量）需实时 Level-2 数据 + 深度衰减建模，是机构级基础设施；个人小资金订单 <1% ADV，深度对自身交易无意义（自己不消耗深度）；MOD-RK-08 Amihud（日频）+ MOD-RK-10 spread（盘内）已覆盖核心问题；依赖 depth 的复合评分（如 Polymarket 2026-06 Liquidity Score = (depth × volume)/(spread + ε)）一并暂缓。**重评条件**：AUM 增长到自身订单 >5% ADV 时。

### 4.6 VPIN 订单流毒性检测 —— 拒绝（过度工程）
- **拒绝理由**：VPIN 需 tick 级交易数据 + 时间桶成交量分类，是机构级闪崩预警指标（theplugg 2026-07 将其与 OBI、Depth-to-Volatility Decay 并列闪崩三大指标）；个人小资金不做市、不受 toxic flow 直接伤害；MOD-RK-10 卖压+spread 双条件已捕获 VPIN 试图检测的同类信号（流动性枯竭+单向压力）。**重评条件**：策略扩展到做市/提供流动性场景时。

### 4.7 Karimi 流动性-信贷联合破产边界 —— 暂缓（Phase 3 远期，选项之外更好的算法）

**算法**（[Karimi & Ahmadian 2026-07 arXiv:2607.17381](https://arxiv.org/abs/2607.17381)）：G18 危机检测与 G16 回撤 Protocol 是独立模块，但流动性与信贷风险的**非线性联合作用** disproportionally 加速破产。连续时间结构动态模型用 HJB 方程求解流动性-信贷联合精确破产边界；**Liquidity-Credit Spiral**（funding shocks+监管约束 Basel III LCR/NSFR→资产负债表调整→内生破产正反馈：流动性冲击迫使出售资产→信贷质量恶化→进一步流动性压力）；**边界凸性**——破产边界 B_exact 在 (λ,d) 平面（λ=流动性压力, d=信贷违约）是凸的，联合压力效应 > 独立效应之和；**代理函数** B_surrogate = w₁λ + w₂d + w₃λd（w₃>0 严格正反映凸性）允许实时监控；Iranian banking 细粒度资产负债表实证确认非线性阈值效应。**与 G18/G16 的关系**：流动性危机+回撤同时发生时破产风险 > 两者独立之和（联合状态需额外 risk premium）——Karimi 边界凸性为 MOD-RK-10 LEVEL_3（≥3 信号联动 Kill Switch）"多信号联合=系统性风险"直觉提供数学基础。

**为何暂缓**：① 银行级模型（LCR/NSFR 监管约束+信贷组合），个人系统无 ② 需 (λ,d) 联合状态变量，"信贷"维度缺失（无融资融券数据接入）③ MOD-RK-10 双条件 AND 是联合边界的简化版（两者同高即触发，近似联合状态检测）。**重评条件**：① 接入融资融券数据后构建 （流动性， 信贷） 联合状态监控 ② AUM 增长到需关注流动性-信贷螺旋 ③ 与 §3.7.8 Multiplex Network Hawkes 同步评估（Karimi 管联合状态边界，Multiplex 管传染通道）。

## 5. 上限定义（Ceiling）

### 5.1 系统上限
- **盘内检测**：MOD-RK-10 LIQUIDITY_CRISIS 信号（卖压 ≥0.65 AND spread ≥0.5%），双条件 AND
- **日频监控**：MOD-RK-08 Amihud ILLIQ（阈值 1e-8）+ 成交量萎缩（阈值 0.5，窗口 20 日）
- **三级警报**：LEVEL_1 停开仓 / LEVEL_2 降仓 30% / LEVEL_3 清仓 + Kill Switch
- **情绪断路器**：情绪指数 ≥0.85 → 强制升级 LEVEL_3
- **Kill Switch 联动**：仅 LEVEL_3（≥3 信号）联动，流动性危机单独不 Kill Switch
- **涨跌停处理**：spread 监控失效，跌停时 spread 置大值 1.0 触发 LIQUIDITY_CRISIS（卖压≈1.0 + spread=1.0 满足 AND），涨跌停状态检测接管（40_execution_broker 决策⑥⑭⑮）

### 5.2 演进路径
- **第一阶段（MVP，已实现）**：MOD-RK-10 绝对阈值（spread 0.5% + 卖压 0.65）+ MOD-RK-08 Amihud 日频。两级流动性监控 production
- **Phase 1.5（首批策略 track record 1-3 个月）**：① 阈值实盘校准（用实盘 spread/卖压分布回归拟合，替代经验默认值）② 相对 spread 阈值（spread / N 日均价差 > 5x，若绝对阈值误报多）③ 流动性指标接入策略层（流动性恶化的票降权或剔除）④ **双阈值方案**（2026-08 microstructure 实践）：spread > 3x N 日均值 = 早期预警（策略层降权），spread > 5x = 危机确认（触发 LEVEL_1）——3x 介于"正常"与"5x 危机"之间，能自适应不同流动性票（大盘股 0.05% 日常→0.15% 预警；小盘股 0.3% 日常→0.9% 预警）⑤ **OFI 动态维度**（§3.1.1 储备）：sell_pressure（静态存量）+ OFI（动态变化趋势）双维度 ⑥ **Hawkes 自激励前置预警**（§3.7.1 储备）：若阈值触发滞后，上推 Hawkes 强度作为前置预警层 ⑦ **Amihud 预测方法学**（§3.7.12 储备：阈值校准时用"动态面板 + 三特征（成交活跃度 + 滞后 Amihud + 市场不确定性）"轻量方案替代重 ML 栈——[SSRN 7125463](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7125463) 实证动态面板不输 XGBoost/SVR，流动性高持续意味着静态阈值短期不失效）
- **第二阶段（AUM 增长或策略需要）**：
  - 盘口深度监控（Level-2 多档数据 + 深度衰减建模）+ Bouchaud Propagator（冲击时间衰减结构，与 40_execution_broker 滑点模型协同）+ 流动性综合评分 Liquidity Score = (depth × volume)/(spread + ε)（depth/volume/spread 三者的复合归一化指标）
  - **Crumbling Labeler**（§3.7.3 远期储备）：区分机械撤退 vs 信息重定价，优化 LEVEL_3 清仓决策
  - **SaR 前瞻性框架**（§3.7.4 储备）：SaR(α)/ESaR(α)/TSaR(α) + 集中度调整，前瞻性滑点预测 + 识别脆弱盘口结构，与 Hawkes 叠加为双层前瞻预警
  - **Residual Supply 被迫卖出压力信号**（[arXiv:2605.30672 2026-05-29](https://arxiv.org/abs/2605.30672) Wang）：残余供给价格分解为库存风险补偿+资本与调整楔子，被迫卖出压力预测当期价格下跌+随后 1-6 月正收益（65bp/月，217bp/6 月），**全市场吸收能力紧张时 premium 翻倍**——A 股用公募赎回/北向净流出/融资余额下降近似 forced selling pressure 作 LEVEL_2 升级信号；Phase 2+ 远期（需 fund flow 数据接入）
  - **LRISK 系统级前瞻预警**（§3.7.11 储备，[SSRN 7110978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7110978)）：流量共振+组合重叠+流动性螺旋三大放大通道，提前 1-2 季度预测市场承压，A 股用公募赎回+北向净流出+融资余额 z-score 近似 flow commonality；Phase 2+ 远期（与 Residual Supply 同需 fund flow 数据，须先验证单资产级边际价值）
  - **AdjPIN 信息/流动性分解**（§3.7.13 储备，[SSRN 7119388](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7119388)）：AdjPIN 信息成分 + PSOS 流动性成分分解，区分"信息驱动价格移动"vs"纯流动性冲击"优化 §3.3 LEVEL 响应——信息驱动跟随减仓、纯流动性等待恢复避免流动性枯竭时交易；Phase 2 候选（ECM 估计计算成本中等）

### 5.3 为何这是上限而非妥协
- 个人账户小资金，多数订单 <1% ADV，自身交易不构成流动性冲击——流动性危机是市场级事件，检测市场级信号（卖压 + spread）已足够；MOD-RK-10 已是 5 信号系统性风险检测器的一部分，LIQUIDITY_CRISIS 是其中 1 个信号，复用边际成本为零
- 盘口深度/tick 级监控是机构级基础设施（需 Level-2 数据 + 低延迟管道），个人系统投入产出比极低；流动性危机的核心风险是"在流动性差时还去开仓"——停开仓（LEVEL_1）已消除此风险，无需更复杂的响应

## 6. 待裁定（暂缓）

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| 盘口深度实时监控 | 需 Level-2 多档数据 + 深度衰减建模，机构级基础设施 | AUM 增长到自身订单 >5% ADV |
| 相对 spread 阈值（5x 正常） | MVP 绝对 0.5% 已与"5x"量级吻合；相对阈值需维护 N 日均价差基准 | 实盘运行后绝对阈值误报多时 |
| 流动性指标接入策略层 | MOD-RK-08 is_illiquid 当前只产告警，未反馈到策略选股/权重 | Phase 1.5，策略层需要流动性过滤时 |
| 阈值实盘校准 | spread 0.5% / 卖压 0.65 / Amihud 1e-8 均为经验默认值 | 累积 3 个月实盘数据后回归拟合 |
| 恢复阈值实盘校准（v1.0.3 新增） | spread 半阈值 0.25% / sell_pressure 0.50 / 最短持续 10-15-30 分钟均为经验初始值 | 累积 3 个月恢复事件数据后评估 thrashing 率 |
| OFI 动态维度（v1.0.3 新增） | sell_pressure（静态）已够 MVP；OFI（动态）需盘口队列变化追踪 | Phase 1.5，静态阈值触发滞后时 |
| Hawkes 自激励前置预警（v1.0.3 新增） | 需 tick 事件流 + 历史危机参数拟合，成本中等 | MOD-RK-10 实盘 3 月发现阈值触发滞后时 |
| Crumbling Labeler 清仓优化（v1.0.3 新增） | 需神经网络 + 标注数据，ICLR 2026 尚无开源实现 | 论文开源 + AUM 增长到清仓成本显著 |
| SaR 前瞻性框架（v1.0.6 新增） | 需重定义 HHI 为"挂单量集中度"+ 校准 η 参数；MVP 双条件 AND 已捕获"正在发生的危机" | 实盘 6 月盘口数据 + AUM 增长到自身交易影响盘口 |
| Residual Supply 被迫卖出压力信号（v1.0.12 新增） | 需 fund flow 数据（公募赎回/北向净流出/融资余额）接入，A 股数据源与论文 US 共同基金流不同须适配 | Phase 2+，公募/北向数据可稳定获取 + AUM 增长到 forced selling pressure 信号有边际价值时 |
| LRISK 系统性流动性风险前瞻指标（v1.0.13 新增） | 系统级指标非个股检测；A 股公募持仓季度披露滞后，"提前两季度"预警可能退化为"提前数周"；与 Residual Supply 重叠须先验证单资产级边际价值 | Phase 2+，§5.2 Residual Supply 验证有效后 + 公募持仓数据频率提升 + 与 Hawkes 日级预警对比 lead-time |
| 欧洲 ML 流动性预测方法学（v1.0.13 新增） | 方法学参考非独立模块；MVP 阶段 Amihud 静态阈值已够（流动性高持续），预测模型边际价值低 | Phase 1.5 阈值校准时选"动态面板+三特征"轻量方案作为 ML 替代 + 实盘 6 月 Amihud 数据验证高持续性 |
| AdjPIN 订单流信息/流动性分解（v1.0.13 新增） | §3.7.2 已拒绝 VPIN/PIN 家族，须先验证 PSOS 成分相对 OBI 增量价值；ECM 估计计算成本中等（每股每日迭代） | Phase 2，§3.3 LEVEL 响应发现"信息驱动 vs 纯流动性"区分不足 + §3.7.5 Latent build-up 未覆盖对称流动性冲击 + tick 买卖分类管道就绪 |
| 与 G16 Kill Switch 对齐（✅ 已解决 v1.0.1） | G16 于 2026-08-10 升级 active v1.0.0，§3.5 Kill Switch 触发条件已填，双向引用已建立 | 已解决，详见决策④ |
| IPO 数据源接入（✅ 已解决 v1.2.1） | §3.2a 原文声称 akshare_provider `stock_ipo_info` 已 production，2026-08-13 施工全仓核查实证**该接口不存在**（akshare_provider 无 ipo capability）。算法已按数据源无关接口施工（IPOEvent 注入），数据管道接入属数据层施工范围 | ✅ 已闭环（2026-08-17 AI-IPO-001，tracker #114）：akshare `ipo_calendar` capability（替代源=巨潮 `stock_new_ipo_cninfo` 全市场新股列表，匿名无反爬）+ c1_market.ipo_calendar 表（DDL-as-Code）+ tasks.yaml `ipo_calendar_daily`（daily_capital）+ DS-105/JOB-086 登记 |

## 7. 待定问题（讨论要点 resolved）

> 以下讨论要点来自 00_index §3 G18，已逐项对齐落入 §3 决策。

- [x] ① 买卖价差监控（>正常 5x 触发）→ **决策①**：复用 MOD-RK-10 LIQUIDITY_CRISIS，spread 作为输入参数，阈值 0.5% 绝对（与"5x"量级吻合），双条件 AND（卖压 + spread）
- [x] ② 流动性危机→立即停止开仓仅允许平仓 → **决策③**：对齐 §2.5.5 + MOD-RK-10 LEVEL_1（新开仓 0%，现有持仓不强制减，允许策略主动平仓但不强制）
- [x] ③ 流动性指标定义（换手率/成交额/盘口深度）→ **决策②**：日频用 Amihud ILLIQ（|r_d|/V_d）+ 成交量萎缩比率（MOD-RK-08）；盘内用卖压 + spread（MOD-RK-10）；盘口深度暂缓（Phase 2）
- [x] ④ 与 Kill Switch 的关系 → **决策④**：流动性危机单独 = LEVEL_1 停开仓（不 Kill Switch）；≥3 信号 = LEVEL_3 清仓 + Kill Switch。比 §2.5.5 更精细，不违反 spec
- [x] ⑤ A 股涨跌停流动性失效处理 → **决策⑤**：涨跌停时 spread 监控失效（盘口单价位），涨跌停状态检测接管（§3.5.1 形式化检测算法），由 40_execution_broker 决策⑥⑭⑮处理；持仓票跌停 = 流动性危机子类
- [x] ⑥ 危机恢复算法（v1.0.3 新增）→ **决策⑥**：滞后-恢复双阈值（hysteresis）+ CUSUM 式持续时间门控，恢复条件 = 半阈值 + 持续 N=5 分钟 + 最短持续时间门控（LEVEL_1 10min/LEVEL_2 15min/LEVEL_3 30min）
- [x] ⑦ 2026 前沿算法评估（v1.0.3 新增）→ **决策⑦**：Hawkes 自激励（Phase 1.5 储备）/ VPIN 重评（维持拒绝，与 OBI 相关性 0.85+ 信息冗余）/ Crumbling Labeler（Phase 2 远期储备，区分机械撤退 vs 信息重定价优化清仓决策）
- [x] ⑧ 施工流程算法总览（v1.0.4 新增）→ **§3.8 盘中流动性监控循环**：四阶段编排（涨跌停检测→危机检测→响应执行→恢复判定）伪代码 + 编排顺序设计理由表 + 与 35 号 §3.13/36 号 §3.12 三循环并行对齐 + A 股 T+1 约束影响。补齐 35/36 号均有日度循环+盘中循环+总览时序但 37 号 缺编排总览的施工流程 gap
- [x] ⑨ SaR 前瞻性框架评估（v1.0.6 新增）→ **§3.7.4 Slippage-at-Risk**：arXiv:2603.09164 Sepper 2026-03 提出的前瞻性流动性风险框架，含 SaR(α)/ESaR(α)/TSaR(α) 三度量 + 集中度调整（HHI 弹性 η≈1.5）。与现有双条件 AND（回溯性、布尔触发、不感知结构）维度互补：SaR 是前瞻性 + 连续分位数 + 感知集中度。判定 Phase 2 储备，与 Hawkes 叠加为双层前瞻预警

## 8. 引用

### 8.1 相关设计备忘
- [30_multi_strategy_concurrency §2.5.5](30_multi_strategy_concurrency.md) Kill Switch 流动性危机触发条件（买卖价差 > 正常 5x → 立即停止开仓仅允许平仓）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) §3.5（G16，active v1.0.0，Kill Switch 触发与执行路径——流动性危机行反向引用本备忘）
- [40_execution_broker](40_execution_broker.md) 决策⑥⑭⑮（涨跌停拒单/挂单价/临时停牌——执行层协同）
- [00_index_trading_decision §3 G18](00_index_trading_decision.md) 流动性危机处理主题组定义
- [01_design_memo_management_spec §4.3](01_design_memo_management_spec.md) 设计备忘推荐章节结构

### 8.2 相关作战地图
- [battle_map_09_risk_control.md](../battle_map/battle_map_09_risk_control.md) 风控阶段：
  - BM-RC-02-E Kill Switch 状态检查（production，盘前拦截拉闸时拒新单）
  - BM-RC-03 Kill Switch 熔断（production，回撤/VaR/Owner 触发，冷却 30 分钟）
  - BM-RC-04-E 流动性风险监控（production，持仓流动性监控）
  - BM-RC-06 系统性风险检测（production，5 大信号含 LIQUIDITY_CRISIS + 三级警报）
  - BM-RC-12-C 流动性危机模拟（design，极端流动性枯竭压力测试）

### 8.3 depgraph 模块（用 path/blueprint_id 引用，非 node_id）

| 模块 | blueprint_id | path | 域 |
|---|---|---|---|
| AshareSystemicRiskDetector | MOD-RK-10 | `src/zephyr/risk/core/ashare_systemic_risk_detector.py` | D_RISK |
| LiquidityMonitor | MOD-RK-08 | `src/zephyr/risk/core/liquidity_monitor.py` | D_RISK |
| Kill Switch（BM-RC-03） | MOD-RK-17 | `src/zephyr/risk/stop_loss.py` | D_RISK |

### 8.4 外部参考
- Amihud (2002) "Illiquidity and stock returns" — ILLIQ = |r_d|/V_d 非流动性指标
- tradingwyckoff 2026-01 Kill Switch Protocol — §2.5.5 来源
- A 股涨跌停流动性失效：涨停板买单堆积/跌停板卖单堆积，盘口退化为单价位（上交所 2026 修订交易规则 §3.3.13 涨跌幅限制）；流动性度量经验法则：spread <0.1% = 高流动性，>1% = 低流动性
- Beelaa 2026-08 做市商撤退与 spread 扩大实证：2026-01 比特币闪崩，IBIT spread 从 2-3bps 扩至 8-10bps（3-4 倍），**5% 抛压→15% 暴跌**（流动性放大 3 倍）——支撑"双条件 AND"假设（卖压+spread 同时扩大=流动性枯竭）+ "LEVEL_1 停开仓不清仓"决策（危机时强制清仓会踩踏）
- theplugg 2026-07 闪崩三阶段模型：机构大单冲击 → 算法撤退 + spread 扩大 → 跨资产级联 + stub quote 成交——VPIN/OBI/Depth-to-Volatility Decay 三大早期预警指标（本系统用卖压+spread 等价覆盖）
- LobeHub 2026-08：spread > 3x average 早期预警（§5.2 双阈值方案来源）；Polymarket 2026-06：OBI >0.60 买压主导/<0.40 卖压主导（与 sell_pressure 0.65 阈值等价，sell_pressure = 1 - OBI）；ClusterLOB 2026-06：VPIN 与 OBI 相关性 0.85+ 信息冗余（§3.7.2 维持拒绝依据）
- stockalpha.ai 2026-02 + arxiv 2310.09273 Hawkes λ(t) = μ + Σ α·exp(-β(t-t_i))——§3.7.1 储备来源；ICLR 2026 Crumbling Labeler（机械撤退 vs 信息重定价）——§3.7.3 远期储备来源
- [arXiv:2603.09164](https://arxiv.org/abs/2603.09164) Sepper 2026-03 SaR 框架——§3.7.4 来源（Hyperliquid 2025-10-10 清算级联实证 SaR 系统性压力领先有效性）；[arXiv:2608.03616](https://arxiv.org/abs/2608.03616) 2026-08 强平级联群组分析——§3.7.4/§3.7.7/§3.7.7.1 实证支撑（级联起始突变 + 两类型分类 + 预警异质性）；[arXiv:2604.20949](https://arxiv.org/abs/2604.20949) Hiremath & Hiremath 2026-04 Latent build-up 检测——§3.7.5 来源（正 lead-time +18.6 timesteps/+38 秒，优于 CUSUM/BOCPD/HMM）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 由 00_index G18 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 / 1.0.1 | 骨架→active，5 项讨论要点定型 + G16 对齐解决 | 复用 MOD-RK-10 双条件 AND + MOD-RK-08 Amihud 日频；响应=LEVEL_1 停开仓仅平仓；危机单独不 Kill Switch，≥3 信号联动；涨跌停由执行层处理；§2.5.5"5x"与代码"0.5% 绝对"量级吻合对齐；tick 级/盘口深度监控判定过度工程暂缓。35号同步升 active v1.0.0，§3.5 双向引用建立，更新 4 处过时"骨架态"描述（§1/§3.4/§6/§8.1） |
| 2026-08-10 | 1.0.2 | 算法断裂修复 + 逃生执行器补全 + 2026-08 实证对齐 | ① 跌停时 spread 置 1.0 使 AND 可满足（原置 None 信号无法触发）② §3.3 补 build_escape_directive 指令结构+守卫+RK-17 消费者 ③ §8.4 补 Beelaa/theplugg/LobeHub/Polymarket 实证 ④ §4.6 拒绝 VPIN + §4.5 Liquidity Score 暂缓 + §5.2 双阈值方案 |
| 2026-08-10 | 1.0.3 | 施工流程算法补全 + 选项外更好算法评估 | ① §3.6 危机恢复 hysteresis + check_recovery（10/15/30 分钟门控）② §3.1.1 sell_pressure OBI 反转公式 ③ §3.1.2 Quoted Spread 公式 ④ §3.5.1 涨跌停五状态检测 ⑤ §3.7 Hawkes（Phase 1.5）/VPIN（维持拒绝）/Crumbling（Phase 2）评估 ⑥ §5.2/§6/§7/§8.4 同步 |
| 2026-08-10 | 1.0.4 / 1.0.5 | §3.8 施工流程总览 + §2.4 指数熔断澄清 | 四阶段编排（涨跌停检测→危机检测→响应执行→恢复判定）+ 与 35号 §3.13/36号 §3.12 三循环对齐 + T+1 影响，编排关键=涨跌停检测须先于危机检测（spread 失效须置 1.0）；A 股指数熔断 2016-01-07 暂停（磁吸效应废止），本协议"熔断"指策略级 Kill Switch 非市场级 |
| 2026-08-10 | 1.0.6 – 1.0.14 | §3.7.x 前沿评估 9 批次登记 + §2.4/§4.7/§5.2/§6 同步 | 1.0.6 §3.7.4 SaR（arXiv:2603.09164，SaR/ESaR/TSaR+HHI η≈1.5）+ arXiv:2608.03616 级联两类型；1.0.7 §3.7.5 Latent build-up（arXiv:2604.20949，正 lead-time +18.6 timesteps/+38 秒，优于 CUSUM/BOCPD/HMM）；1.0.8 §3.7.1 Hawkes 更新（arXiv:2512.08000 A 股实证+图熵领先 7-12 天+2026-07 危机验证 CSI300 -5.81%/科创50 -17.46%）；1.0.9 §2.4 LAN 通道关闭交叉引用（≥2ms，TWAP 5%→3-4%，spread 0.5% 三月重校，三方对齐）；1.0.10 §3.7.6/§3.7.7/§3.7.8 + §4.7（ExsdHawkes KKT 分离 / Liquidation Cascade 三因子 λ≈0.1-0.2 / Multiplex Network Hawkes / Karimi 联合边界凸性 B_surrogate=w₁λ+w₂d+w₃λd）；1.0.11 §3.7.7.1/§3.7.9/§3.7.10（39 配置无事件不变量+taker 方差压缩 p≈5×10⁻⁶ / Weng Johnson S_U 消牛熊偏差 / Zhou 平方根冲击操纵周期必要条件 Hopf 分岔）；1.0.12 Residual Supply（arXiv:2605.30672 premium 翻倍，65bp/月 217bp/6 月）；1.0.13 §3.7.11/§3.7.12/§3.7.13（LRISK 提前两季度 / 动态面板不输 ML / AdjPIN PSOS 与 OBI 正交）；1.0.14 §3.7.14/§3.7.15（Kyle λ̂=Cov(ΔP,OF)/Var(OF) / Çetin 大单≠信息 Student-t ν>2）——均 Phase 1.5-3 储备/远期非施工缺失 |
| 2026-08-10 | 1.0.15 / 1.0.16 | §3.2a IPO 流动性抽离预警 + §3.6 check_recovery 签名修复 | 长鑫科技 688825 募资 579-666 亿缺口发现；drain_ratio=未来5日募资/20日均成交额，4 级→position_cap_adjustment，与 26号 §2.5a 联动（事前预警 vs §3.2 事后检测正交）；check_recovery 定义与 §3.8 调用点统一为参数化阈值签名（消除两处真相源），修 `if recovered:` 真值检查 bug（target_level=0 被跳过）→ `is not None` |
| 2026-08-12 | 1.0.17 / 1.0.18 | 作战地图全覆盖补丁 BM-RC-12-B / BM-RC-12 闭合 + BM-RC-06-A 锚定 | §3.7.16 跨市场传导登记远期+激活条件（管道不存在无承载，MVP 布尔级由 36号 §3.5.2 CONTAGION→BS005 承载；退化=全市场同向下跌最坏假设），父环节 BM-RC-12 闭合；§3.1 末尾补 BM-RC-06-A 映射块，环节级可追溯；frontmatter date→2026-08-12 |
| 2026-08-13 | 1.1.0 | 施工落地 + 施工审查修复 3 处文档缺陷 | AI-LIQ-001：新建 MOD-RK-21 liquidity_crisis_manager 承载六算法（§3.1.1/§3.1.2/§3.5.1/§3.6/§3.8/§3.2a，检测委托 MOD-RK-10，阈值从 detector.config 读取），54 测试全绿；修 §3.1.1 公式代数错误（ΣVolAsk/(ΣVolBid+ΣVolAsk)）+ §3.8 涨跌停 spread 矛盾（LIMIT_DOWN→1.0/LIMIT_UP→None）+ §3.2a 数据源虚标（akshare 无 ipo capability→§6 待裁定）；commit d53693a1/16a089c8/db695f9d |
| 2026-08-14 | 1.1.1 | 压缩精简 | 已施工内容折叠，零信息丢失审查通过（AI-DOCS-001） |
| 2026-08-17 | 1.2.1 | IPO 数据源接入闭环（tracker #114，AI-IPO-001） | §3.2a 数据管道落地：akshare `ipo_calendar` capability（巨潮 `stock_new_ipo_cninfo` 替代源）+ c1_market.ipo_calendar 表 + ipo_calendar_daily 盘后调度 + DS-105/JOB-086；§6 待裁定行与结案报告同步闭环 |
| 2026-08-15 | 1.1.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-05） | §3.4 差异对齐 380 字段要点化（spec/代码实现/G16 对齐三要点，过程性叙述删）；§5.2 第二阶段 500 字段按候选拆 6 子项（全部链接/参数保留）；全篇扫描无其他可压缩点——OBI 公式 ΣVolAsk/(ΣVolBid+ΣVolAsk)、0.65/0.5%/0.25%/0.50 阈值、min_hold 10/15/30 分钟、IPO 四级 0.01/0.02/0.03→1.0/0.90/0.75/0.60、LEVEL_1/2/3 响应矩阵、Amihud 1e-8/萎缩 0.5、BM 锚点/开放问题/链接逐项零丢失 |
| 2026-08-17 | 1.2.0 | LEVEL_3 生产接线闭环（AI-LVL3-001） | 结案报告 L21 遗留第一项闭环：①`detector.check()` 嵌入 `risk_layer_orchestrator.evaluate_intraday`（与 VaR/ES/回撤同层，systemic_detector+systemic_input_provider 成对注入即生效）②LEVEL_3 → `build_escape_directive` → `_engage_kill_switch` 单一仲裁点 → `execute_kill_switch_liquidation` 消费链接通 ③§3.6 降级机接线（复用 MOD-RK-21 `check_recovery`/`LiquidityRecoveryState`，LEVEL_3→LEVEL_2 冷却 30min+信号≤2+spread<0.3% 逐级迁移，降级不解除熔断闩锁——35 号 KILL 态人工复位不变式保持）④tracker #42①编排层接入 35 号 §3.13 调用方并入本批闭环（生产载体=trading_session 调仓循环+orchestrator 同 tick）；红队三向量非 mock 实证 16 项全绿（多信号 LEVEL_3 全链/情绪断路器 0.85 强制升级/冷却期逐级降级+非 LEVEL_3 逃逸守卫），28 项 orchestrator 测试两轮全绿；IPO 数据源接入登记遗留（§6 持续有效） |
