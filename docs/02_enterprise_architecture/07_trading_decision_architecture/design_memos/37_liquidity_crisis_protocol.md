---
ttl: permanent
doc_type: architecture_view
title: 流动性危机处理
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.16"
date: 2026-08-10
topic: liquidity_crisis_protocol
scope: 07_trading_decision_architecture
---

# 流动性危机处理

> 本备忘记录"流动性危机识别→响应"的选型推理与上限定义。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
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
| 状态 | active 1.0.13（5 项讨论要点已定型 + G16 对齐已解决 + 涨跌停算法断裂修复 + 逃生执行器补全 + 2026-08 实证对齐 + 危机恢复算法补全 + sell_pressure/spread/涨跌停形式化 + Hawkes/VPIN/Crumbling Labeler 2026 前沿评估 + §3.7.4 SaR 前瞻性框架评估（选项之外更好算法） + §3.7.5 Latent Microstructure Regime Detection 隐含微结构 regime 转变检测（选项之外更好算法，正 lead-time 优于 CUSUM/BOCPD/HMM） + §3.8 盘中流动性监控循环施工流程总览 + §2.4 指数熔断澄清 + §3.7.1 Hawkes 2026-08 最新研究更新（A股直接实证 arXiv:2512.08000 + 图熵领先7-12天预警 An&Dai 2026-08-06 + 2026-07 A股量化危机活体验证，预警时间从分钟级升级到日级）+ §2.4 v1.0.9 新增 2026-07-31 交易所 LAN 通道关闭交叉引用（流动性结构影响 + 三方对齐 33号/40号/00_index）+ §3.7.6 ExsdHawkes 状态消失扩展（v1.0.10 Kimura arXiv:2604.23961 KKT 分离估计+物理约束避免爆炸分支比）+ §3.7.7 Liquidation Cascade 三因子框架（v1.0.10 Garcia Seuma arXiv:2608.03616 推翻临界级联假设，severity=冲击×路径×流动性撤回）+ §3.7.7.1 临界性预警异质性（v1.0.11 Garcia Seuma Part I arXiv:2607.27070 39配置系统测试，无事件不变量+吃单订单流方差压缩群体级前兆+冲击类型识别约束）+ §3.7.8 Multiplex Network Hawkes 系统性风险（v1.0.10 Zelvyte&Griffin arXiv:2606.15755 多层网络通道分离）+ §3.7.9 Weng A股羊群效应 Johnson S_U 变换（v1.0.11 arXiv:2607.27063 A股专属agent-based网络+Johnson S_U消除牛熊偏差，时间×截面双维度预警互补Hawkes）+ §3.7.10 Zhou 平方根冲击操纵周期（v1.0.11 arXiv:2607.05141 A股专属±10%涨跌停+T+1+隐形分配，平方根冲击是内生操纵周期必要条件，§3.7.x系列统一理论支撑）+ §4.7 Karimi 流动性-信贷联合破产边界（v1.0.10 arXiv:2607.17381 HJB 联合边界凸性，LEVEL_3 联动理论支撑）+ §5.2 Residual Supply 被迫卖出压力信号（v1.0.12 arXiv:2605.30672 全市场吸收能力紧张 premium 翻倍，A 股适配用公募赎回/北向净流出/融资余额近似）+ §3.7.11 LRISK 系统性流动性风险前瞻指标（v1.0.13 SSRN 7110978 Jourde/Saillard/Van Dijk 三大放大通道流量共振+组合重叠+流动性螺旋，提前1-2季度预测市场承压，§3.7.x系列补系统级前瞻预警层）+ §3.7.12 欧洲 ML 流动性预测对比（v1.0.13 SSRN 7125463 Arakelia等 动态面板不输XGBoost/SVR，流动性高持续+三驱动因子为Phase 1.5阈值校准提供方法学）+ §3.7.13 AdjPIN 订单流信息/流动性分解（v1.0.13 SSRN 7119388 Park 信息成分+PSOS流动性成分，§3.7.2 VPIN拒绝后补"信息驱动vs纯流动性"区分路径，优化§3.3 LEVEL响应）） |

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
- **2026-07-31 交易所 LAN 通道关闭（v1.0.9 新增交叉引用）**：上交所正式关闭机房内局域网交易行情线路，统一切换广域网，核心硬约束：广域网线路双向时延不得低于 2ms（含存量+新增线路）。物理链路层抹平微秒级抢跑优势（旧机房内网直连 0.13ms-10μs → 新广域网最低 2ms）。首日成交从 2.56 万亿缩至 2.01 万亿（缩 5488 亿），纯超高频量化超额从 14% 回落至 3% 以内，量化行业从"拼网速"→"拼研究"时代。**对流动性的直接影响**：① 流动性收缩使大额强裁冲击成本上升——建议将 [33_budget_change_handler](33_budget_change_handler.md) §3.2.3 的 `TWAP_LARGE_ORDER_THRESHOLD` 从总资产 5% 下调至 3-4%（保守自限，留流动性冲击余量）；② 高频做市商超额收益压缩退场，盘口深度可能变薄——§3.1.2 Quoted Spread 阈值 0.5% 须在上线后 3 个月重新校准（旧阈值基于高频做市商活跃的盘口，新结构下 spread 中枢可能上移）；③ §3.7 Hawkes 自激励过程的"高活跃期延续趋势"判定（[arXiv:2512.08000](https://arxiv.org/abs/2512.08000) A 股实证）需在新流动性结构下重新拟合基线。与 [00_index §3 G22⑨](00_index_trading_decision.md) + [40_execution_broker](40_execution_broker.md) + [33_budget_change_handler §3.2.3](33_budget_change_handler.md) 三方对齐。

## 3. 决策

### 3.1 决策①：盘内流动性危机检测——复用 MOD-RK-10 LIQUIDITY_CRISIS 信号

**决策**：复用已实现的 [AshareSystemicRiskDetector](file:///d:/ZephyrAlpha/src/zephyr/risk/core/ashare_systemic_risk_detector.py)（MOD-RK-10，production）的 LIQUIDITY_CRISIS 信号，作为盘内流动性危机检测主路径。**不新建**独立 LiquidityCrisisProtocol 模块。

**已实现能力**（代码已实现）：
- `_check_liquidity_crisis(sell_pressure, bid_ask_spread)`：**双条件 AND** 触发——卖盘压力 `>= 0.65` 且买卖价差 `>= 0.005 (0.5%)`，两者同时满足才判定流动性危机
- `bid_ask_spread` / `sell_pressure` 作为 `detect()` 的**输入参数**由上游数据层提供（MOD-RK-10 不自行计算 spread，只做阈值判定）
- 三级警报按触发信号数递进：1 信号 → LEVEL_1 停开仓 / 2 信号 → LEVEL_2 降仓 30% / ≥3 信号 → LEVEL_3 清仓 + 联动 Kill Switch
- 情绪断路器：情绪指数超阈值（0.85）→ 强制升级至 LEVEL_3

**为何双条件 AND 而非单条件**：
- 单看 spread 扩大可能是低流动性票的常态（小盘股日常 spread 就大），误报高
- 单看卖盘压力可能是正常调仓（机构换仓时卖盘也会短期升高）
- 两者同时出现才是真正的流动性危机信号（卖压 + 价差扩大 = 流动性正在枯竭）
- 这与 §2.5.5 的"价差 > 正常 5x"方向一致：价差异常扩大是必要条件，叠加卖压是充分条件

**§2.5.5 "价差 > 正常 5x" 与代码 "0.5% 绝对" 的对齐**：
- §2.5.5 的"5x 正常"是**方向性 spec**（价差异常扩大到正常水平的数倍），需要维护"正常基准"（N 日均价差）
- 代码用**绝对阈值 0.5%**（简单稳健，无需维护基准）——A 股流动性正常的票 spread 通常 0.01-0.05%（1-5 个 tick），0.5% 已是 10-50 倍正常水平，与"5x"量级吻合
- MVP 用绝对阈值（简单），Phase 1.5 可上推相对阈值（spread / N 日均价差 > 5x）若绝对阈值误报多

#### 3.1.1 sell_pressure 形式化定义（v1.0.3 补全）

> **v1.0.3 新增**：§3.1 描述了 `sell_pressure >= 0.65` 阈值但未形式化 sell_pressure 的计算公式——上游数据层需知道如何产出此参数。本节补齐。

**定义**：sell_pressure 衡量盘口卖方主导程度，范围 [0, 1]，1 = 纯卖压。

**推荐算法——OBI 反转**（Order Book Imbalance，[Polymarket 2026-06](https://polymarket.com) 流动性监控引擎）：

```python
def sell_pressure(bid_volumes: list[float], ask_volumes: list[float]) -> float:
    """卖盘压力 = 1 - OBI（Order Book Imbalance）
    
    OBI = (ΣVolBid - ΣVolAsk) / (ΣVolBid + ΣVolAsk)
    sell_pressure = 1 - OBI = 2 × ΣVolAsk / (ΣVolBid + ΣVolAsk)
    
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
    return total_ask / total  # = 1 - OBI
```

**为何用 OBI 反转而非成交量比率**：
- OBI 基于盘口挂单（限价单队列），是**瞬时**流动性画像——反映"此刻谁在排队"
- 成交量比率（如卖成交量/总成交量）是**滞后**指标——成交已经发生，来不及预警
- A 股 miniQMT `xtdata.get_full_tick` 提供 5 档买卖盘挂单量，可直接计算
- 0.65 阈值 = OBI 0.35（买盘仅占 35%），与 Polymarket `<0.40 卖压主导`阈值量级一致

**替代算法——OFI 一阶差分**（[ClusterLOB 2026-06](https://clusterlob.com)）：
- OFI（Order Flow Imbalance）= 限价单队列变化的一阶差分，反映**动态**压力变化方向
- `OFI_t = Δ(Q_bid_t) - Δ(Q_ask_t)`，正=买方加单/卖方撤单（买压升），负=卖压升
- OFI 是 sell_pressure 的**补充**而非替代：sell_pressure 衡量静态存量，OFI 衡量动态变化趋势
- **Phase 1.5 储备**：sell_pressure（静态）+ OFI（动态）双维度——静态超阈值触发 + 动态急剧恶化提前预警

#### 3.1.2 spread 形式化定义（v1.0.3 补全）

**定义**：bid_ask_spread 衡量盘口即时交易成本，与 0.5% 阈值量纲一致。

**推荐算法——Quoted Spread**（最基础、与代码阈值同量纲）：

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

**为何用 Quoted Spread 而非 Effective Spread**：
- Quoted Spread = (ask-bid)/mid，直接从盘口读取，**零延迟**，适合盘内实时检测
- Effective Spread = 2×|成交价-mid|/mid，需等成交后才能计算，**滞后**于盘口变化
- 流动性危机检测需要**领先**信号——盘口 spread 扩大先于成交价恶化
- A 股 miniQMT `get_full_tick` 直接提供买一/卖一价，无需额外计算

**涨跌停特殊处理**（与 §3.5 对齐）：
- 跌停板：`ask_price` 存在（跌停价卖单），`bid_price` 可能缺失（无买单）→ spread 置 **1.0**（大值，使 AND 条件可满足）
- 涨停板：`bid_price` 存在（涨停价买单），`ask_price` 可能缺失（无卖单）→ spread 置 **None**（跳过检查，涨停不触发流动性危机）
- 停牌：两者均缺失 → spread 置 None（跳过检查）

### 3.2 决策②：日频结构性流动性监控——复用 MOD-RK-08 LiquidityMonitor

**决策**：复用已实现的 [LiquidityMonitor](file:///d:/ZephyrAlpha/src/zephyr/risk/core/liquidity_monitor.py)（MOD-RK-08，production）的 Amihud 非流动性指标 + 成交量萎缩比率，作为日频结构性流动性恶化监控。

**已实现能力**（代码已实现）：
- `compute_amihud(closes, volumes)`：Amihud ILLIQ = |r_d| / V_d 的 N 日均值（r_d=日收益率，V_d=日成交额）。ILLIQ 越高越不流动
- `compute_volume_shrinkage(volumes)`：V_ratio = V_t / MA(V, N)，<1=萎缩，<0.5 判定萎缩
- `assess(symbol, ohlcv, bid_ask_spread)`：综合判定 is_illiquid = Amihud 超阈值(1e-8) OR 成交量萎缩(<0.5)
- `bid_ask_spread` 为**可选外部输入**（MOD-RK-08 不自行计算，由上游提供）
- 纯机制零参数：阈值/窗口为 C 类参数（有行业默认值），可在构造时覆盖

**与 MOD-RK-10 的互补关系**（代码注释已明确）：
- MOD-RK-10 LIQUIDITY_CRISIS：盘内紧急（卖压 + 价差扩大）→ 紧急性流动性危机
- MOD-RK-08 LiquidityMonitor：日频趋势（Amihud + 成交量萎缩）→ 结构性流动性恶化
- 两者时间尺度互补：盘内秒级 vs 日频，不重叠不冲突

**为何需要日频层**：盘内检测只能抓"正在发生的危机"，日频监控能提前发现"流动性正在恶化"的趋势，给策略层调整持仓的时间窗口（如逐步减仓流动性变差的票，而非等危机爆发才被动停开仓）。

### 3.2a IPO 流动性抽离预警（v1.0.15 新增——前瞻性流动性监控）

> **缺口背景**：final_report_0724 实证 2026-07-27 长鑫科技（688825）科创板上市（募资 579-666 亿），可能吸金 500 亿+。此类**事件型流动性抽离**无法被 Amihud/spread/sell_pressure 事后检测捕获——等 spread 扩大时 IPO 已经吸完。需要**前瞻性**流动性预警（上市日前已知 IPO 日历+募资规模），提前调整仓位上限。

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

**与 [26_event_driven §2.5a](26_event_driven_strategy_detail.md) 的联动**：26 号负责"alpha 方向+仓位策略"（IPO 上市前完成主仓位布局+保留现金+上市后存量板块降仓），37 号负责"流动性检测+仓位上限节流"（drain_level→position_cap_adjustment）。两者互补：26 号是事件驱动 sleeve 的主动策略，37 号是 firm 层的被动仓位上限。

**与 §3.2 Amihud/成交量萎缩的区别**：§3.2 的 Amihud/成交量萎缩是**事后**检测（流动性已经恶化），§3.2a 是**事前**预警（IPO 上市日前已知募资规模→提前计算 drain_ratio）。两者时间轴正交：§3.2a 在 IPO 上市前 N 日启动预警，§3.2 在 IPO 上市后检测实际流动性恶化（若有）。

**数据源**：IPO 上市日历/募资规模来自 `akshare_provider`（`stock_ipo_info` 接口，production）。科创板/创业板前 5 日无涨跌幅限制是规则硬编码。

### 3.3 决策③：流动性危机响应——停开仓仅平仓（对齐 §2.5.5 + LEVEL_1）

**决策**：流动性危机触发后，响应动作 = **立即停止开仓，仅允许平仓**，对齐 §2.5.5 spec 与 MOD-RK-10 LEVEL_1 警报。

**响应动作映射**（MOD-RK-10 三级警报）：

| 警报级别 | 触发条件 | position_cap | 响应动作 | 与 §2.5.5 对齐 |
|---|---|---|---|---|
| LEVEL_1 | 1 信号（含 LIQUIDITY_CRISIS 单独触发） | 1.0（现有仓位不动）+ 新开仓 0% | **停开仓仅平仓** | ✅ 对齐"流动性危机→停止开仓仅允许平仓" |
| LEVEL_2 | 2 信号 | 70%（降仓 30%） | 减仓 30% | 比 §2.5.5 更严（叠加多信号时升级） |
| LEVEL_3 | ≥3 信号 或 情绪断路器 | 0%（清仓） | 清仓 + 撤单 + 暂停 + Kill Switch | 对齐 Kill Switch"宁可错杀"原则 |

> **注**：LEVEL_1 的 `position_cap=1.0`（代码字段值），"新开仓 0%"是独立的动作位（`halt_new_orders` 语义），不改变 position_cap。即：现有仓位不受强制减仓，但禁止新建仓。

**为何 LEVEL_1 是"停开仓"而非"清仓"**：
- §2.5.5 明确："流动性危机→立即停止开仓，仅允许平仓"——是停开仓不是清仓
- 流动性危机时市场已经流动性差，强行清仓会踩踏（卖在最低点），反而扩大损失
- 停开仓 + 允许平仓 = 不加新仓（避免在流动性差时建仓），但允许策略主动减仓（平仓是策略决策，不是强制清仓）
- 只有当 ≥3 信号同时触发（系统性崩盘）才升级到清仓（LEVEL_3），此时"跑得快"比"卖得好"重要

**为何不强制平仓**：LEVEL_1 的"仅允许平仓"是**允许**平仓（不阻止），不是**强制**平仓。是否平仓由策略层决策（策略可能判断持仓票基本面没变，等流动性恢复）。强制平仓会剥夺策略的决策权，且在流动性危机时强制卖出必然踩踏。

**逃生执行器（LEVEL_3 专属，已实现）**：

LEVEL_3 警报触发时，`AshareSystemicRiskDetector.build_escape_directive(alert)` 产出逃生指令字典，供 RK-17 Kill Switch 执行：

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

- **守卫**：非 LEVEL_3 调用 `build_escape_directive` 抛 `InvalidSystemicRiskInputError`（逃生指令仅 LEVEL_3 可产出）
- **消费者**：RK-17 Kill Switch（MOD-RK-17）接收逃生指令 → 执行清仓 + 撤单 + 暂停 + 冷却 30 分钟
- **数据流**：`check()` → `SystemicRiskAlert(LEVEL_3)` → `build_escape_directive(alert)` → RK-17 执行

### 3.4 决策④：与 Kill Switch 的关系——流动性危机不直接触发 Kill Switch

**决策**：流动性危机（LIQUIDITY_CRISIS 信号）**单独触发时为 LEVEL_1（停开仓），不联动 Kill Switch**；只有 ≥3 信号同时触发（LEVEL_3）才联动 Kill Switch 清仓。

**Kill Switch 触发条件**（battle_map_09 BM-RC-03，production）：
- 回撤超 Emergency 阈值
- VaR 超限且无法减仓
- Owner 手动

> **注意**：BM-RC-03 的 Kill Switch 触发条件中**不直接包含"流动性危机"**——流动性危机通过 MOD-RK-10 的 LEVEL_3（≥3 信号）间接联动 Kill Switch，而非直接触发。这与 §2.5.5 把"流动性危机"列为 Kill Switch 触发条件之一的表述有细微差异。

**差异对齐**：
- §2.5.5 把流动性危机列为 Kill Switch 4 触发条件之一（单日亏损>6% / 回撤>25% / 连续5天亏损 / 流动性危机）
- 代码实现：流动性危机单独 = LEVEL_1 停开仓（不 Kill Switch）；流动性危机 + 其他 ≥2 信号 = LEVEL_3 清仓 + Kill Switch
- **对齐结论**：代码比 §2.5.5 更精细——§2.5.5 的"流动性危机→停开仓仅平仓"对应 LEVEL_1，§2.5.5 的 Kill Switch"宁可错杀"原则对应 LEVEL_3。流动性危机单独时不该清仓（踩踏风险），只有叠加多信号才升级。这是对 §2.5.5 的合理细化，不违反 spec 精神。
- **G16 已对齐**：[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16）已于 2026-08-10 升级为 active v1.0.0，§3.5"Kill Switch 触发与执行路径"已填写完整。其多源触发表中"流动性危机"行明确写"买卖价差 > 正常 5x → G18 流动性危机 Protocol（[37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)）"，与本备忘决策④双向引用已建立。G16 确认流动性危机通过 MOD-RK-10 LEVEL_3（≥3 信号）间接联动 Kill Switch，与本备忘决策④一致。

**为何流动性危机不直接 Kill Switch**：
- Kill Switch = 清仓 + 暂停 + 冷却 30 分钟（BM-RC-03-B），是核按钮
- 流动性危机单独发生时（如某票突发利空 spread 扩大），清仓会踩踏，停开仓已足够保护
- Kill Switch 留给"系统性崩盘"（≥3 信号），此时不清仓会亏更多
- 分级响应比一刀切清仓更合理——这是对 §2.5.5 的工程细化

### 3.5 决策⑤：A 股涨跌停流动性失效处理

**决策**：A 股涨跌停时 spread 监控**失效**（盘口退化为单价位），涨跌停本身即流动性危机子类，由执行层 [40_execution_broker](40_execution_broker.md) 决策⑥⑭处理，不在 G18 重复定义。

**涨跌停流动性失效机制**：

| 场景 | 盘口状态 | spread 监控 | 流动性含义 |
|---|---|---|---|
| 涨停板 | 只有涨停价一个买价位，卖单稀缺/消失 | 失效（无卖一价，spread=∞ 或未定义） | 买不进（排队），可卖（有人挂涨停买） |
| 跌停板 | 只有跌停价一个卖价位，买单稀缺/消失 | 失效（无买一价，spread=∞ 或未定义） | 卖不出（排队），可买（有人挂跌停卖） |
| 接近涨停 | 买一/卖一价差正常但买一堆积巨量 | 正常但失真（spread 小但不代表流动性好） | 即将买不进 |
| 接近跌停 | 买一/卖一价差正常但卖一堆积巨量 | 正常但失真 | 即将卖不出 |

**与执行层的协同**（40_execution_broker 已覆盖）：
- 决策⑥拒单分类：涨停(50)/跌停(51)拒单不重试直接放弃（涨跌停板排不上，重试无意义）
- 决策⑭挂单价：涨停板卖单挂涨停价（唯一可成交价位）、跌停板买单挂跌停价
- 决策⑮临时停牌：跨日停牌核查移除目标 + 释放资金预占

**G18 的补充约束**（执行层未覆盖的）：
- **涨跌停时 MOD-RK-10 的 bid_ask_spread 输入处理**：跌停时（卖压≈1.0）应将 `bid_ask_spread` 置为**大值（如 1.0=100%）**而非 None——这样双条件 AND（`sell_pressure >= 0.65` AND `spread >= 0.005`）可满足，LIQUIDITY_CRISIS 信号正常触发。**若置为 None 则代码跳过检查（`if sell_pressure is not None and bid_ask_spread is not None`），信号无法触发**——这是 v1.0.2 修复的算法断裂。涨停时（买压主导）不触发流动性危机（卖压低），spread 置 None 即可（跳过检查）。
- **持仓票跌停 = 流动性危机子类**：跌停时卖不出，等同于"平仓通道冻结"。MOD-RK-10 的 LIQUIDITY_CRISIS 信号在跌停时触发（卖压≈1.0 + spread=1.0 满足双条件 AND），联动 LEVEL_1 停开仓——此时停开仓是对的（跌停时开仓=接飞刀）
- **涨跌停监控数据源**：miniQMT `xtdata.get_full_tick` 可取实时盘口（买一/卖一/涨停价/跌停价），用于判定涨跌停状态

#### 3.5.1 涨跌停状态检测算法（v1.0.3 补全）

> **v1.0.3 新增**：§3.5 描述了涨跌停时 spread 应如何取值，但未形式化涨跌停**判定算法**——上游需知道如何判定当前是否处于涨跌停状态。本节补齐。

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

**涨跌停价获取**：miniQMT `xtdata.get_full_tick` 返回的 tick 数据含 `limit_up` / `limit_down` 字段（交易所每日计算 = 前收盘价 × (1±涨跌幅限制)），ST/*ST 股 ±5%、主板 ±10%、创业板/科创板 ±20%、北交所 ±30%。

**与 §3.1.1/§3.1.2 的联动**：

| 涨跌停状态 | sell_pressure | bid_ask_spread | LIQUIDITY_CRISIS 触发？ |
|---|---|---|---|
| limit_up（涨停） | 低（买压主导） | None（跳过检查） | ❌ 不触发（涨停≠流动性危机，是买盘过剩） |
| limit_down（跌停） | ≈1.0（纯卖压） | 1.0（大值，使 AND 可满足） | ✅ 触发（跌停=平仓通道冻结=流动性危机子类） |
| near_up（接近涨停） | 正常 | 正常 | 按正常逻辑判定 |
| near_down（接近跌停） | 偏高 | 偏大 | 可能触发（视实际 sell_pressure/spread 值） |

### 3.6 决策⑥：危机恢复算法——滞后-恢复双阈值（Hysteresis）

> **v1.0.3 新增**：§3.1-§3.5 只定义"如何进入" LEVEL_1/2/3，**未定义"如何退出"**。实盘一旦触发 LEVEL_1 停开仓，若无恢复算法，系统会一直停开仓——错过所有后续建仓机会。本节补齐恢复算法。

**核心原则**：触发阈值与恢复阈值**不对称**（hysteresis 双阈值），避免在临界状态反复震荡（触发→恢复→再触发→再恢复的 thrashing）。

**恢复条件矩阵**（对称于 §3.3 触发条件，但阈值更宽松）：

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
    
    v1.0.11 修：签名与 §3.6 编排伪代码 intraday_liquidity_loop 调用点对齐。
    原定义用硬编码阈值（spread<0.0025 / pressure<0.50）+ positional 参数
    (current_state, signals, spread, sell_pressure, time_since_trigger)，
    与调用点的显式阈值参数（trigger_threshold_*/recovery_threshold_*/min_hold_minutes/elapsed）
    完全不匹配。统一为参数化签名——阈值/最短持续时间作为参数注入，
    支持实盘校准时外部调整（对齐 §6 "待校准"要求），且消除"两处真相源"。
    
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

**恢复执行动作**：

| 恢复路径 | 执行动作 |
|---|---|
| LEVEL_1 → 正常 | `halt_new_orders=False`（恢复开仓权限）；position_cap 保持 1.0；通知日志"流动性危机解除，恢复开仓" |
| LEVEL_2 → LEVEL_1 | position_cap 从 0.70 → 1.00；`halt_new_orders=False`；通知日志"多信号降级，恢复满仓权限" |
| LEVEL_3 → LEVEL_2 | Kill Switch 冷却期满后，position_cap 从 0.00 → 0.70；`halt_new_orders=False`（允许重建仓至 70%）；通知日志"系统性危机降级，允许重建仓 70%" |

**为何用半阈值（hysteresis）而非原阈值**：
- 若恢复阈值 = 触发阈值（spread 0.5%），则在 spread 于 0.49%-0.51% 间波动时会反复触发/恢复（thrashing），系统在"开仓-停开仓"间震荡
- 半阈值（0.25%）制造了一个"恢复缓冲带"——spread 须从 0.5% 降到 0.25% 才恢复，从 0.25% 升到 0.5% 才再触发，中间 0.25% 的区间是稳定区
- 这是控制论中 hysteresis（迟滞回线）的标准应用，恒温器/施密特触发器同原理

**为何需要最短持续时间门控**：
- 流动性危机的恢复不是瞬时的——spread 短暂回到 0.25% 以下不代表危机已过（可能只是盘中波动间隙）
- N=5 分钟的持续时间窗口确保恢复条件**持续满足**而非瞬时满足
- LEVEL_1 最短 10 分钟、LEVEL_2 最短 15 分钟是对 A 股日内波动节奏的经验估计（MVP 先定，实盘校准）

**与 MOD-RK-10 的集成**：
- 恢复判定由 `AshareSystemicRiskDetector.check()` 在每次 `detect()` 调用时顺带执行——检测信号触发 + 检测恢复条件，输出 `SystemicRiskAlert(level=current_state)` 或 `SystemicRiskAlert(level=0, recovered_from=prev_state)`
- 恢复动作（`halt_new_orders=False` / `position_cap` 调整）由 FirmRiskAggregator 在消费 alert 时执行，与触发动作的消费者一致

> **待校准**（§6 新增）：恢复阈值（spread 半阈值 0.25% / sell_pressure 0.50）和最短持续时间（10/15/30 分钟）是经验初始值，需实盘观测触发-恢复频率校准。重评条件：实盘累积 3 个月恢复事件数据后评估 thrashing 率（恢复后 N 分钟内再次触发的比例）。

### 3.7 决策⑦：2026 前沿算法评估——Hawkes / VPIN 重评 / Crumbling Labeler

> **v1.0.3 新增**：用户要求审查"选项之外更好的算法"。本节评估 3 项 2026 前沿微结构算法对 G18 流动性危机检测的增益，判定采纳/储备/拒绝。

#### 3.7.1 Hawkes 自激励过程——储备（Phase 1.5 候选）

**算法**：Hawkes 过程建模流动性事件的**聚集性**——一次大单冲击后，后续冲击概率短期升高（自激励），λ(t) = μ + Σ α·exp(-β(t-t_i))（[stockalpha.ai 2026-02](https://stockalpha.ai)；[arxiv 2310.09273](https://arxiv.org/abs/2310.09273)）。

```python
def hawkes_intensity(t: float, events: list[float], mu: float, 
                     alpha: float, beta: float) -> float:
    """Hawkes 自激励强度
    
    Args:
        t: 当前时间
        events: 历史事件时间戳列表 [t_1, t_2, ..., t_n]
        mu: 基线强度（外生事件到达率）
        alpha: 激励幅度（每次事件触发的强度增量）
        beta: 衰减率（激励随时间指数衰减）
    Returns:
        lambda(t): 当前时刻的事件到达强度
    """
    intensity = mu
    for t_i in events:
        if t_i < t:
            intensity += alpha * np.exp(-beta * (t - t_i))
    return intensity
```

**对 G18 的增益**：
- MOD-RK-10 的 LIQUIDITY_CRISIS 是**阈值触发**（卖压 + spread 超阈值），无聚集性建模——无法区分"孤立事件"与"聚集事件"
- Hawkes 强度持续升高 = 事件正在**聚集** → 比单次阈值触发更早预警"危机正在酝酿"
- 典型场景：融资盘平仓潮——第一笔大单抛售触发小幅 spread 扩大（未超阈值），但 Hawkes 强度已因自激励升高 → 提前预警后续平仓潮

**判定：储备（Phase 1.5 候选）**，非 MVP 采纳：
- 增益明确但需 tick 级事件流（大单成交/撤单事件序列），数据管道成本中等
- 参数 μ/α/β 需用历史危机事件拟合（A 股 2015 股灾/2024 小盘股流动性危机等），校准成本高
- MVP 的 sell_pressure + spread 双条件已能捕获"正在发生的危机"，Hawkes 的价值是"提前 1-3 分钟预警"
- **重评条件**：MOD-RK-10 实盘运行 3 个月后，若发现阈值触发滞后（危机已爆发才触发），上推 Hawkes 作为前置预警层

**⚠️ 2026-08 最新研究更新（v1.0.8 补，十三次审查）**——3 项新证据强化 Hawkes 储备地位：

1. **A 股直接实证**（[arXiv:2512.08000](https://arxiv.org/abs/2512.08000), Yang 2025/2026）：对上证综指、深证成指、创业板指及 CSI 消费/医药/金融行业指数拟合自激+抑制型 Hawkes 过程，发现**高交易活跃期行业指数延续趋势，低活跃期出现强行业轮动**——Hawkes 可同时解释 A 股"行业轮动"和"踩踏传染"双重现象
2. **图熵领先 7-12 天预警**（[An & Dai 2026, Entropy 28(8):887](https://www.mdpi.com/1099-4300/28/8/887)，2026-08-06 发表）：用 bias-corrected kNN 估计 transfer entropy + 多元 Hawkes 建模极端损失事件相互激发，**Von Neumann 图熵在回撤峰值前 7-12 个交易日达到历史极端值**——这是从"分钟级 tick 预警"升级到"日级提前预警"的关键发现。Hawkes 激发分量在 COVID-19 和 2022 欧洲能源危机期间使传染强度比基线高 35%-58%
3. **2026-07 A 股量化危机验证**（edgen 2026-07-21）：CSI300 -5.81%，科创50 -17.46%，动量/小盘/反转因子同时失效，量化产品 NAV 回撤超 10%，两周蒸发 10 万亿市值——Hawkes 自激过程描述的"止损→价格下跌→更多止损"级联在中小盘无量跌停中精确体现

**升级评估**：原判定"Phase 1.5 候选，提前 1-3 分钟预警"须修正——图熵领先 7-12 天的发现将 Hawkes 价值从"分钟级盘中预警"扩展到"日级提前预警"，**可能上调到 Phase 1 候选**。但图熵计算需跨资产/跨板块事件网络（非单资产 Hawkes），数据管道成本从"中等"升级到"高"。**维持储备判定**，但重评条件从"3 个月阈值滞后"扩展到"若需日级提前预警而非分钟级"。远期实施时优先用 `tick` 库（Python，Marcel Gauthche 2026-05 提供完整实现：order-flow toxicity 3σ 阈值 + 清算级联预警 + 财报成交量爆发检测）。

#### 3.7.2 VPIN 重评——维持拒绝（2026 证据不改变结论）

**§4.6 原拒绝理由回顾**：VPIN 需 tick 级时间桶成交量分类，个人小资金不做市不受 toxic flow 直接伤害，MOD-RK-10 卖压+spread 已等价覆盖。

**2026 新证据**：
- [theplugg 2026-07](https://theplugg.com)：VPIN 与 OBI、Depth-to-Volatility Decay 并列为闪崩三大早期预警指标——但该文同时指出 VPIN 的核心价值是**做市商视角**（toxic flow 吃掉做市商库存）
- [ClusterLOB 2026-06](https://clusterlob.com)：VPIN 在 A 股的实证显示，与简单 OBI 的相关性达 0.85+——VPIN 的额外信息量有限
- 个人系统不做市 → VPIN 的核心价值（保护做市商库存）不适用

**重评结论：维持拒绝**：
- VPIN 与 OBI/sell_pressure 相关性 0.85+（ClusterLOB 2026-06 实证）→ 信息冗余
- VPIN 的 toxic flow 检测价值 = 保护做市商，个人系统不做市 → 价值不适用
- MOD-RK-10 的 sell_pressure（OBI 反转）+ spread 已覆盖 VPIN 试图检测的同一类信号
- **重评条件不变**：策略扩展到做市/提供流动性场景时

#### 3.7.3 Crumbling Labeler——储备（Phase 2 远期候选）

**算法**：[ICLR 2026](https://iclr.cc) Crumbling Labeler——神经网络分类器区分"机械性流动性撤退"（做市商批量撤单，价格会恢复）与"信息驱动重定价"（基本面变化，价格不会恢复），用于决定是否清仓（[theplugg 2026-07](https://theplugg.com) 引用）。

**对 G18 的增益**：
- 当前 LEVEL_3 清仓是**一刀切**——不区分"机械撤退"（价格会恢复，不该清仓）与"信息重定价"（价格不会恢复，该清仓）
- Crumbling Labeler 能区分两者 → 更精细的清仓决策：机械撤退→维持持仓等恢复，信息重定价→清仓
- 这是对 §3.3 "LEVEL_3 清仓"决策的潜在增强——从"≥3 信号一刀切清仓"进化到"≥3 信号 + Crumbling Labeler 判定信息重定价才清仓"

**判定：储备（Phase 2 远期候选）**，非近期采纳：
- 需训练神经网络分类器（标注数据成本高——需人工标注历史危机事件的"机械 vs 信息"标签）
- ICLR 2026 论文尚处学术阶段，无开源实现/工业部署案例
- MVP 的"≥3 信号清仓"是**保守安全**的——即使误清仓（机械撤退被当信息重定价），代价是错过恢复后的反弹，而非本金亏损
- **重评条件**：① 论文有开源实现 ② AUM 增长到清仓成本显著（错过恢复的代价 > 训练 Crumbling Labeler 的成本）

#### 3.7.4 Slippage-at-Risk (SaR) 框架——储备（Phase 2 候选，选项之外更好的答案算法）

> **v1.0.6 新增**：用户要求审查"选项之外更好的答案算法"。SaR 是 2026-03 才发表的**前瞻性**流动性风险框架，与 MOD-RK-10 当前基于"已发生价差+卖压"的**回溯性**检测形成维度互补——本节评估其增益与移植成本。

**算法**：[arXiv:2603.09164](https://arxiv.org/abs/2603.09164) Sepper 2026-03 SepperLabs 提出 Slippage-at-Risk (SaR)，从**当前盘口微结构**推导**前瞻性**清算执行风险，区别于 VaR 等基于历史收益的回溯性指标。框架含三个互补度量：

```
SaR(α)   = inf{s : P(slippage > s) ≤ 1-α}    # 横截面滑点分位数（α 置信下最坏滑点）
ESaR(α)  = E[slippage | slippage > SaR(α)]    # 尾部期望滑点（类 ES 的尾部均值）
TSaR(α)  = Q × ESaR(α) × notional            # 美元计总尾部滑点（组合层级）
```

**集中度调整**（Concentration Haircut）——本框架关键创新，惩罚"少数做市商主导报价"的脆弱结构：

```python
def concentration_adjusted_sar(sar_base: float, hhi: float, eta: float = 1.5) -> float:
    """集中度调整后的 SaR——惩罚做市商集中度高的脆弱盘口。
    
    Args:
        sar_base: 基础 SaR(α)（未调整）
        hhi: Herfindahl-Hirschman Index，盘口各做市商深度份额平方和 ∈(0,1]
              hhi→1 = 单一做市商垄断（极脆弱）
              hhi→0 = 高度分散（健康）
        eta: 集中度弹性系数（Sepper 2026 实证 η≈1.5）
    Returns:
        concentration-adjusted SaR（≥ sar_base，单调递增于 hhi）
    """
    # 集中度 haircut 因子：单一做市商垄断时做市商撤离会导致盘口瞬间蒸发
    haircut_factor = 1 + (hhi ** eta)  # hhi=1 → 因子=2（SaR 翻倍）；hhi=0.1 → 因子≈1.03
    return sar_base * haircut_factor
```

**对 G18 的增益**——与现有 sell_pressure + spread 双条件 AND 检测的维度互补：

| 维度 | 现有（MOD-RK-10 双条件 AND） | SaR 框架 |
|---|---|---|
| **时间方向** | 回溯性（价差已扩大+卖压已出现才触发） | **前瞻性**（从当前盘口微结构预测未来清算滑点） |
| **输入** | sell_pressure（OBI）+ bid_ask_spread | 完整盘口多档深度 + 做市商集中度 |
| **输出** | 布尔触发（危机/非危机） | 连续滑点分布分位数（风险量化） |
| **做市商结构** | 不感知（只看总量） | **感知**（HHI 调整，识别"单一做市商撤离即崩溃"的脆弱结构） |
| **组合层级** | 单标的判定 | TSaR 聚合到组合美元滑点 |

**典型场景**：盘口 5 档深度看似充足（spread 正常、sell_pressure 正常），但深度高度集中于 1-2 个做市商——现有检测不触发（spread/sell_pressure 正常），但 SaR 的集中度调整会给出高 SaR 值（HHI→1 → haircut 因子→2 → SaR 翻倍），**提前预警"盘口深度是脆弱的纸糊结构"**。随后该做市商撤离 → 盘口瞬间蒸发 → spread 暴扩（此时 MOD-RK-10 才触发，已晚 1-3 分钟）。

**移植评估——A 股适配性**：
- ✅ **数据可得**：miniQMT `xtdata.get_full_tick` 提供 5 档买卖盘挂单量，可计算 HHI（需按做市商聚合，A 股无做市商席位标识——需用"挂单量集中度"近似，如前 3 大挂单 / 总挂单）
- ⚠️ **做市商结构差异**：原论文针对永续期货交易所（少数做市商主导报价），A 股个股无指定做市商（科创板做市商制度 2023 才引入，覆盖有限）——HHI 需重新定义为"挂单量集中度"而非"做市商份额集中度"
- ⚠️ **清算机制差异**：原论文针对永续合约清算级联（强平→ cascading liquidation），A 股无杠杆清算级联——但融资融券平仓潮机制类似（融资盘跌破维持担保比例→强制平仓→ cascading）
- ✅ **核心价值保留**：前瞻性滑点预测 + 集中度调整两项核心增益与 A 股场景适配，不依赖永续合约特有机制

**判定：储备（Phase 2 候选）**，非 MVP 采纳：
- 增益明确（前瞻性 + 集中度感知），但需重定义 HHI 为"挂单量集中度"并校准 η 参数
- MVP 的 sell_pressure + spread 双条件已能捕获"正在发生的危机"（回溯性），SaR 的价值是"提前预警脆弱结构"（前瞻性）
- 与 Hawkes（聚集性预警）正交互补：Hawkes 预警"事件聚集"，SaR 预警"结构脆弱"——两者可叠加为 Phase 2 的双层前瞻预警
- **重评条件**：① MOD-RK-10 实盘运行 6 个月积累足够盘口数据校准 HHI 阈值 ② AUM 增长到自身交易开始影响盘口（需 SaR 评估自身清算滑点）

**实证支撑——强制平仓级联两类型分类**（[arXiv:2608.03616](https://arxiv.org/abs/2608.03616), 2026-08）：对 7 起加密货币强平级联（2022-2025）的群组分析揭示：
- **级联起始是突变而非渐进**——order parameter 在起始瞬间跳变 1.6-4.4 个基线标准差，susceptibility proxy 在 7 起中 5 起崩溃但**无发散**（与经典临界相变预期相反）
- **两类型分类**：① **内生累积型**（拥挤→临界→崩塌，有 critical slowing down 前兆，Hawkes 可预警）vs ② **外生冲击型**（突发新闻/政策，无前兆，SaR 集中度调整可识别结构脆弱性但不能预测冲击本身）
- **88% 起始后强制卖出在 30 分钟内**，63% 被交易所 backstop 场外吸收，持仓量清除 25-70%

**对 G18 的启示**：两类型分类为"Hawkes + SaR 双层前瞻预警"提供理论框架——Hawkes 适配内生累积型（有前兆），SaR 适配两者（内生型脆弱结构是必要条件，外生型冲击需脆弱结构才级联化）。A 股融资盘平仓潮对应内生累积型（担保比例渐降→临界→强平级联），突发行情利空对应外生冲击型。MVP 双条件 AND 检测是对两种类型的统一回溯响应。

#### 3.7.5 Latent Microstructure Regime Detection（隐含微结构 regime 转变检测）——储备（Phase 2 候选，选项之外更好的算法）

> **v1.0.7 新增**：用户要求审查"选项之外更好的答案算法"+ 全网搜索 2026 最新研究。arXiv:2604.20949（Hiremath & Hiremath, 2026-04）提出**隐含 build-up regime** 概念——在可见压力（spread 扩大/sell_pressure 飙升）出现**之前**，存在一个隐含恶化阶段（latent build-up），可用专门的检测器实现**正 lead-time**（提前预警），而 OFI/spread/volatility 等标准信号**按构造是反应性的**（negative lead-time）。

**算法**：[arXiv:2604.20949](https://arxiv.org/abs/2604.20949)（Hiremath & Hiremath, 2026-04, Visvesvaraya Technological University）提出三 regime 因果数据生成过程（DGP）：**stable → latent build-up → stress**。核心洞察：标准早期预警信号（OFI、spread、volatility）是**按构造反应性的**——它们测量的是已发生压力的后果，而非前兆。一个在这些信号上校准的检测器，触发时间 τ ≥ σ（σ = 可见压力起始），零或负 lead-time 不是调参失败而是逻辑必然。论文证明 latent build-up regime 在时间漂移和 regime 持续性的温和条件下可识别，并推导两个保证：① 充分 drift-to-noise 条件保证严格正期望 lead-time（Proposition 1）；② 检测概率在 stress 起始前的下界为 SNR 和 build-up 持续时间的函数（Proposition 2）。

**触发检测器**（trigger-based detector）三组件：
1. **MAX 聚合**——uncertainty 和 drift 两个通道取 MAX（任一通道异常即触发）
2. **Rising-edge 条件**——信号须为上升沿（过滤已处于高位的噪声）
3. **自适应阈值**——根据近期信号分布动态调整触发阈值

**触发通道**：深度侵蚀（depth erosion）+ HMM 熵（HMM entropy）——两者占 >99% 首次触发事件，提供可解释的机制（与因果模型一致）。

**实证性能**：
- 仿真（200 runs）：mean lead-time +18.6±3.2 timesteps，precision 1.00±0.00，coverage 0.54±0.06
- 实数据（BTC/USDT 1Hz，1 周，5 标注事件）：mean lead-time +38±21 秒，precision 1.00，coverage 0.80
- **优于 CUSUM、BOCPD、HMM thresholding、imbalance/volatility baselines**（基线均为负 lead-time）

**与现有方法的关系**：
- **Hawkes（§3.7.1）**：时间维度——检测"事件正在聚集"（事件频率上升）。Latent build-up 检测：regime 转变维度——检测"order book 正从 stable 转向 stressed"（深度侵蚀+HMM 熵变化）
- **SaR（§3.7.4）**：结构维度——检测"盘口结构是脆弱的"（HHI 集中度）。Latent build-up 检测：动态维度——检测"盘口正在恶化"（深度侵蚀趋势）
- 三者正交：Hawkes（时间）× SaR（结构）× Latent build-up（regime 转变），可叠加为三层前瞻预警
- **与 35 号 §4.18 BOCD 的关系**：论文明确指出 latent build-up 检测器**优于 BOCPD**——BOCPD 检测变点（已发生），latent build-up 检测器检测 build-up（变点前兆）。但 BOCPD 在 35 号用于策略衰减 kill switch（日级），latent build-up 在 37 号用于盘中流动性（秒级），两者场景不同不冲突

**A 股适配评估**：
- **数据可得性**：论文用 1Hz order book 数据。A 股 miniQMT 提供 tick 级数据但非均匀采样——depth erosion 通道可用 5 档盘口快照近似（miniQMT 5 档实时），HMM 熵通道需拟合 HMM 到 order book 状态（与 [10 号](10_regime_detector_spec.md) regime 检测器同类计算，可行但增加计算负担）
- **适用场景**：① 融资盘平仓潮——担保比例渐降→临界→强平级联，build-up 阶段（担保比例渐降）对应 latent build-up regime，depth erosion 可提前预警；② 涨跌停前夕——价格接近涨跌停时深度递减，build-up 检测可在涨停前预警；③ 尾盘集中交易——14:50-15:00 深度变化加速，build-up 检测可预警尾盘流动性恶化
- **限制**：论文实数据验证仅 BTC/USDT（加密货币），A 股微结构差异大（无做市商制度、T+1、涨跌停），需独立验证

**为何 Phase 2 候选而非立即采纳**：
1. **数据粒度**：1Hz order book depth 在 A 股 miniQMT 下非实时均匀可得——tick 级但采样不固定，需重采样到固定频率
2. **计算复杂度**：HMM 熵计算 + MAX 聚合 + rising-edge + 自适应阈值是多组件检测器，盘中实时运行的工程成本高于双条件 AND
3. **验证不足**：论文实数据仅 5 个标注事件（BTC/USDT 1 周），A 股独立验证需积累实盘盘口数据
4. **MVP 已覆盖**：双条件 AND（sell_pressure + spread）已能捕获"正在发生的危机"，latent build-up 的增量价值是"提前 30-60 秒预警"——Phase 1.5 Hawkes 已覆盖"提前 1-3 分钟预警"，两者重叠

**重评条件**：① MOD-RK-10 实盘运行 6 个月积累足够盘口数据验证 depth erosion 通道有效性；② Hawkes（§3.7.1）上线后若发现仍存在 lead-time 不足（Hawkes 检测事件聚集但深度侵蚀更早）；③ miniQMT 提供均匀采样的 5 档盘口数据（支持 HMM 熵计算）

**五算法评估汇总**：

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

> **v1.0.10 新增**：标准 Hawkes（§3.7.1）假设所有状态转移皆可发生，但 A 股 LOB 存在物理约束——涨停时无卖单（卖方状态消失）、跌停时无买单（买方状态消失）。标准 Hawkes 在状态消失时产生爆炸分支比（branching ratio > 1）导致模拟不稳定。

**算法**：[Kimura 2026-04 arXiv:2604.23961](https://arxiv.org/abs/2604.23961)（Sophia University）Extended State-Dependent Hawkes Process（ExsdHawkes）：
- **核心创新**：放宽传统约束允许状态消失（state disappearance），用 KKT（Karush-Kuhn-Tucker）条件证明 MLE 可分离——转移概率与 Hawkes 参数可独立估计，即使某些转移被物理禁止
- **波动率签名图复现**：ExsdHawkes 唯一复现波动率签名图的向上斜率——通过捕获均衡失衡状态的"局部超临界"（local super-criticality）
- **MLO 催化识别**：Marketable Limit Orders（可成交限价单）被识别为迫使 LOB 进入不稳定状态的主要催化剂
- **物理一致性**：缺乏物理约束的模型（如标准 SD-Hawkes）产生爆炸分支比并无法维持模拟稳定——物理一致性不是数学修饰而是准确建模宏观波动率的先决条件

**与 §3.7.1 标准 Hawkes 的关系**：
- 标准 Hawkes：λ(t) = μ + Σ α·exp(-β(t-t_i))，所有事件可发生，无状态约束
- ExsdHawkes：在 LOB 状态空间上定义 Hawkes，状态消失时"暂停"残差累积，避免爆炸

**为何储备而非采纳**：
1. **复杂度高**：状态空间定义 + KKT 分离估计 + 指数核递归估计是多组件系统
2. **A 股适配性待验证**：Kimura 实证用 MUFG tick 数据（日本市场），A 股涨跌停板制度更严格（状态消失更频繁）需独立验证
3. **MVP Hawkes 足够**：§3.7.1 标准 Hawkes 储备已能预警事件聚集，ExsdHawkes 的增量价值是"避免爆炸分支比"——仅在标准 Hawkes 实盘运行出现不稳定时升级

**重评条件**：① §3.7.1 标准 Hawkes 上线后若发现涨跌停时分支比爆炸导致预警失效；② miniQMT Level-2 数据支持 LOB 状态空间建模；③ A 股涨跌停频繁的票种独立验证 ExsdHawkes 稳定性

#### 3.7.7 Liquidation Cascade 三因子框架——储备（Phase 2 候选，选项之外更好的算法）

> **v1.0.10 新增**：标准 Hawkes 假设级联中分支比上升（critical slowing down 预警），但 2026-08 最新加密市场实证推翻此假设——级联全程深度亚临界，预警信号在突发冲击中失效。

**算法**：[Garcia Seuma 2026-08 arXiv:2608.03616](https://arxiv.org/abs/2608.03616)（"Measuring the engine of a liquidation cascade: subcritical branching inside a first-order transition"）：
- **核心发现**：7 次重大加密永续合约强平级联（2022-2025）中，三种估计器（结构比/放大记账/INAR-Hawkes 流式估计）一致显示级联全程深度亚临界（λ≈0.1-0.2），流式估计在高潮时**下降**而非上升
- **推翻临界级联假设**：Galton-Watson 临界级联不适用作"级联前状态"描述，critical slowing down 预警信号在 abrupt shock 中失效
- **一阶相变框架**：提出一阶相变（first-order transition）替代临界相变（critical transition）框架
- **三因子严重度**：severity = 冲击 × 路径映射 × 流动性撤回（非发散乘子）
- **级联吸收**：88% 强平在 30 分钟内完成，63% 被场外兜底吸收

**对 §3.7.1 Hawkes 的修正**：
- 标准 Hawkes 用分支比上升作为预警信号 → Garcia Seuma 证明级联中分支比下降
- **修正建议**：Hawkes 预警应监测"三因子"（冲击幅度 + 路径映射 + 流动性撤回）而非单一分支比
- A 股迁移：无永续合约强平机制，但融资融券平仓线 + 股权质押爆仓形成类似级联——可监测两融余额变化率 + 平仓密度作为代理

**为何储备而非采纳**：
1. **加密市场实证**：A 股无永续合约强平机制，级联动力学不同
2. **三因子数据**：路径映射因子需定义（A 股可用行业关联度/担保圈网络）
3. **MVP Hawkes 足够**：§3.7.1 标准 Hawkes 储备已能预警事件聚集，三因子框架是"预警信号选择"的升级非替代

**重评条件**：① A 股融资盘平仓数据（两融余额/平仓密度）可得；② §3.7.1 Hawkes 上线后若发现分支比预警信号失效（级联中分支比下降而非上升）

#### 3.7.8 Multiplex Network Hawkes 系统性风险——储备（Phase 3 远期候选）

> **v1.0.10 新增**：标准 Hawkes 是单资产/单事件流的自激励模型，无法捕获跨机构/跨行业的传染通道。Multiplex Network Hawkes 将 Hawkes 扩展到多层网络，分离不同传染通道的贡献。

**算法**：[Zelvyte & Griffin 2026-06 arXiv:2606.15755](https://arxiv.org/abs/2606.15755)（University of Kent，"A Multiplex Network Hawkes Model for Systemic Risk Measurement"）：
- **核心创新**：扩展 Linderman & Adams (2014) 网络 Hawkes 框架，允许多个激励层，权重依赖于观测到的边和节点协变量
- **通道分离**：多层结构在单一推断传输网络内分离特定通道贡献——可直接比较候选传播机制（行业相似性/偿付能力/盈利能力）
- **MCMC 后验推断**：对推断有向网络及其激励动态进行后验推断，提供不确定性量化
- **实证发现**：99 家北美和欧洲公司 CDS 数据（2004-2022），稀疏传染路径，系统性风险传输集中在外向流（少数有影响力机构），而非机构间相互反馈

**与 §3.7.1 标准 Hawkes 的关系**：
- 标准 Hawkes：单资产/单事件流自激励，检测"事件聚集"
- Multiplex Network Hawkes：多机构/多通道网络传染，检测"谁传染谁"——是系统性风险测量的升级

**A 股迁移路径**：
- A 股 CDS 市场不发达，但可迁移到股权质押网络/担保圈/行业供应链关联
- 可用公开的关联担保/股权质押数据构建多层网络，识别系统性风险外向源
- 计算成本中等（MCMC），适合周度/月度重估

**为何远期储备**：
1. **数据依赖高**：需构建机构间关联网络（股权质押/担保/供应链），A 股公开数据有限
2. **计算成本**：MCMC 采样器计算成本中等，但需周度/月度重估
3. **MVP 优先级低**：个人小资金的流动性危机检测已由 MOD-RK-10 双条件 AND 覆盖，系统性传染是宏观级风险非个体级

**重评条件**：① A 股股权质押/担保圈网络数据可得且质量足够；② AUM 增长到需关注系统性传染时；③ 与 §3.7.6 ExsdHawkes 同步评估（ExsdHawkes 管单资产 LOB，Multiplex 管跨机构网络）

#### 3.7.7.1 Garcia Seuma 临界性预警异质性 —— 储备（Phase 2 候选，§3.7.7 Liquidation Cascade 配套）

> **v1.0.11 新增**：§3.7.7 Liquidation Cascade 三因子框架（Garcia Seuma 2026-08 arXiv:2608.03616 Part II）推翻"临界级联"假设，但其配套论文 Part I（[arXiv:2607.27070](https://arxiv.org/abs/2607.27070)，"Where does the criticality live? Early-warning signals are event-heterogeneous across seven crypto-perpetual liquidation cascades"，2026-07-29）系统测试了 7 次级联的 39 种分析配置，发现**没有任何变量是事件不变的**——critical slowing down 在 5/7 事件的价格序列中出现，但在 2 次突发新闻（关税）冲击中完全缺失。唯一在 300 onset placebo test 中存活的规律是**吃单订单流方差压缩**（taker order-flow variance compression，Fisher-combined p ≈ 5×10⁻⁶），但这是群体级前兆而非单事件警报。此配套发现对 §3.7.7 三因子框架的"冲击类型识别"提供关键约束。

**算法**（[Garcia Seuma 2026-07-29 arXiv:2607.27070](https://arxiv.org/abs/2607.27070)）：
- **核心发现**：7 次重大加密永续合约强平级联（2022-2025）的 39 种分析配置（每变量×每事件）系统测试：
  1. **无事件不变量**：滚动方差 + lag-1 自相关（critical slowing down 经典信号）在 5/7 事件的价格序列中出现，但在 2 次突发新闻（关税）冲击中**完全缺失**——临界性预警信号的事件异质性是结构性的，非噪声
  2. **唯一存活规律**：吃单订单流方差压缩（taker order-flow variance compression）——在 300 onset placebo test 中 Fisher-combined p ≈ 5×10⁻⁶ 显著，但这是**群体级前兆**（population-level precursor）而非**单事件警报**（per-event alarm），不能直接用于个体级实时预警
  3. **冲击类型识别约束**：突发新闻冲击（如关税公告）与内生流动性冲击（如杠杆平仓级联）的预警信号完全不同——前者无 critical slowing down，后者有

- **对 §3.7.7 三因子框架的约束**：
  | 冲击类型 | critical slowing down | taker flow variance compression | §3.7.7 三因子预警 |
  |---|---|---|---|
  | 内生杠杆级联（5/7 事件） | ✅ 出现 | ✅ 出现 | 三因子（冲击×路径×流动性撤回）有效 |
  | 突发新闻冲击（2/7 事件） | ❌ 缺失 | ✅ 出现 | 三因子需补充"新闻冲击"维度 |

  §3.7.7 三因子框架（severity = 冲击 × 路径 × 流动性撤回）在内生级联中有效，但突发新闻冲击时"路径映射"因子可能突变（新闻冲击无前置路径累积）——需区分冲击类型分别校准三因子权重。

- **A 股迁移路径**：
  - A 股无永续合约强平，但融资融券平仓线 + 股权质押爆仓 + 突发监管政策（如 2024 国九条）形成两类冲击
  - **内生杠杆级联**：两融余额快速下降 + 平仓密度上升 → §3.7.7 三因子框架适用
  - **突发政策冲击**：监管公告/重大新闻 → 三因子框架需降权"路径映射"因子（无前置累积），主要靠"冲击幅度 + 流动性撤回"双因子
  - **吃单订单流方差压缩**：A 股可用 miniQMT Level-2 主动买/主动卖单流量方差作为代理——但作为群体级前兆，需配合其他信号确认才能用于实时预警

- **为何储备而非采纳**：
  1. **群体级 vs 个体级**：taker flow variance compression 是群体级前兆（p ≈ 5×10⁻⁶ 是 300 事件聚合统计），单事件预测力弱——个体级实时预警需更高分辨率信号
  2. **加密市场实证**：A 股无永续合约强平机制，需独立验证吃单订单流方差压缩在 A 股的显著性
  3. **与 §3.7.7 同期评估**：本节是 §3.7.7 三因子框架的冲击类型识别约束，应与 §3.7.7 同期评估非独立模块

- **重评条件**：① §3.7.7 三因子框架上线后若发现突发新闻冲击时预警失效；② miniQMT Level-2 主动买卖单流量数据可得；③ 与 §3.7.7 同期 A 股实证验证

#### 3.7.9 Weng A 股羊群效应 Johnson S_U 变换 —— 储备（Phase 2 候选，A 股专属）

> **v1.0.11 新增**：§3.7.6-§3.7.8 的 Hawkes 系列算法均源自美股/加密市场实证，A 股专属的羊群效应建模缺乏。2026-07-29 最新研究（[Weng 2026-07-29 arXiv:2607.27063](https://arxiv.org/abs/2607.27063)，"Herding, Momentum, and Reversal in China's A-Share Market: An Agent-Based Network Model with Information Diffusion"）构建 A 股专属的 agent-based 网络模型，引入 **Johnson S_U 变换** 处理 CSAD/LSV 羊群效应度量的非正态性——这是 A 股专属的羊群效应检测算法，填补 §3.7.x 系列"A 股实证"空白。

**算法**（[Weng 2026-07-29 arXiv:2607.27063](https://arxiv.org/abs/2607.27063)）：
- **核心创新**：A 股专属 agent-based 网络模型 + Johnson S_U 变换羊群效应指标
  1. **异质高斯信念**：投资者在 von Neumann/Moore 晶格、Erdős-Rényi、Watts-Strogatz 网络上形成异质高斯信念，根据邻居行为修正行动概率——区分**信息调整**（informational adjustment）与**行为模仿**（behavioral imitation）
  2. **有限速度信息扩散**：独立的信息扩散过程以有限速度传播——使模型能区分"基本面信息驱动的合理跟随"与"无信息纯模仿的羊群效应"
  3. **Johnson S_U 变换**：对 CSAD（Cross-Sectional Absolute Deviation）/ LSV（Lakonishok-Shleifer-Vishny）羊群效应度量应用 Johnson S_U 变换——S_U 是 Johnson 变换族中处理**有界非正态分布**的无界变换，将 CSAD/LSV 的偏态厚尾分布转为近似正态，使滚动羊群指标具备统计可比较性
  4. **滚动尾端羊群指标**：用 Johnson S_U 变换后的 CSAD/LSV 计算滚动尾端羊群指标，识别信息延迟、局部社会强化、羊群衰减作为动量与反转的互补机制

- **实证发现**：
  - A 股动量与反转由三个互补机制驱动：信息延迟（information delay）+ 局部社会强化（local social reinforcement）+ 羊群衰减（herding decay）
  - Johnson S_U 变换使羊群指标在不同市场状态（牛/熊/震荡）下可比——原始 CSAD/LSV 在牛市偏高（成交量放大）、熊市偏低（成交量萎缩），S_U 变换消除此偏差

- **与 §3.7.1 标准 Hawkes 的关系**：
  | 维度 | §3.7.1 标准 Hawkes | Weng Johnson S_U 羊群指标（§3.7.9） |
  |---|---|---|
  | 信号类型 | 事件聚集（event clustering） | 截面分散度（cross-sectional dispersion） |
  | 数据需求 | tick 级事件流 | 日级 CSAD/LSV + 网络结构 |
  | 时间尺度 | 分钟级 | 日级/周级 |
  | A 股适配 | 通用（加密/美股实证为主） | **A 股专属**（直接 A 股实证） |
  | 互补性 | 检测"事件何时聚集" | 检测"羊群何时形成" |

  两者正交——Hawkes 检测事件聚集（时间维度），Weng 检测羊群形成（截面维度），组合可构建"时间×截面"双维度流动性危机预警。

- **与 32号 §2.10.6 华泰金工风格拥挤度的关系**：32号 §2.10.6 D-3 华泰金工风格拥挤度（动量+成交量双维度分域模型）是**风格级**羊群检测（哪个风格拥挤），Weng §3.7.9 是**市场级**羊群检测（整体羊群度）——两者递进：Weng 管市场整体羊群度，华泰管哪个风格拥挤，§3.7.1 Hawkes 管事件聚集。

- **为何储备而非采纳**：
  1. **网络结构假设**：Weng 模型假设投资者在特定网络拓扑（晶格/ER/WS）上互动，A 股真实社交网络结构难以观测——模型参数需校准
  2. **Johnson S_U 参数估计**：S_U 变换的参数（γ, δ, ξ, λ）需用 A 股历史 CSAD/LSV 数据拟合，MVP 阶段样本不足
  3. **与 HBI/CSAD 重叠**：§3.5 已有 HBI/CSAD 基础羊群指标，Weng 的增量价值是"Johnson S_U 变换消除牛/熊偏差"——需先验证 HBI/CSAD 在牛/熊市偏差显著才能引入

- **重评条件**：① §3.5 HBI/CSAD 上线后若发现牛/熊市偏差显著影响羊群信号；② A 股历史 CSAD/LSV 数据 ≥2 年用于 Johnson S_U 参数拟合；③ 与 §3.7.1 Hawkes 同期评估（时间×截面双维度预警）

#### 3.7.10 Zhou 平方根冲击操纵周期 —— 储备（Phase 3 远期，A 股专属）

> **v1.0.11 新增**：§3.7.6-§3.7.9 聚焦"检测流动性危机何时发生"，但未涉及"流动性危机的内生操纵机制"。2026-07-06 最新研究（[Zhou, Chen & Wei 2026-07-06 arXiv:2607.05141](https://arxiv.org/abs/2607.05141)，"Square-Root Price Impact Is Necessary for Endogenous Manipulation Cycles in Learning-Agent Markets"，Westlake University）构建 A 股专属的 agent-based 模型（含 ±10% 涨跌停板 + T+1 结算 + 隐形分配机制），证明**平方根价格冲击是内生操纵周期的必要条件**——线性冲击消除 Hopf 分岔使市场无条件稳定。此发现对 §3.7.x 系列的"危机机制理解"提供 A 股专属理论支撑。

**算法**（[Zhou, Chen & Wei 2026-07-06 arXiv:2607.05141](https://arxiv.org/abs/2607.05141)）：
- **核心创新**：A 股专属 agent-based 模型 + 平方根冲击的内生操纵周期理论
  1. **A 股专属机制**：单个进化优化机构 agent 对抗 20,000 个羊群散户 agent，实现 A 股三大机制——±10% 涨跌停板 + T+1 结算 + 隐形分配（stealth distribution，机构卖出时有效羊群减半）
  2. **均场约化**：将 agent-based 模型均场约化为非线性振荡器，发现连续 Hopf 分岔（amplitude A ∝ (C-C_c)^½）+ 不连续 fold 转变
  3. **平方根冲击必要性**：**关键理论发现**——平方根价格冲击是内生操纵周期的**必要条件**。线性冲击消除 Hopf 分岔，使散户市场无条件稳定（无操纵周期）；平方根冲击（更符合 A 股大单冲击实证）引入非线性反馈，使机构能通过"卖出-触发羊群-低位回补"循环获利

- **对 §3.7.x 系列的理论支撑**：
  | §3.7.x 算法 | 检测目标 | Zhou 理论支撑 |
  |---|---|---|
  | §3.7.1 Hawkes | 事件聚集 | 操纵周期的"卖出-羊群-回补"循环产生事件聚集 |
  | §3.7.6 ExsdHawkes | LOB 状态失稳 | 涨跌停板使 LOB 状态消失，Zhou 模型直接建模此机制 |
  | §3.7.7 Liquidation Cascade | 三因子级联 | "流动性撤回"因子对应 Zhou 的"隐形分配减半"机制 |
  | §3.7.9 Weng 羊群 | 截面羊群度 | Zhou 的 20,000 散户 agent 是 Weng 羊群的微观基础 |

  Zhou 模型为 §3.7.x 系列提供**统一的 A 股内生操纵机制理论**——所有检测算法的预警信号本质上都在捕捉 Zhou 模型描述的"机构卖出-羊群跟风-流动性撤回-低位回补"循环的不同侧面。

- **对 [40号执行算法](40_execution_broker.md) 的启示**：Zhou 证明平方根冲击是操纵周期必要条件——[40号](40_execution_broker.md) §2.12 平方根冲击模型（已施工）不仅是执行成本建模，更是**操纵周期检测的输入**。当平方根冲击系数异常升高时，可能预示操纵周期启动——可联动 §3.7.1 Hawkes 的"冲击幅度"因子。

- **为何储备而非采纳**：
  1. **理论模型非工程算法**：Zhou 是 agent-based 理论模型证明平方根冲击必要性，非可直接施工的预警算法——其价值是理论支撑非直接部署
  2. **A 股专属但参数难校准**：20,000 散羊 agent 的行为参数（跟风概率/信息延迟）需 A 股实盘数据校准，MVP 阶段无校准依据
  3. **与 §3.7.1 Hawkes 重叠**：Zhou 的"操纵周期产生事件聚集"是 Hawkes 预警的理论解释，非独立预警算法——Hawkes 已能检测事件聚集，Zhou 提供机制理解

- **重评条件**：① §3.7.1 Hawkes 上线后若需理解预警信号的微观机制；② [40号](40_execution_broker.md) §2.12 平方根冲击系数实盘校准后，验证"冲击系数异常升高→操纵周期启动"假设；③ A 股散户跟风行为参数（跟风概率/信息延迟）实证研究可得

#### 3.7.11 LRISK 系统性流动性风险前瞻指标 —— 储备（Phase 2+ 远期，系统级前瞻预警）

> **v1.0.13 新增**：§3.7.1-§3.7.10 聚焦"检测流动性危机何时发生"的微观/中观信号（tick 级事件聚集 + 日级羊群 + 盘口微结构），但缺一个**系统级前瞻指标**——从全市场基金部门层面预测"系统性赎回冲击下的总价格压力"。2026-07-14 最新研究（[Jourde, Saillard & Van Dijk 2026-07-14 SSRN 7110978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7110978)，Banque de France/CREST，"LRISK: Systemic Liquidity Risk in Mutual Funds"，原稿 2026-01-05）提出 **LRISK**——前瞻性系统性流动性风险度量，量化"严重系统级赎回冲击条件下基金部门对金融市场施加的总价格压力"。

**算法**（[Jourde, Saillard & Van Dijk 2026 SSRN 7110978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7110978)）：
- **核心创新**：三大放大通道整合的前瞻性系统级指标
  1. **流量共振（flow commonality）**：相关联的赎回导致基金同时卖出——用 flow beta 动态预测聚合基金流的极端尾部（超越静态假设冲击）
  2. **组合重叠（portfolio similarity）**：重叠持仓将同时卖出压力集中在相同资产上——用基金持仓穿透映射销售到具体资产
  3. **流动性螺旋（liquidity spirals）**：抛售本身内生恶化资产流动性——用非线性价格下跌建模反馈环（超越线性价格冲击假设，区别于 Duarte & Eisenbach 2021 的线性假设）
- **实证验证**：应用于 2011-2024 美国公司债基金，LRISK 隐含价格压力在 COVID-19 危机期间预测债券横截面收益；聚合层面 LRISK 作为早期预警信号**提前两个季度预测市场承压**；LRISK 还解释了基金采用 in-kind redemption（实物赎回）作为流动性管理工具的差异
- **与现有系统性风险指标对比**：CoVaR（Adrian & Brunnermeier 2016）/ SRISK（Brownlees & Engle 2017）为银行设计非资产管理；LRISK 专为开放基金部门的流动性错配设计——捕捉"每日赎回承诺 vs 持有非流动证券"的脆弱性

- **与 §3.7.x 系列的关系**：
  | §3.7.x 算法 | 层级 | 时间尺度 | LRISK 关系 |
  |---|---|---|---|
  | §3.7.1 Hawkes / §3.7.6 ExsdHawkes | 微观（tick 事件聚集） | 分钟级 | LRISK 是**宏观前瞻**层，Hawkes 是**微观即时**层 |
  | §3.7.7 Liquidation Cascade | 中观（级联机制） | 分钟-小时级 | LRISK 的"流动性螺旋"通道是 Liquidation Cascade 的系统级聚合 |
  | §3.7.9 Weng 羊群 | 中观（截面羊群） | 日级 | LRISK 的"流量共振"通道是 Weng 羊群的资金流侧体现 |
  | §3.7.10 Zhou 操纵周期 | 理论（机制） | — | LRISK 不涉及操纵周期，专注被动赎回→火售外溢 |

  LRISK 为 §3.7.x 系列补上**系统级前瞻预警层**——所有微观/中观检测算法捕捉的是"危机已发生/正在发生"，LRISK 提前 1-2 季度预测"危机即将发生"。

- **与 §5.2 Residual Supply 的关系**：§5.2 v1.0.12 已登记 Residual Supply（[arXiv:2605.30672](https://arxiv.org/abs/2605.30672)）作"被迫卖出压力信号"——单资产侧的 forced selling premium。LRISK 是**全市场系统级**的 forced selling 外溢度量（基金部门共振赎回→重叠持仓→火售螺旋）。两者递进：Residual Supply 管单资产被迫卖出 premium，LRISK 管全市场被迫卖出系统性外溢。

- **A 股适配评估**：
  - **数据可得性**：A 股公募基金持仓穿透数据每季度披露（滞后），北向资金日频可得，融资余额日频可得——可用于近似 flow commonality + portfolio similarity
  - **机制差异**：论文用美国公司债基金（OTC 流动性差 + 每日赎回错配），A 股股票型基金流动性更好但 2026-07 量化危机实证（CSI300 -5.81%/科创50 -17.46%）显示 A 股基金赎回→集中卖出→流动性螺旋机制同样存在
  - **简化适配**：用公募赎回率 + 北向净流出 + 融资余额下降三项的加权 z-score 作为 LRISK 简化代理（flow commonality 近似），重叠持仓用基金重仓股集中度近似（portfolio similarity 近似）

- **为何储备而非采纳**：
  1. **系统级指标非个股检测**：LRISK 是市场级前瞻指标，MVP 阶段 LEVEL_1/2/3 响应基于个股/组合级信号（sell_pressure + spread），系统级信号到 MVP 响应有层级跳跃
  2. **数据频率与滞后**：A 股公募持仓季度披露滞后，北向/融资日频——LRISK 的"提前两季度"预警在 A 股数据频率下可能退化为"提前数周"
  3. **与 §5.2 Residual Supply 重叠**：两者都需 fund flow 数据接入，Residual Supply 已先登记（v1.0.12），LRISK 是其系统级扩展——须先验证 Residual Supply 边际价值再考虑 LRISK

- **重评条件**：① §5.2 Residual Supply 上线后若发现单资产级 forced selling 信号有效但缺系统级聚合；② A 股公募基金持仓穿透数据可得频率提升（月频或更高）；③ 与 §3.7.1 Hawkes 日级预警（图熵领先 7-12 天）对比，验证 LRISK 系统级是否提供额外 lead-time

#### 3.7.12 欧洲 ML 流动性预测对比 —— 储备（Phase 1.5 候选，Amihud 预测方法学）

> **v1.0.13 新增**：§3.1.2 用 Quoted Spread + §2.2 MOD-RK-08 用 Amihud 日频做流动性监控，但**阈值是静态经验值**（spread 0.5% / Amihud 历史分位）。§5.2 Phase 1.5 已规划"阈值实盘校准"，但未涉及"Amihud 本身如何预测"。2026-07-16 最新研究（[Arakelia, Caporale, Gasparinatou & Karanasos 2026-07-16 SSRN 7125463 / CESifo WP 12829](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7125463)，"Machine Learning and Liquidity Dynamics in European Stock Markets"）系统对比传统计量与 ML 对 Amihud 非流动性指标的预测能力——为 §5.2 Phase 1.5 阈值校准 + Amihud 预测提供方法学参考。

**算法**（[Arakelia et al. 2026 SSRN 7125463](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7125463)）：
- **核心框架**：欧洲五大股指（DAX/CAC 40/FTSE 100/FTSE MIB/IBEX 35）2010-2026 日频数据，对数 Amihud 非流动性指标的一步滚动预测
  1. **传统计量基线**：ARIMA 模型 + 动态面板（dynamic panel）设定
  2. **ML 对比**：Random Forest / XGBoost / SVR，统一 walk-forward 滚动框架
  3. **可解释性**：SHAP 分析识别流动性预测的主要驱动因子
- **关键发现**：
  - 流动性**高度持续**（highly persistent）——滞后流动性是最强预测因子
  - **动态面板模型预测误差最低**，但 Diebold-Mariano 检验表明其相对 ML 模型**无显著预测优势**——简单计量模型不输 ML
  - SHAP 分析：**成交活跃度 + 滞后流动性 + 市场不确定性**是三大驱动因子

- **对 §3.1 / §5.2 的方法学启示**：
  | 启示 | 应用到 37 号 |
  |---|---|
  | 流动性高度持续 | §3.1 静态阈值合理——高持续意味着今日 Amihud ≈ 昨日，阈值无需频繁更新 |
  | 动态面板不输 ML | §5.2 Phase 1.5 阈值校准可用简单动态面板（Amihud_t = α + β·Amihud_{t-1} + γ·volume_t + δ·volatility_t + ε）而非重 ML 栈——符合 MVP 简化原则 |
  | 三大驱动因子 | §5.2 Phase 1.5 特征工程：成交活跃度（换手率）+ 滞后 Amihud + 市场不确定性（A 股用波动率/期权 IV 近似）作为 Amihud 预测输入 |

- **与 §3.7.4 SaR 的关系**：§3.7.4 SaR 是**前瞻性滑点预测**（从盘口微结构推导），本条是**前瞻性 Amihud 预测**（从时间序列计量推导）——两者正交：SaR 管"下一笔清算的滑点"，Amihud 预测管"明日整体非流动性状态"。

- **A 股适配评估**：论文用欧洲蓝筹股指，A 股用沪深 300/中证 500 成分股——Amihud 高持续 + 三大驱动因子结论跨市场稳健（流动性时间序列的普遍特征）；动态面板设定可直接迁移（面板数据 = 多股票 × 多日期）。

- **为何储备而非采纳**：
  1. **MVP 阶段 Amihud 静态阈值已够**：§2.2 MOD-RK-08 Amihud 日频已 production，流动性高持续意味着静态阈值在短期不会失效——预测模型边际价值低
  2. **方法学参考非独立模块**：本条价值是"为 §5.2 Phase 1.5 阈值校准提供方法学选择"（用动态面板而非 ML），非独立预警算法
  3. **与 §3.7.5 Latent build-up 重叠**：§3.7.5 已登记"前瞻性微结构 regime 检测"（正 lead-time），本条是"前瞻性 Amihud 预测"——两者都做前瞻但维度不同（微结构 vs 日级流动性），§3.7.5 优先级更高

- **重评条件**：① §5.2 Phase 1.5 阈值校准时选择预测模型——本条提供"动态面板 + 三特征"轻量方案作为 ML 替代；② 实盘 6 月 Amihud 数据验证高持续性假设；③ 与 §3.7.5 Latent build-up 同期评估（微结构前瞻 vs 日级前瞻 lead-time 对比）

#### 3.7.13 AdjPIN 订单流信息/流动性分解 —— 储备（Phase 2 候选，§3.7.2 VPIN 配套细化）

> **v1.0.13 新增**：§3.7.2 基于 ClusterLOB 2026-06 实证（VPIN 与 OBI 相关性 0.85+ 信息冗余）维持拒绝 VPIN。但 VPIN 拒绝留下一个 gap：**如何区分"信息驱动的价格移动"与"纯流动性危机"**——§3.3 LEVEL 响应须区分两者（信息驱动 = 跟随减仓，纯流动性 = 等待恢复避免在流动性枯竭时交易）。2026-07-14 最新研究（[Park 2026-07-14 SSRN 7119388](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7119388)，"Is Machine Learning Predictability Driven by Information or Liquidity? Evidence from Order Flow and AdjPIN Decomposition"）用 AdjPIN 模型将订单流分解为**信息不对称成分 + 流动性成分**，为 §3.7.2 VPIN 拒绝后的"信息/流动性分离"提供方法学路径。

**算法**（[Park 2026 SSRN 7119388](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7119388)，基于 Duarte & Young 2009 AdjPIN 模型 + Ghachem & Ersan 2025 ECM 估计）：
- **核心创新**：AdjPIN 将传统 PIN 分解为两个正交成分
  1. **AdjPIN（信息不对称成分）**：知情交易概率——捕捉信息驱动的订单流（知情交易者基于私有信息买卖）
  2. **PSOS（对称订单流冲击 / 流动性成分）**：对称买卖双增的流动性冲击——捕捉非信息驱动的订单流（如做市商调仓/流动性提供者撤退）
- **Park 2026 实证发现**：ML 对收益的可预测性主要由**流动性成分（PSOS）**而非信息成分（AdjPIN）驱动——"机器学习能预测"不等于"有信息含量"，部分可预测性来自流动性溢价
- **估计方法**（Ghachem & Ersan 2025，[tandfonline 10.1080/14697688.2025.2515929](https://www.tandfonline.com/doi/full/10.1080/14697688.2025.2515929)）：ECM（Expectation-Conditional Maximization）算法 + 对数似然分解，解决 AdjPIN 参数空间大导致的数值不稳定 + 局部最优问题

- **对 §3.7.2 VPIN 拒绝的补全**：
  | 维度 | §3.7.2 VPIN（已拒绝） | §3.7.13 AdjPIN 分解（本条） |
  |---|---|---|
  | 检测目标 | 知情交易概率（单一指标） | 信息成分 + 流动性成分（分解） |
  | 与 OBI 冗余 | 高（相关性 0.85+，ClusterLOB 实证） | 低——PSOS 流动性成分与 OBI 的卖压方向不同（PSOS 是对称双增，OBI 是单边卖压） |
  | 对 §3.3 的价值 | 低（单一指标不分信息/流动性） | **高**——区分"信息驱动价格移动"（跟随减仓）vs"纯流动性冲击"（等待恢复，避免在流动性枯竭时交易） |

- **与 §3.1.1 sell_pressure 的关系**：§3.1.1 sell_pressure = ΣVolAsk/(ΣVolBid+ΣVolAsk) 是**单边卖压**度量；AdjPIN 的 PSOS 是**对称买卖双增**的流动性冲击度量——两者正交：sell_pressure 检测"单边卖压危机"，PSOS 检测"对称流动性冲击（如做市商撤退导致双边挂单同时消失）"。

- **A 股适配评估**：
  - **数据可得性**：AdjPIN 估计需 tick 级买卖分类（buy-initiated vs sell-initiated trades）——A 股 miniQMT tick 数据可得，可用 Lee-Ready 规则或 tick rule 分类
  - **A 股做市商差异**：AdjPIN 原模型假设做市商提供流动性，A 股无正式做市商（除科创板做市商制度 2022 起）——PSOS 在 A 股解释为"流动性提供者（含高频被动单）撤退导致的对称订单流冲击"
  - **估计成本**：ECM 算法每只股票每日需迭代估计，计算成本中等——A 股 ~5000 股票全市场实时估计不可行，但可限定到持仓股 + 观察池

- **为何储备而非采纳**：
  1. **§3.7.2 已拒绝 VPIN/PIN 家族**：AdjPIN 是 PIN 家族的改进版（分解信息/流动性），但 §3.7.2 拒绝 VPIN 的理由（与 OBI 冗余 + MVP 双条件 AND 已够）部分适用——须先验证 AdjPIN 的 PSOS 成分相对 OBI 的增量价值
  2. **计算成本**：ECM 估计每只股票每日迭代，MVP 阶段无此计算预算——Phase 2 候选
  3. **与 §3.7.5 Latent build-up 重叠**：§3.7.5 已登记"隐含微结构 regime 检测"（含 depth erosion + HMM 熵），部分覆盖"流动性提供者撤退"检测——须先验证 §3.7.5 不够再引入 AdjPIN

- **重评条件**：① §3.3 LEVEL 响应实盘发现"信息驱动 vs 纯流动性"区分不足导致响应失误（如在纯流动性冲击中过度减仓）；② §3.7.5 Latent build-up 上线后若未覆盖"对称流动性冲击"检测；③ 持仓股 tick 级买卖分类数据管道就绪 + ECM 估计计算预算可承担

#### 3.7.14 Signed Order Flow Kyle λ —— 有向订单流恢复方向性信息（Phase 2 候选，§3.1 流动性因子增强）

> **v1.0.14 新增**：[Aldridge 2026-07-01, "Liquidity Premium and Investment Horizons"](https://arxiv.org/abs/2607.01377) 直接从日度股票订单流估计 Kyle (1985) 的价格冲击系数 λ̂，构建两种估计量：月内价格冲击回归与 Amihud 式比率。用 CRSP 2020-2025 数据，Fama-MacBeth 回归证明**有向(signed)订单流**强预测当期与未来一月收益，而成交量波动预测较低未来收益（因噪声交易方差扩大 λ、降低价格发现精度）。

**核心方法**：
- **Kyle λ 估计**：λ̂ = Cov(ΔP, OF_signed) / Var(OF_signed)，其中 OF_signed 为有向订单流（买方发起为正、卖方发起为负）。相比 Amihud ILLIQ = |r_d|/V_d（无向），Kyle λ 恢复了 Kyle 均衡中的**方向性信息含量**
- **两种估计量**：① 月内价格冲击回归（ΔP = λ·OF + ε，滚动月窗 OLS）；② Amihud 式比率（日频 |ΔP|/|OF| 的月均，类 Amihud 但用有向 OF 替代无向 V）
- **理论贡献**：通过逆向选择机制解决 Constantinides (1986) 流动性溢价之谜——有向 OF 的信息含量使 λ 捕获流动性溢价，而无向成交量扩大噪声方差降低价格发现精度

**与 §3.1 Amihud 的关系**：
| 维度 | §3.1 Amihud ILLIQ（已采纳） | §3.7.14 Signed Kyle λ（本条） |
|---|---|---|
| 方向性 | 无向（\|r\|/V） | 有向（OF_signed 回归） |
| 信息含量 | 仅流动性成本 | 流动性成本 + 信息含量 |
| 数据需求 | OHLCV（日频） | 需买卖分类（Lee-Ready/tick rule） |
| 计算成本 | 极低 | 中（需 tick 级买卖分类） |
| A 股数据 | 可得（日频 OHLCV） | 可得（miniQMT tick 数据） |

**A 股适配**：① A 股日度数据完备，signed order flow 可从 Level-2 重建（Lee-Ready 规则或 tick rule 分类买卖方向）；② 对流动性因子构建与选股直接可用——Kyle λ 可作为多因子模型中的流动性因子维度；③ A 股散户占比高，噪声交易方差大，Aldridge 的"噪声交易扩大 λ 降低价格发现精度"洞察尤其重要

**为何储备而非采纳**：
1. **§3.1 Amihud 已满足 MVP**：Amihud 无向 ILLIQ 已作日频结构性流动性恶化监控，MVP 不需方向性信息
2. **数据管道成本**：signed OF 需 tick 级买卖分类，MVP 阶段流动性监控用日频 OHLCV 即可，Phase 2 引入 Level-2 数据管道后评估
3. **与 §3.7.13 AdjPIN 重叠**：两者都需 tick 级买卖分类，AdjPIN 分解信息/流动性，Kyle λ 量化价格冲击——Phase 2 可同时引入

**重评条件**：① miniQMT Level-2 tick 数据管道就绪；② §3.1 Amihud 实盘发现无向 ILLIQ 不足以区分"信息驱动价格冲击"与"纯流动性成本"；③ 多因子模型需引入流动性因子维度

#### 3.7.15 流动性尾部风险与价格发现 —— 大单非信息场景（Phase 2 候选，§3.3 LEVEL 响应理论支撑）

> **v1.0.14 新增**：[Çetin, Lin & Livieri 2026-07-21, "When large trades are not (automatically) news: liquidity tail risk and price discovery"](https://arxiv.org/abs/2607.01198)（LSE）研究重尾流动性需求如何改变价格发现。在序贯 LOB 中，流动性供给方只观测聚合订单流而非其分解；当非知情订单流重尾(Student-t, ν>2)时，大额交易在更宽深度范围内仍"合理地非知情"，**压平价格冲击、减缓学习**。

**核心方法**：
- **重尾流动性需求建模**：非知情聚合订单流为 Student-t (ν>2)，大单在更宽深度范围内仍"看似非知情"——压平深度价格冲击并放慢价格发现学习
- **非线性不动点方程**：刻画边际成本计划的均衡，在尾部受控类中证明不动点存在性、后验一致性
- **尾部渐近**：推导边际成本、知情需求与聚合订单流的尾部渐近行为
- **AAPL 10 档数据实证**：重尾大单后存在持续的买卖价差与远端交叉诊断

**核心洞察——"大单 ≠ 信息"**：
传统微结构假设"大单 = 知情交易"（Easley-O'Hara），Çetin 2026 证明当流动性需求重尾时，**大单在更宽深度范围内仍"合理地非知情"**——大单未必是信息。这对 A 股尤其重要：A 股大单常源于机构调仓/融资盘平仓/公募赎回而非信息驱动。

**与 §3.3 LEVEL 响应的关系**：
- §3.3 LEVEL 响应在检测到大单冲击时须区分"信息驱动"（跟随减仓）与"纯流动性"（等待恢复避免在流动性枯竭时交易）
- Çetin 2026 提供**理论支撑**：重尾流动性需求下大单更可能是非信息的——倾向"等待恢复"而非"跟随减仓"
- 与 §3.7.13 AdjPIN 互补：AdjPIN 从订单流分解角度区分信息/流动性，Çetin 从价格发现学习速度角度区分

**A 股适配**：① A 股大单常源于机构调仓/融资盘平仓/公募赎回（非信息），重尾流动性需求假设非常契合；② 对大单冲击建模与执行算法有直接指导——大单后不应自动假设信息驱动而跟随减仓；③ T+1 制度下大单次日开盘反应可验证"大单=信息"假设是否成立

**为何储备而非采纳**：
1. **理论性较强**：Çetin 2026 是理论微结构论文，工程落地需将不动点方程数值化
2. **与 §3.7.13 AdjPIN 功能重叠**：两者都区分信息驱动 vs 纯流动性，AdjPIN 更工程化（有 ECM 估计实现）
3. **§3.3 LEVEL 响应当前简化**：MVP 用大单阈值 + Amihud 双条件触发，不需重尾流动性需求建模

**重评条件**：① §3.3 LEVEL 响应实盘发现大单后"跟随减仓 vs 等待恢复"决策失误频繁；② §3.7.13 AdjPIN 上线后若信息/流动性分离仍不充分；③ 需要大单冲击的定量预测模型（而非仅定性区分）

### 3.8 施工流程算法总览（盘中流动性监控循环）

> **持续改进补全**：35 号 §3.13 有"盘中实时风控循环 30 秒轮询"伪代码，36 号 §3.12 有"盘中 VaR/ES 重算触发"伪代码，37 号 之前只有各决策（§3.1 检测 / §3.3 响应 / §3.6 恢复）的独立算法，**缺一个编排总览**将检测→响应→恢复→涨跌停处理串成单循环。补齐此 gap 使三篇风控文档施工流程对齐（均有日度循环 + 盘中循环 + 总览时序）。

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
    if limit_status in ("LIMIT_UP", "LIMIT_DOWN"):
        # 涨跌停时 spread 置 1.0 使 §3.1 AND 条件可满足（§3.5 算法断裂修复）
        effective_spread = 1.0
    
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
- **拒绝理由**：MOD-RK-10 已实现 LIQUIDITY_CRISIS 信号 + 三级警报 + Kill Switch 联动，重复造轮子违反 AI-dev 归因清晰度原则
- G18 的价值是给已有实现补 why 层 + 对齐 §2.5.5 spec，不是新建基础设施
- 新建模块会制造"流动性危机检测有两个真相源"的歧义

### 4.2 实时 tick 级 spread 监控 —— 拒绝（过度工程）
- **拒绝理由**：个人系统无需 tick 级流动性监控基础设施（需维护 tick 级盘口数据管道 + 实时 spread 计算 + 低延迟告警），投入产出比极低
- MOD-RK-10 的秒级/分钟级检测已足够（流动性危机是分钟级事件，不是微秒级）
- 机构做 tick 级是因为它们自身交易会影响流动性（大单冲击），个人小资金自身不影响

### 4.3 流动性危机直接清仓 —— 拒绝
- **拒绝理由**：§2.5.5 明确是"停开仓仅平仓"不是清仓；流动性危机时强制清仓会踩踏（卖在最低点）
- 只有 ≥3 信号（系统性崩盘）才清仓（LEVEL_3），此时"跑得快"比"卖得好"重要
- 分级响应（LEVEL_1 停开仓 / LEVEL_3 清仓）比一刀切更合理

### 4.4 "价差 > 正常 5x" 相对阈值 —— 部分采纳（MVP 用绝对阈值）
- **拒绝理由（MVP）**：相对阈值需维护"N 日均价差"基准，每只票的"正常 spread"不同（大盘股 0.01% vs 小盘股 0.3%），基准维护复杂
- 代码用绝对 0.5% 阈值：A 股正常票 spread 0.01-0.05%，0.5% 已是 10-50 倍，与"5x"量级吻合，简单且误报低
- **重评条件**：实盘运行后若绝对阈值误报多（小盘股日常 spread 接近 0.5%），再上推相对阈值

### 4.5 盘口深度实时监控 —— 拒绝（MVP 延后）
- **拒绝理由**：盘口深度（多档买卖盘挂单量）需实时 Level-2 数据 + 深度衰减建模，是机构级基础设施
- 个人小资金订单 <1% ADV，盘口深度对自身交易无意义（自己不消耗深度）
- MOD-RK-08 Amihud（日频）+ MOD-RK-10 spread（盘内）已覆盖"流动性是否够用"的核心问题
- 依赖 depth 的复合评分（如 Polymarket 2026-06 Liquidity Score = (depth × volume)/(spread + ε)）一并暂缓
- **重评条件**：AUM 增长到自身订单 >5% ADV 时

### 4.6 VPIN 订单流毒性检测 —— 拒绝（过度工程）
- **拒绝理由**：VPIN（Volume-Synchronized Probability of Toxicity）需 tick 级交易数据 + 时间桶成交量分类，是机构级闪崩早期预警指标（theplugg 2026-07 将其与 OBI、Depth-to-Volatility Decay 并列为闪崩三大指标）
- 个人小资金不需要 tick 级毒性检测——自身不提供流动性（不做市），不受 toxic flow 直接伤害
- MOD-RK-10 的卖压 + spread 双条件已捕获 VPIN 试图检测的同一类信号（流动性枯竭 + 单向交易压力）
- **重评条件**：若策略扩展到做市/提供流动性场景时

### 4.7 Karimi 流动性-信贷联合破产边界 —— 暂缓（Phase 3 远期，选项之外更好的算法）

> **v1.0.10 新增**：当前 G18 流动性危机检测（MOD-RK-10 双条件 AND）与 G16 回撤 Protocol（drawdown_tracker）是两个独立模块——流动性危机检测"流动性枯竭"，回撤 Protocol 检测"净值下跌"。但 2026-07 最新研究表明，流动性与信贷风险的**非线性联合作用** disproportionally 加速破产——两者联合效应远大于个体效应之和。

**算法**：[Karimi & Ahmadian 2026-07 arXiv:2607.17381](https://arxiv.org/abs/2607.17381)（"Determining Insolvency Regions in Banks: A Stochastic Dynamic Approach Integrating Liquidity and Credit Risk"）：
- **核心创新**：连续时间结构动态模型，用 HJB（Hamilton-Jacobi-Bellman）方程求解流动性-信贷联合作用的精确破产边界
- **Liquidity-Credit Spiral**：funding shocks + 监管约束（Basel III LCR/NSFR）→ 资产负债表调整 → 内生破产。流动性冲击迫使银行出售资产 → 信贷组合质量恶化 → 进一步流动性压力（正反馈回路）
- **边界凸性**：破产边界 B_exact 在 (λ,d) 平面（λ=流动性压力, d=信贷违约）中是凸的——同时增加流动性和信贷压力的效应大于两者独立效应之和
- **代理函数**：推导并验证代理解析近似函数 B_surrogate = w₁λ + w₂d + w₃λd（w₃>0 严格正反映凸性），允许实时监控
- **Iranian banking 实证**：用细粒度资产负债表数据校准，确认非线性阈值效应

**与 G18/G16 的关系**：
- 当前 G18 MOD-RK-10 检测"流动性危机"（spread + sell_pressure），G16 drawdown_tracker 检测"净值下跌"——两者独立触发
- Karimi 框架表明：流动性危机 + 回撤同时发生时的破产风险 > 两者独立触发之和——联合状态需额外 risk premium
- **对 LEVEL_3 升级的理论支撑**：MOD-RK-10 的 LEVEL_3（≥3 信号联动 Kill Switch）隐含"多信号联合 = 系统性风险"的直觉，Karimi 的边界凸性为这一直觉提供了数学基础

**为何暂缓而非采纳**：
1. **银行级模型**：Karimi 模型针对银行（有 LCR/NSFR 监管约束 + 信贷组合），个人量化系统无信贷组合 + 无监管约束
2. **数据依赖**：需流动性-信贷联合状态变量（λ,d），个人系统的"信贷"维度缺失（无融资融券数据接入）
3. **MVP 双条件 AND 已覆盖联合检测**：MOD-RK-10 双条件 AND（sell_pressure + spread）是 Karimi 联合边界的简化版——两者同时高即触发，近似联合状态检测

**重评条件**：① 接入融资融券数据后（"信贷"维度可得），可构建 (流动性, 信贷) 联合状态监控；② AUM 增长到需关注流动性-信贷螺旋时；③ 与 §3.7.8 Multiplex Network Hawkes 同步评估（Karimi 管联合状态边界，Multiplex 管传染通道）

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
- **第二阶段（AUM 增长或策略需要）**：盘口深度监控（Level-2 多档数据 + 深度衰减建模）+ Bouchaud Propagator（冲击时间衰减结构，与 40_execution_broker 滑点模型协同）+ 流动性综合评分 Liquidity Score = (depth × volume)/(spread + ε) 作为 depth/volume/spread 三者的复合归一化指标 + **Crumbling Labeler**（§3.7.3 远期储备：区分机械撤退 vs 信息重定价，优化 LEVEL_3 清仓决策）+ **SaR 前瞻性框架**（§3.7.4 储备：SaR(α)/ESaR(α)/TSaR(α) + 集中度调整，前瞻性滑点预测 + 识别脆弱盘口结构，与 Hawkes 叠加为双层前瞻预警）+ **Residual Supply 被迫卖出压力信号**（[arXiv:2605.30672 2026-05-29](https://arxiv.org/abs/2605.30672) Wang "Residual Supply and the Price of Risk Absorption"：连续时市场出清模型将残余供给价格分解为库存风险补偿+资本与调整楔子，被迫卖出压力预测当期价格下跌+随后 1-6 月正收益（65bp/月，217bp/6 月），**全市场吸收能力紧张时 premium 翻倍**——A 股适配：用公募赎回数据/北向净流出/融资余额下降近似 forced selling pressure，market-wide absorption capacity strain 作为 LEVEL_2 升级信号；Phase 2+ 远期因需 fund flow 数据接入）+ **LRISK 系统级前瞻预警**（§3.7.11 储备：[SSRN 7110978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7110978) Jourde/Saillard/Van Dijk 2026 三大放大通道——流量共振+组合重叠+流动性螺旋，提前 1-2 季度预测市场承压，A 股用公募赎回+北向净流出+融资余额 z-score 近似 flow commonality；Phase 2+ 远期因与 Residual Supply 同需 fund flow 数据，须先验证单资产级边际价值）+ **AdjPIN 信息/流动性分解**（§3.7.13 储备：[SSRN 7119388](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7119388) Park 2026 将订单流分解为 AdjPIN 信息成分 + PSOS 流动性成分，区分"信息驱动价格移动"vs"纯流动性冲击"优化 §3.3 LEVEL 响应——信息驱动跟随减仓、纯流动性等待恢复避免流动性枯竭时交易；Phase 2 候选因 ECM 估计计算成本中等）

### 5.3 为何这是上限而非妥协
- 个人账户小资金，多数订单 <1% ADV，自身交易不构成流动性冲击——流动性危机是市场级事件，检测市场级信号（卖压 + spread）已足够
- MOD-RK-10 已是 5 信号系统性风险检测器的一部分，LIQUIDITY_CRISIS 是其中 1 个信号，复用边际成本为零
- 盘口深度/tick 级监控是机构级基础设施（需 Level-2 数据 + 低延迟管道），个人系统投入产出比极低
- 流动性危机的核心风险是"在流动性差时还去开仓"——停开仓（LEVEL_1）已消除此风险，无需更复杂的响应

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

## 7. 待定问题（讨论要点 resolved）

> 以下 5 项来自 00_index §3 G18 讨论要点，已逐项对齐落入 §3 决策。

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
- A 股涨跌停流动性失效：涨停板买单堆积/跌停板卖单堆积，盘口退化为单价位（上交所 2026 修订交易规则 §3.3.13 涨跌幅限制）
- 流动性度量指标：买卖价差（最基础，taker 成本）/ 成交量与换手率（活跃度）/ 盘口深度（多档挂单量）——经验法则 spread <0.1% = 高流动性，>1% = 低流动性
- Beelaa 2026-08 做市商撤退与 spread 扩大实证：2026-01 比特币闪崩，做市商撤退导致 IBIT spread 从 2-3bps 扩至 8-10bps（3-4 倍），**5% 抛压→15% 暴跌**（流动性放大 3 倍）——支撑"双条件 AND"假设（卖压+spread 同时扩大=流动性枯竭）+ "LEVEL_1 停开仓不清仓"决策（危机时强制清仓会踩踏）
- theplugg 2026-07 闪崩三阶段模型：机构大单冲击 → 算法撤退 + spread 扩大 → 跨资产级联 + stub quote 成交——VPIN/OBI/Depth-to-Volatility Decay 三大早期预警指标（本系统用卖压+spread 等价覆盖）
- LobeHub 2026-08 microstructure 实践：spread widening alerts trigger when > 3x average（3 倍均值早期预警）——§5.2 Phase 1.5 双阈值方案来源
- Polymarket 2026-06 流动性监控引擎：OBI >0.60 买压主导 / <0.40 卖压主导——与 sell_pressure 0.65 阈值等价（sell_pressure = 1 - OBI），阈值量级与行业对齐
- ClusterLOB 2026-06 OFI 与 VPIN 相关性实证：VPIN 与 OBI 相关性 0.85+，信息冗余——支撑 §3.7.2 VPIN 维持拒绝决策
- stockalpha.ai 2026-02 + arxiv 2310.09273 Hawkes 自激励过程：λ(t) = μ + Σ α·exp(-β(t-t_i)) 建模流动性事件聚集性——§3.7.1 Hawkes 储备来源
- ICLR 2026 Crumbling Labeler：神经网络区分机械性流动性撤退 vs 信息驱动重定价——§3.7.3 Crumbling Labeler 远期储备来源
- theplugg 2026-07 闪崩三大指标（VPIN/OBI/Depth-to-Volatility Decay）+ Crumbling Labeler 引用——§3.7 2026 前沿算法评估来源
- [arXiv:2603.09164](https://arxiv.org/abs/2603.09164) Sepper 2026-03 SepperLabs "Slippage-at-Risk (SaR): A Forward-Looking Liquidity Risk Framework"——§3.7.4 SaR 前瞻性框架来源：SaR(α)/ESaR(α)/TSaR(α) 三度量 + 集中度调整（Concentration Haircut，HHI 弹性 η≈1.5），从当前盘口微结构推导前瞻性清算执行风险，区别于 VaR 等回溯性指标。Hyperliquid 2025-10-10 清算级联实证 SaR 作为系统性压力领先指标的有效性
- [arXiv:2608.03616](https://arxiv.org/abs/2608.03616) 2026-08 强制平仓级联群组分析——§3.7.4 实证支撑：7 起加密货币强平级联（2022-2025）揭示级联起始突变性（order parameter 跳变 1.6-4.4σ）+ 两类型分类（内生累积型有前兆 vs 外生冲击型无前兆），为"Hawkes + SaR 双层前瞻预警"提供理论框架
- [arXiv:2604.20949](https://arxiv.org/abs/2604.20949) Hiremath & Hiremath 2026-04 "Early Detection of Latent Microstructure Regimes in Limit Order Books"——§3.7.5 Latent build-up 检测来源：三 regime 因果 DGP（stable → latent build-up → stress）+ trigger-based detector（MAX 聚合 + rising-edge + 自适应阈值）+ depth erosion + HMM 熵触发通道。核心洞察：OFI/spread/volatility 按构造是反应性的（negative lead-time），latent build-up 是可识别的前兆。仿真 lead-time +18.6 timesteps / 实数据 +38 秒，优于 CUSUM/BOCPD/HMM thresholding

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G18 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active，5 项讨论要点定型 | 全网搜索 2026 流动性监控 + 审查已有代码（MOD-RK-08/10 已 production）+ 对齐 §2.5.5 spec：① 复用 MOD-RK-10 LIQUIDITY_CRISIS（卖压+spread 双条件 AND）② 复用 MOD-RK-08 Amihud 日频 ③ 响应=LEVEL_1 停开仓仅平仓 ④ 流动性危机单独不 Kill Switch，≥3 信号才联动 ⑤ 涨跌停 spread 失效由执行层处理。过度工程审查：MOD-RK-08/10 已 production，G18 是 why 层对齐非新建基础设施，tick 级/盘口深度监控判定为过度工程暂缓。发现 §2.5.5"价差>5x"与代码"0.5%绝对"对齐方案（量级吻合，MVP 用绝对阈值）。发现 G16(35号)依赖项为骨架态待填。 |
| 2026-08-10 | 1.0.1 | G16 依赖对齐已解决 | 交叉引用核查发现 G16（35_drawdown_protocol_impl）已于 2026-08-10 同步升级为 active v1.0.0，§3.5 Kill Switch 触发与执行路径已填写完整，其多源触发表"流动性危机"行明确反向引用本备忘（买卖价差>5x → G18）。更新 4 处过时的"骨架态"描述为"active v1.0.0"：§1 依赖行、§3.4 决策④ G16 对齐段、§6 待裁定表（标记为已解决）、§8.1 引用。双向引用链建立，G16 确认流动性危机通过 LEVEL_3 间接联动 Kill Switch 与本备忘决策④一致。 |
| 2026-08-10 | 1.0.2 | 施工环节算法完整性审查 + 2026-08 研究对齐 | 深度二次审查发现并修复 4 项：① **算法断裂修复**：§3.5 涨跌停处理中"spread 置 None"与"LIQUIDITY_CRISIS 应触发"矛盾（代码要求 spread 非 None 才检查）——改为跌停时 spread 置大值 1.0 使 AND 条件可满足 ② **逃生执行器补全**：§3.3 补充 `build_escape_directive` 指令结构（directive/action/position_cap/cancel_pending_orders/halt_new_orders/kill_switch_required）+ 守卫（非 LEVEL_3 抛异常）+ 消费者（RK-17）+ 数据流 ③ **2026-08 实证对齐**：§8.4 补充 Beelaa 做市商撤退实证（spread 3-4 倍扩张 + 5%抛压→15%暴跌，支撑"双条件 AND"+"停开仓不清仓"）+ theplugg 闪崩三阶段 + LobeHub 3x average 早期预警 + Polymarket OBI 对齐 ④ **过度工程补审**：§4.6 显式拒绝 VPIN + §4.5 补 Liquidity Score 一并暂缓 + §5.2 Phase 1.5 双阈值方案（3x 预警/5x 危机）+ Phase 2 Liquidity Score 储备。全网搜索确认高频认定 300 笔/秒未变（40号文档辟谣正确，15 笔/秒为谣言）。 |
| 2026-08-10 | 1.0.3 | 施工流程算法补全 + 选项外更好算法评估 | 深度三次审查发现并补全 6 项：① **危机恢复算法**（§3.6）：§3.1-3.5 只定义"如何进入"LEVEL_1/2/3 未定义"如何退出"——补滞后-恢复双阈值（hysteresis）+ CUSUM 式 `check_recovery()` 持续时间门控（LEVEL_1 10min/LEVEL_2 15min/LEVEL_3 30min）+ 恢复执行动作矩阵 ② **sell_pressure 形式化**（§3.1.1）：补 OBI 反转公式 `sell_pressure = ΣVolAsk/(ΣVolBid+ΣVolAsk)` + OFI 一阶差分动态维度储备 ③ **spread 形式化**（§3.1.2）：补 Quoted Spread `(ask-bid)/mid` 公式 + 涨跌停特殊处理规则 ④ **涨跌停检测算法**（§3.5.1）：补 `detect_limit_status()` 五状态检测 + 涨跌停价获取 + 与 §3.1.1/3.1.2 联动表 ⑤ **2026 前沿算法评估**（§3.7）：Hawkes 自激励（Phase 1.5 储备，提前 1-3 分钟预警聚集性危机）/ VPIN 重评（维持拒绝，ClusterLOB 2026-06 实证 VPIN 与 OBI 相关性 0.85+ 信息冗余）/ Crumbling Labeler（Phase 2 远期储备，ICLR 2026 区分机械撤退 vs 信息重定价优化清仓决策）⑥ **§5.2 演进路径更新**：Phase 1.5 补 OFI + Hawkes，Phase 2 补 Crumbling Labeler；§6 待裁定补 4 项新暂缓项；§7 补决策⑥⑦；§8.4 补 5 条新参考 |
| 2026-08-10 | 1.0.4 | 补充 **§3.8 施工流程算法总览**（盘中流动性监控循环伪代码：四阶段编排 涨跌停检测→危机检测→响应执行→恢复判定 + 编排顺序设计理由表 + 与 35 号 §3.13/36 号 §3.12 三循环并行对齐 + A 股 T+1 约束影响）+ §7 补决策⑧ | 持续改进：用户要求再次审查文档所有内容+施工环节流程算法是否有缺失。对照 35 号（§3.10 日度循环 + §3.13 盘中循环 + §3.17 总览时序）和 36 号（§3.10 日度循环 + §3.11 回测端到端 + §3.12 盘中重算）发现 37 号 之前只有各决策（§3.1 检测/§3.3 响应/§3.6 恢复）的独立算法，**缺一个编排总览**将检测→响应→恢复→涨跌停处理串成单循环。补齐此 gap 使三篇风控文档施工流程对齐（均有日度循环+盘中循环+总览时序），编排顺序的关键是涨跌停检测须先于危机检测（spread 在涨跌停时失效须置 1.0 才能进入 §3.1 AND 条件） |
| 2026-08-10 | 1.0.5 | §2.4 约束条件新增"A 股无市场级指数熔断"澄清 | 用户要求评估 circuit breakers 作为流动性危机协议组成部分。A 股指数熔断机制于 2016-01-07 暂停实施（仅运行 4 个交易日因磁吸效应废止），现行波动控制依赖个股涨跌停板+盘中临时停牌。本协议中的"熔断"（BM-RC-03 Kill Switch 熔断）指策略级响应非市场级指数熔断，策略须自建断路器而非依赖交易所熔断——此澄清消除 circuit breaker 术语歧义，明确 G18 的断路器是策略级自建而非交易所级依赖 |
| 2026-08-10 | 1.0.6 | 补充 **§3.7.4 Slippage-at-Risk (SaR) 前瞻性框架评估**（选项之外更好的答案算法）+ 强制平仓级联两类型分类实证支撑 + 三算法→四算法评估汇总表更新 | 持续改进：用户要求再次审查"选项之外更好的答案算法"+ 全网搜索 2026 最新研究。发现 [arXiv:2603.09164](https://arxiv.org/abs/2603.09164) Sepper 2026-03 SepperLabs 提出的 SaR 框架——从当前盘口微结构推导**前瞻性**清算执行风险（区别于 VaR 等回溯性指标），含 SaR(α)/ESaR(α)/TSaR(α) 三度量 + 集中度调整（Concentration Haircut，HHI 弹性 η≈1.5，惩罚"少数做市商主导报价"的脆弱结构）。与 MOD-RK-10 现有 sell_pressure+spread 双条件 AND（回溯性、布尔触发、不感知做市商结构）形成维度互补：SaR 是前瞻性+连续分位数+感知集中度。典型场景：盘口深度看似充足但高度集中于 1-2 个做市商 → 现有检测不触发但 SaR 集中度调整给出高值 → 提前预警"脆弱纸糊结构"。A 股适配评估：数据可得（miniQMT 5 档盘口）但需重定义 HHI 为"挂单量集中度"（A 股无做市商席位标识）；清算机制差异（永续合约清算级联 vs A 股融资盘平仓潮，机制类似可迁移）。判定 Phase 2 储备（与 Hawkes 正交互补：Hawkes 预警事件聚集，SaR 预警结构脆弱，可叠加为双层前瞻预警）。重评条件：实盘 6 月盘口数据校准 HHI 阈值 + AUM 增长到自身交易影响盘口。补充 [arXiv:2608.03616](https://arxiv.org/abs/2608.03616) 强制平仓级联两类型分类实证支撑——7 起级联（2022-2025）揭示级联起始突变性 + 内生累积型（有前兆，Hawkes 适配）vs 外生冲击型（无前兆，SaR 适配脆弱结构）两类型分类，为"Hawkes + SaR 双层前瞻预警"提供理论框架 |
| 2026-08-10 | 1.0.7 | 补充 **§3.7.5 Latent Microstructure Regime Detection**（选项之外更好的答案算法）+ 四算法→五算法评估汇总表更新 | 持续改进：用户要求再次审查"选项之外更好的答案算法"+ 全网搜索 2026-08-08 最新研究。发现 [arXiv:2604.20949](https://arxiv.org/abs/2604.20949)（Hiremath & Hiremath, 2026-04）提出**隐含 build-up regime** 概念——在可见压力出现之前存在隐含恶化阶段，可用 trigger-based detector（MAX 聚合 + rising-edge + 自适应阈值）实现**正 lead-time**。核心洞察：OFI/spread/volatility 等标准信号**按构造是反应性的**（negative lead-time），零或负 lead-time 不是调参失败而是逻辑必然。触发通道：depth erosion + HMM 熵（>99% 首次触发）。仿真 lead-time +18.6 timesteps / 实数据 +38 秒，优于 CUSUM/BOCPD/HMM thresholding。与现有方法正交：Hawkes（时间）× SaR（结构）× Latent build-up（regime 转变）= 三层前瞻预警。与 35 号 §4.18 BOCD 关系：论文指出优于 BOCPD（BOCPD 检测变点已发生 vs latent build-up 检测前兆），但场景不同（35 号日级 kill switch vs 37 号盘中流动性秒级）不冲突。A 股适配：depth erosion 可用 miniQMT 5 档盘口近似，HMM 熵与 10 号 regime 检测器同类计算。判定 Phase 2 储备（数据粒度/计算复杂度/验证不足/MVP 已覆盖），重评条件：实盘 6 月盘口数据 + Hawkes lead-time 不足时 |
| 2026-08-10 | 1.0.8 | §3.7.1 Hawkes 自激励过程补充 **2026-08 最新研究更新**——3 项新证据强化储备地位：① A 股直接实证 arXiv:2512.08000（上证/深证/创业板 Hawkes 拟合，高活跃期延续趋势/低活跃期强轮动，同时解释轮动+踩踏）；② 图熵领先 7-12 天预警（An & Dai 2026 Entropy 28(8):887，2026-08-06，Von Neumann 图熵在回撤峰值前 7-12 交易日达极端值，从分钟级升级到日级提前预警）；③ 2026-07 A 股量化危机验证（CSI300 -5.81%/科创50 -17.46%，动量/小盘/反转同时失效，Hawkes 自激级联在中小盘无量跌停精确体现）。升级评估：图熵发现将 Hawkes 价值从"分钟级盘中预警"扩展到"日级提前预警"，可能上调 Phase 1 候选，但图熵需跨资产事件网络数据管道成本高，维持储备判定，重评条件扩展。frontmatter v1.0.7→v1.0.8 | 十三次审查全网搜索 2026-08-08~10 最新研究，发现 Hawkes 在 A 股有直接实证（arXiv:2512.08000）+ 图熵领先 7-12 天预警（An & Dai 2026-08-06）+ 2026-07 量化危机活体验证。3 项新证据强化 Hawkes 储备地位，尤其图熵发现将预警时间从分钟级升级到日级，可能上调 Phase 1，但跨资产事件网络数据管道成本高维持储备 |
| 2026-08-10 | 1.0.9 | §2.4 约束条件新增 **2026-07-31 交易所 LAN 通道关闭**交叉引用（十四次审查跨文档一致性补全）| 2026-07-31 上交所正式关闭机房内局域网交易行情线路统一切换广域网，核心硬约束：广域网线路双向时延不得低于 2ms（含存量+新增线路），物理链路层抹平微秒级抢跑优势（旧机房内网直连 0.13ms-10μs → 新广域网最低 2ms），首日成交从 2.56 万亿缩至 2.01 万亿（缩 5488 亿），纯超高频量化超额从 14% 回落至 3% 以内，量化行业从"拼网速"→"拼研究"时代。**对 G18 流动性的 3 项直接影响**：① 流动性收缩使大额强裁冲击成本上升——建议 33号 §3.2.3 的 `TWAP_LARGE_ORDER_THRESHOLD` 从总资产 5% 下调至 3-4%；② 高频做市商超额收益压缩退场盘口深度可能变薄——§3.1.2 Quoted Spread 阈值 0.5% 须在上线后 3 个月重新校准；③ §3.7 Hawkes"高活跃期延续趋势"判定需在新流动性结构下重新拟合基线。与 [00_index §3 G22⑨](00_index_trading_decision.md) + [40_execution_broker](40_execution_broker.md) + [33_budget_change_handler §3.2.3](33_budget_change_handler.md) 三方对齐。frontmatter v1.0.8→v1.0.9 | 十四次审查跨文档一致性发现 37 号缺 2026-07-31 LAN 通道关闭对流动性结构影响的交叉引用——33 号 v2.4.0 + 40 号 v1.3.0 + 00_index v2.15.0 均已记录此监管变化，37 号作为流动性协议文档却未提及，是交叉引用缺口。补齐后三方文档监管变化对齐完整 |
| 2026-08-10 | 1.0.10 | §3.7 新增 3 项 Hawkes 前沿评估（§3.7.6 ExsdHawkes + §3.7.7 Liquidation Cascade 三因子 + §3.7.8 Multiplex Network Hawkes）+ §4.7 Karimi 流动性-信贷联合破产边界 | §3.7 前沿算法评估从 5 算法扩展到 8 算法：① **§3.7.6 ExsdHawkes**（Kimura arXiv:2604.23961, Sophia University 2026-04）——放宽传统约束允许状态消失（涨跌停时卖方/买方状态消失），KKT 条件证明 MLE 可分离，唯一复现波动率签名图向上斜率，避免标准 Hawkes 爆炸分支比；② **§3.7.7 Liquidation Cascade 三因子**（Garcia Seuma arXiv:2608.03616, 2026-08-04）——7 次加密强平级联实证推翻临界级联假设（级联全程亚临界 λ≈0.1-0.2），severity=冲击×路径映射×流动性撤回非发散乘子，一阶相变替代临界相变框架，修正标准 Hawkes 分支比上升预警信号；③ **§3.7.8 Multiplex Network Hawkes**（Zelvyte&Griffin arXiv:2606.15755, University of Kent 2026-06）——多层网络 Hawkes 通道分离（行业相似性/偿付能力/盈利能力协变量），MCMC 后验识别系统性风险外向源，A 股迁移到股权质押/担保圈网络；④ **§4.7 Karimi 流动性-信贷联合破产边界**（arXiv:2607.17381, 2026-07）——HJB 方程求解联合边界，边界凸性（w₃>0）证明联合效应 > 个体效应之和，为 LEVEL_3 多信号联动提供数学基础，代理函数 B_surrogate=w₁λ+w₂d+w₃λd 允许实时监控。4 项均为 Phase 2-3 远期储备非施工算法缺失 | 用户要求再次审查+选项外更好算法+全网搜索 2026-08-08 最新研究+持续改进不停。后台搜索代理返回 2026-08 Hawkes/流动性级联/系统性风险最新研究，4 项均为"选项之外更好算法"——ExsdHawkes 修正标准 Hawkes 在涨跌停时的爆炸分支比，Liquidation Cascade 推翻 Hawkes 分支比上升预警假设，Multiplex Network Hawkes 从单资产扩展到跨机构网络，Karimi 为流动性-回撤联合检测提供数学基础。4 项均远期储备不直接采纳，维持 MVP 双条件 AND 检测 |
| 2026-08-10 | 1.0.11 | §3.7.7.1 Garcia Seuma 临界性预警异质性（Part I）+ §3.7.9 Weng A股羊群效应 Johnson S_U 变换 + §3.7.10 Zhou 平方根冲击操纵周期 三项 A 股专属/配套算法登记 | 二十四次审查全网搜索 2026-08-08 最新 A 股流动性/羊群效应/操纵周期研究，搜索 agent 返回 10 篇前沿论文筛除已登记/不适配，登记 3 项高价值发现：① §3.7.7.1 Garcia Seuma Part I（arXiv:2607.27070 2026-07-29）——§3.7.7 Liquidation Cascade Part II 的配套论文，39 配置系统测试 7 次级联发现无事件不变量（critical slowing down 在 5/7 事件出现但在 2 次突发新闻冲击缺失），唯一存活规律是吃单订单流方差压缩（p≈5×10⁻⁶ 但是群体级前兆非个体级警报），对 §3.7.7 三因子框架提供"冲击类型识别约束"——突发新闻冲击需降权路径映射因子；② §3.7.9 Weng A股羊群效应 Johnson S_U 变换（arXiv:2607.27063 2026-07-29）——A 股专属 agent-based 网络模型（异质高斯信念+有限速度信息扩散区分信息调整vs行为模仿）+ Johnson S_U 变换消除 CSAD/LSV 牛熊偏差，与 §3.7.1 Hawkes 正交（时间×截面双维度预警）+ 与 32号 §2.10.6 华泰金工递进（市场级vs风格级羊群）；③ §3.7.10 Zhou 平方根冲击操纵周期（arXiv:2607.05141 2026-07-06 Westlake）——A 股专属 ABM（±10%涨跌停+T+1+隐形分配），证明平方根冲击是内生操纵周期必要条件（线性冲击消除 Hopf 分岔），为 §3.7.x 系列提供统一 A 股内生操纵机制理论支撑，联动 [40号 §2.12](40_execution_broker.md) 平方根冲击系数作为操纵周期检测输入。3 项均储备非采纳：§3.7.7.1 是 §3.7.7 配套约束非独立模块，§3.7.9 待 §3.5 HBI/CSAD 上线验证牛熊偏差后引入，§3.7.10 是理论模型非工程算法。施工算法完整性结论：37 号施工流程算法闭环无缺失独立环节，3 项均为远期候选登记非施工算法缺失 |
| 2026-08-10 | 1.0.12 | §5.2 演进路径补 Residual Supply 被迫卖出压力信号（Phase 2+ 远期）+ §6 待裁定新增条目 | 二十六次审查全网搜索 2026-08-08 最新量化金融研究，后台 agent 返回 24 篇前沿论文，经覆盖检查 22/24 已登记，仅 2 项未登记（CHASM→55号 + Residual Supply→37号）。§5.2 第二阶段演进路径新增 Residual Supply 被迫卖出压力信号（[arXiv:2605.30672 2026-05-29](https://arxiv.org/abs/2605.30672) Wang "Residual Supply and the Price of Risk Absorption"）——连续时市场出清模型将残余供给价格分解为库存风险补偿+资本与调整楔子，被迫卖出压力预测当期价格下跌+随后 1-6 月正收益（65bp/月，217bp/6 月），**全市场吸收能力紧张时 premium 翻倍**。A 股适配：用公募赎回数据/北向净流出/融资余额下降近似 forced selling pressure，market-wide absorption capacity strain 作为 LEVEL_2 升级信号。Phase 2+ 远期因需 fund flow 数据接入，A 股数据源与论文 US 共同基金流不同须适配。§6 待裁定新增条目。施工算法完整性结论：37 号施工流程算法闭环无缺失独立环节，Residual Supply 是远期候选登记非施工算法缺失。 |
| 2026-08-10 | 1.0.13 | §3.7 新增 3 项 2026-07 SSRN 前沿算法（§3.7.11 LRISK 系统性流动性风险前瞻 + §3.7.12 欧洲 ML 流动性预测对比 + §3.7.13 AdjPIN 订单流信息/流动性分解）+ §5.2 演进路径同步 + §6 待裁定新增 3 条目 | 二十七次审查全网搜索 2026-08-08 最新流动性研究，验证登记 3 篇 2026-07 SSRN 论文（均经 WebSearch 确认真实存在）：① **§3.7.11 LRISK**（[SSRN 7110978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7110978) Jourde/Saillard/Van Dijk 2026-07-14 Banque de France/CREST，原稿 2026-01-05）——前瞻性系统性流动性风险度量，整合三大放大通道（流量共振 flow commonality + 组合重叠 portfolio similarity + 流动性螺旋 liquidity spirals），应用于 2011-2024 美国公司债基金验证 COVID-19 危机横截面收益预测 + **提前两个季度预测市场承压**。为 §3.7.x 系列补**系统级前瞻预警层**（微观 Hawkes/中观 Liquidation Cascade/宏观 LRISK 三层级）。A 股适配：公募赎回+北向净流出+融资余额 z-score 近似 flow commonality。Phase 2+ 远期因系统级指标非个股检测 + 与 Residual Supply 同需 fund flow 数据须先验证单资产级边际价值。② **§3.7.12 欧洲 ML 流动性预测对比**（[SSRN 7125463](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7125463) / CESifo WP 12829 Arakelia/Caporale/Gasparinatou/Karanasos 2026-07-16）——欧洲五大股指 2010-2026 Amihud 非流动性一步滚动预测，ARIMA/动态面板 vs RF/XGBoost/SVR。关键发现：流动性高度持续 + **动态面板不输 ML**（Diebold-Mariano 检验无显著差异）+ SHAP 三大驱动因子（成交活跃度+滞后流动性+市场不确定性）。为 §5.2 Phase 1.5 阈值校准提供"动态面板+三特征"轻量方案替代重 ML 栈，符合 MVP 简化原则。Phase 1.5 候选因 MVP 阶段 Amihud 静态阈值已够（流动性高持续）。③ **§3.7.13 AdjPIN 订单流信息/流动性分解**（[SSRN 7119388](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7119388) Park 2026-07-14，基于 Duarte&Young 2009 + Ghachem&Ersan 2025 ECM 估计）——将订单流分解为 AdjPIN 信息成分 + PSOS 流动性成分，Park 实证 ML 可预测性主要由流动性成分（PSOS）驱动。补全 §3.7.2 VPIN 拒绝后的 gap：区分"信息驱动价格移动"（跟随减仓）vs"纯流动性冲击"（等待恢复避免流动性枯竭时交易）优化 §3.3 LEVEL 响应。PSOS 对称买卖双增与 §3.1.1 sell_pressure 单边卖压正交。Phase 2 候选因 ECM 估计计算成本中等 + §3.7.2 已拒绝 PIN 家族须先验证 PSOS 增量价值。施工算法完整性结论：37 号施工流程算法闭环无缺失独立环节，3 项均为远期候选登记非施工算法缺失——LRISK 补系统级前瞻层、欧洲 ML 提供方法学参考、AdjPIN 补信息/流动性分离路径，维度互补不重叠。 |
| 2026-08-10 | 1.0.14 | §3.7 新增 2 项 2026-07 前沿算法（§3.7.14 Signed Order Flow Kyle λ 有向订单流价格冲击 + §3.7.15 流动性尾部风险与价格发现大单非信息场景） | 二十八次审查全网搜索 2026-08-08 最新流动性微结构研究，登记 2 篇高价值论文：① **§3.7.14 Signed Order Flow Kyle λ**（[arXiv:2607.01377](https://arxiv.org/abs/2607.01377) Aldridge 2026-07-01 "Liquidity Premium and Investment Horizons"）——从日度股票订单流估计 Kyle (1985) 价格冲击系数 λ̂ = Cov(ΔP, OF_signed)/Var(OF_signed)，CRSP 2020-2025 Fama-MacBeth 回归证明**有向订单流**强预测当期与未来一月收益（无向成交量波动则降低价格发现精度）。与 §3.1 Amihud ILLIQ（无向 \|r\|/V）形成维度互补：Kyle λ 恢复方向性信息含量，Amihud 仅流动性成本。A 股适配：Level-2 tick 数据 Lee-Ready 规则重建 signed OF，散户占比高噪声方差大尤其适配"噪声扩大 λ 降低价格发现"洞察。Phase 2 候选因需 tick 级买卖分类数据管道 + 与 §3.7.13 AdjPIN 重叠（两者都需 tick 级买卖分类，Phase 2 可同时引入）。② **§3.7.15 流动性尾部风险与价格发现**（[arXiv:2607.01198](https://arxiv.org/abs/2607.01198) Çetin/Lin/Livieri 2026-07-21 LSE "When large trades are not (automatically) news"）——重尾流动性需求下大额交易在更宽深度范围内仍"合理地非知情"，**压平价格冲击、减缓学习**。核心洞察"大单 ≠ 信息"颠覆 Easley-O'Hara 传统假设，对 A 股尤其重要（大单常源于机构调仓/融资盘平仓/公募赎回非信息驱动）。为 §3.3 LEVEL 响应提供理论支撑：重尾流动性需求下倾向"等待恢复"而非"跟随减仓"。与 §3.7.13 AdjPIN 互补（AdjPIN 从订单流分解角度区分，Çetin 从价格发现学习速度角度区分）。Phase 2 候选因理论性较强需不动点方程数值化 + 与 AdjPIN 功能重叠 AdjPIN 更工程化。施工算法完整性结论：37 号施工流程算法闭环无缺失独立环节，2 项均为远期候选登记非施工算法缺失——Kyle λ 补方向性价格冲击维度、Çetin 补大单非信息理论支撑，与 §3.7.13 AdjPIN 形成"订单流分解+价格冲击+价格发现学习"三维信息/流动性分离框架 |
| 2026-08-10 | 1.0.15 | §3.2a 新增 IPO 流动性抽离预警 | final_report_0724 交叉对照发现 37 号无 IPO 驱动的流动性抽离预警——长鑫科技 688825 科创板上市募资 579-666 亿可能吸金 500 亿+，此类事件型流动性抽离无法被 Amihud/spread/sell_pressure 事后检测捕获。新增 §3.2a 前瞻性 IPO 流动性抽离预警算法（drain_ratio = 未来5日IPO募资总额/全市场日均成交额，4 级 drain_level→position_cap_adjustment），与 26 号 §2.5a IPO 虹吸效应算法联动（26 号管 alpha 方向+仓位策略，37 号管流动性检测+仓位上限节流）。与 §3.2 Amihud 的事后检测正交：§3.2a 事前预警（IPO 上市日前已知），§3.2 事后检测（上市后实际恶化） |
| 2026-08-10 | 1.0.16 | §3.6 `check_recovery` 签名对齐修复——定义与调用点签名不一致 + 真值检查 bug | 伪代码完整性审计发现 §3.6 恢复算法存在两处缺陷：① **签名不一致**——`check_recovery` 定义用硬编码阈值 positional 参数 `(current_state, signals, spread, sell_pressure, time_since_trigger, recovery_window=5)`，但 §3.6 编排伪代码 `intraday_liquidity_loop` 调用点用参数化阈值关键字参数 `(current_spread, current_sell_pressure, trigger_threshold_spread, recovery_threshold_spread, trigger_threshold_pressure, recovery_threshold_pressure, min_hold_minutes, elapsed)`，两者完全不匹配无法调用。统一为参数化签名（阈值/最短持续时间作为参数注入，支持实盘校准外部调整，对齐 §6 "待校准"要求，消除两处真相源），新增 `current_level`/`active_signals` 参数。② **真值检查 bug**——`check_recovery` 返回 `target_level`（int 0/1/2 或 None），但调用点用 `if recovered:` 真值检查，当 target_level=0（LEVEL_1→正常态）时为 falsy，**会跳过 LEVEL_1 恢复到正常态**。改为 `if recovered is not None:` 并在 docstring 显式标注警告。调用点补 `active_signals` 计数（§3.1 双条件计数 sell_pressure 超阈值 + spread 超阈值，范围 0-2）+ `recovery_state.exit_crisis(target_level=recovered)` 传递目标级别。 |
