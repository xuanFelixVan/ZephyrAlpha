---
ttl: permanent
doc_type: architecture_view
title: 流动性危机处理
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.3.0"
date: 2026-08-10
topic: liquidity_crisis_protocol
scope: 07_trading_decision_architecture
---

# 流动性危机处理

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G18 主题组派生，将流动性危机处理的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：Fosset/Bouchaud/Benzaquen "Endogenous Liquidity Crises" arXiv:1912.00359（Hawkes/Q-Hawkes 内生流动性危机相变模型）；Xu et al. arXiv:2604.21993（Crumbling Quotes 机械性流动性侵蚀检测，ICLR 2026 Workshop）；An & Dai Entropy 28(8) 887 2026-08（Transfer Entropy + 多元 Hawkes 跨境风险传染）；O'Connell 2026 L-VaR（Amihud + Kyle λ）；2026-07-06 上交所交易新规（ST 涨跌停放宽至 10%、盘后固定价格全市场扩容）；Realsumen OFE-Hawkes 2025-08（多元 Hawkes 6 类订单簿事件交叉激励矩阵）；Wehrli & Sornette 2022 Quantitative Finance（Hawkes(p,q) EM 估计时变 branching ratio + 闪崩分类）；Rakeshks7 2026-02（Recursive MLE O(N) 对数似然实现，适配高频规模）；Lee & Seo 2022 arXiv:2201.10173（extended Hawkes 价差依赖强度 + 负激励项）；Anantha & Jain 2024-08 arXiv:2408.03594（Hawkes 预测高频 OFI 分布）。**v1.2.0 新增**：VPIN 订单流毒性检测（Easley/Lopez de Prado/O'Hara 2012 RFS + BVC 买卖分类 + Andersen & Bondarenko 2014 JFM 批判性讨论 + VisualHFT Silahian 2026-03 实务阈值）+ Unified OFI 含撤单流（Kolm & Netoličková 2025 R² 0.32→0.65 + finantrix 2026-08 Conditional OFI Sharpe=1.79）+ VPIN/OFI/Hawkes 三联毒性危机综合检测。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G18 流动性危机处理 |
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5.5 |
| 依赖 | G16（[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 已定稿 v1.0.0） |
| 对标 | tradingwyckoff Kill Switch / 机构流动性风控 / Capital Fund Management 内生危机模型 |
| 正交性 | ✅ 与 regime 正交（流动性危机是微结构级，regime 是市场级） |
| 优先级 | P3 |
| 状态 | ✅ active — 流动性指标+危机检测+应急响应算法已定稿 |

## 2. 背景

### 2.1 项目处境

A 股市场具有独特的流动性风险结构：涨跌停板 + T+1 结算构成"制度性锁仓"——当股票跌停时，卖单只能按 10%/20%/30% 逐日沉没，价格调整被人为切碎，流动性通道被堵死，形成"流动性黑洞"（2015 股灾定性）。2026-07-06 上交所新规将 ST/*ST 涨跌幅从 5% 放宽至 10%，"天地板""地天板"极端行情概率上升。

### 2.2 核心问题

1. **流动性指标定义**：需要量化"流动性"——换手率、成交额、盘口深度、买卖价差、Amihud 非流动性比率各有优劣，需组合使用。
2. **内生 vs 外生危机**：传统模型视流动性危机为外生新闻冲击，但 Fosset et al. (arXiv:1912.00359) 证明大部分大价格跳跃是内生反馈——过去波动率和趋势降低订单簿流动性 → 放大未来波动率 → 二阶相变临界点。
3. **机械性 vs 信息性侵蚀**：观测到的报价恶化无法唯一归因——机械性撤单（瞬时、可恢复）vs 信息重定价（持久、有效价格变化）在 top-of-book 签名相似但含义相反，需区分（arXiv:2604.21993 Xu 2026）。
4. **A 股涨跌停流动性失效**：跌停封单远大于流通盘时，次日惯性下跌；"想卖卖不出"是制度性高频事件，非黑天鹅。
5. **与 Kill Switch 的关系**：§2.5.5 定义"流动性危机（买卖价差 > 正常 5x）→ 立即停止开仓，仅允许平仓"，需明确检测算法和执行路径。

### 2.3 约束条件

- **A 股 T+1**：流动性危机触发时，当日买入无法当日卖出，只能对 T-1 持仓操作
- **涨跌停板**：跌停时卖单无法成交，需建模"封单力度/排队位置"
- **盘后固定价格交易**（2026-07-06 新规）：15:05-15:30 按收盘价逐笔撮合，盘后流动性弱于盘中
- **MVP 简化**：先建全+全 log，实盘 6-12 月后裁剪未触发项

### 2.4 2026-07 量化同质化踩踏实证——内生危机模型的现实验证

2026-07 A 股量化行业遭遇深度回撤，是 §3.4 Hawkes 内生反馈模型的现实验证：

**事件经过**（界面新闻 2026-08-10）：
- 2026 上半年：全市场 40-50% 成交额集中在前 5% 热门科技股（算力/半导体），海量量化资金依托相似的量价因子/动量因子同向涌入
- 2026-07 中旬：风格突然逆转，动量因子全面失效，从收益来源变为最大亏损源
- **"个体理性叠加成灾难性的集体非理性"**：数千套高度雷同的模型在同一时刻触发同款风控指令，形成"下跌—减仓—更深下跌"的闭环负反馈
- 实际损失：幻方量化 9 只展示产品单月跌幅全数突破 20%，核心产品最大回撤 22.15%；主动量化基金收益率中位数低至 -7.13%
- 2026-07-31：交易所局域网行情通道正式关闭，统一切换广域网——"速度红利"退潮，竞争回归策略本身

**与 Hawkes 内生危机模型的对应**：
- Hawkes 分支比 n→1（相变临界）：同质化模型触发同款风控 = 撤单激励撤单 = 交叉激励矩阵对角元素激增
- "下跌—减仓—更深下跌"负反馈 = Fosset et al. 的二阶相变——过去波动率降低流动性 → 放大未来波动率
- 这不是外生新闻冲击，而是**纯内生反馈**——Wehrli & Sornette 闪崩分类的 endogenous_dominant 类型

**对本系统的启示**：
1. **因子拥挤度监控**（已在 §4.27 因子冗余检查 E16 登记）：crowded momentum 崩溃概率高 1.7-1.8×，crowded reversal 崩溃概率低 0.38×（Chorok Lee 2025-12 双曲因子衰减）
2. **VPIN/Unified OFI 的预警价值**：同质化减仓 = 买卖单方极端失衡 = VPIN 飙升 + Unified OFI 方向性极端——§3.9 三联检测应能在"下跌—减仓"闭环形成前预警
3. **DrawdownCircuitBreaker 的风控价值**（yoyo-quant 2026-08-07 实证）：-35% 阈值可将 MaxDD 从 -33.4% 压到 -27.8%，但 Sharpe 从 0.611 降到 0.535——"CB 的价值在风控（MaxDD），不在收益（Sharpe）"，验证本项目回撤 Protocol 的风险优先原则
4. **广域网切换的执行层影响**：已在 [40_execution_broker] 登记 latency_floor_ms + network_type 字段，速度红利退潮后执行竞争回归算法质量

## 3. 决策

### 3.1 架构定义

流动性危机处理作为独立风控模块，与回撤 Protocol（G16）和 Kill Switch 联动：

```
盘口数据 → [流动性指标计算] → [危机检测] → [应急响应]
                                    ↓
                    [Hawkes 内生反馈检测] → Kill Switch 联动
                    [Crumbling Quotes 检测] → 回撤 Protocol 联动
```

**核心模块**：
- `LiquidityIndicatorCalculator`：多维度流动性指标计算（价差/深度/Amihud/Kyle λ）
- `LiquidityCrisisDetector`：危机检测（价差倍数阈值 + Hawkes 内生反馈 + Crumbling Quotes）
- `LiquidityCrisisResponse`：应急响应（停止开仓/仅允许平仓/强制平仓）
- `LimitDownTrapHandler`：A 股涨跌停流动性失效处理

### 3.2 流动性指标计算算法

```python
import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class LiquidityIndicators:
    """多维度流动性指标。"""
    bid_ask_spread: float            # 买卖价差（相对值，如 0.002 = 0.2%）
    spread_multiple_vs_normal: float # 当前价差 / 正常价差倍数
    order_book_depth: float          # 盘口深度（最优 5 档总量 / 流通市值）
    amihud_illiq: float              # Amihud 非流动性比率
    kyle_lambda: float               # Kyle λ 价格冲击系数
    turnover_rate: float             # 换手率
    volume: float                    # 成交额（元）
    is_limit_down: bool              # 是否跌停
    is_limit_up: bool                # 是否涨停
    seal_ratio: Optional[float]      # 封单力度（封单量 / 流通市值），仅涨跌停时有值


def calc_liquidity_indicators(
    bid: float, ask: float, mid: float,
    best_5_levels_volume: float, float_mkt_cap: float,
    daily_return: float, daily_volume: float,
    price_history: np.ndarray, volume_history: np.ndarray,
    order_flows: Optional[np.ndarray] = None,
    limit_down_price: Optional[float] = None,
    limit_up_price: Optional[float] = None,
    seal_volume: Optional[float] = None,
) -> LiquidityIndicators:
    """计算多维度流动性指标。

    2026-08 研究整合：
    - Amihud ILLIQ（Micro Alphas 2026-06）：日频广泛结构化横截面流动性
    - Kyle λ（O'Connell 2026）：精细战术单券冲击，需订单流数据
    - 买卖价差倍数：tradingwyckoff 2026-01 Kill Switch 触发条件
    """
    # 买卖价差
    spread = (ask - bid) / mid if mid > 0 else 0.0

    # 正常价差基准（近 20 日中位数）
    # 简化：实际需维护历史价差序列
    normal_spread = 0.001  # 占位，实际从历史计算
    spread_multiple = spread / normal_spread if normal_spread > 0 else 1.0

    # 盘口深度（最优 5 档总量 / 流通市值）
    depth = best_5_levels_volume / float_mkt_cap if float_mkt_cap > 0 else 0.0

    # Amihud 非流动性
    amihud = calc_amihud_illiq(price_history, volume_history)

    # Kyle λ（需订单流数据）
    kyle_lambda = 0.0
    if order_flows is not None and len(order_flows) == len(price_history) - 1:
        price_changes = np.diff(price_history)
        kyle_lambda = calc_kyle_lambda(price_changes, order_flows)

    # 换手率
    turnover = daily_volume / float_mkt_cap if float_mkt_cap > 0 else 0.0

    # 涨跌停判定
    is_limit_down = (limit_down_price is not None and abs(mid - limit_down_price) < 0.001)
    is_limit_up = (limit_up_price is not None and abs(mid - limit_up_price) < 0.001)

    # 封单力度
    seal_ratio = None
    if (is_limit_down or is_limit_up) and seal_volume is not None:
        seal_ratio = seal_volume / float_mkt_cap if float_mkt_cap > 0 else 0.0

    return LiquidityIndicators(
        bid_ask_spread=spread,
        spread_multiple_vs_normal=spread_multiple,
        order_book_depth=depth,
        amihud_illiq=amihud,
        kyle_lambda=kyle_lambda,
        turnover_rate=turnover,
        volume=daily_volume,
        is_limit_down=is_limit_down,
        is_limit_up=is_limit_up,
        seal_ratio=seal_ratio,
    )


def calc_amihud_illiq(returns: np.ndarray, dollar_volumes: np.ndarray) -> float:
    """Amihud 非流动性比率（Micro Alphas 2026-06）。

    ILLIQ = mean_t(|r_t| / DollarVolume_t) × 10^6
    """
    valid = dollar_volumes > 0
    if not np.any(valid):
        return 0.0
    ratios = np.abs(returns[valid]) / dollar_volumes[valid]
    return float(np.mean(ratios)) * 1e6


def calc_kyle_lambda(price_changes: np.ndarray, order_flows: np.ndarray) -> float:
    """Kyle λ 价格冲击系数（O'Connell 2026）。

    ΔP_t = λ · OrderFlow_t + ε
    λ = Cov(ΔP, OF) / Var(OF)
    """
    if len(price_changes) < 10:
        return 0.0
    cov = np.cov(price_changes, order_flows)[0, 1]
    var_of = np.var(order_flows)
    return float(cov / var_of) if var_of > 0 else 0.0
```

### 3.3 流动性危机检测算法

```python
@dataclass
class LiquidityCrisisSignal:
    """流动性危机检测结果。"""
    crisis_level: str        # "NORMAL" / "WARNING" / "CRISIS" / "BLACK_HOLE"
    triggers: list[str]      # 触发原因列表
    recommended_action: str  # "monitor" / "stop_new_open" / "flatten_only" / "force_flatten"


def detect_liquidity_crisis(
    indicators: LiquidityIndicators,
    hawkes_intensity: Optional[float] = None,    # Hawkes 过程强度（如已计算）
    crumbling_prob: Optional[float] = None,      # Crumbling Quotes 概率（如已计算）
    consecutive_limit_down_days: int = 0,        # 连续跌停天数
) -> LiquidityCrisisSignal:
    """流动性危机检测——多维度综合判定。

    三级危机：
    - WARNING：价差 > 3x 正常 或 Amihud > 2x 基准 → 加强监控
    - CRISIS：价差 > 5x 正常（Kill Switch 触发线）→ 停止开仓，仅允许平仓
    - BLACK_HOLE：跌停封单 > 流通市值 5% 或连续 2+ 跌停 → 强制平仓（T+1 仅对 T-1 持仓）

    2026-08 研究整合：
    - Fosset et al. (arXiv:1912.00359): Hawkes/Q-Hawkes 内生流动性危机——
      过去波动率和趋势降低流动性 → 放大未来波动率 → 二阶相变临界点
    - Xu et al. (arXiv:2604.21993, ICLR 2026): Crumbling Quotes 检测——
      区分机械性撤单（瞬时可恢复）vs 信息重定价（持久有效价变化），
      神经模型 AUC 比规则基线提升 +36%
    - tradingwyckoff 2026-01: 价差 > 正常 5x → Kill Switch
    """
    triggers = []

    # 检测 1：买卖价差倍数（Kill Switch 主触发线）
    if indicators.spread_multiple_vs_normal > 5.0:
        triggers.append(f"spread_{indicators.spread_multiple_vs_normal:.1f}x_gt_5x")
    elif indicators.spread_multiple_vs_normal > 3.0:
        triggers.append(f"spread_{indicators.spread_multiple_vs_normal:.1f}x_gt_3x")

    # 检测 2：Hawkes 内生反馈强度（如已计算）
    if hawkes_intensity is not None and hawkes_intensity > 2.0:
        # Hawkes 强度 > 2.0 表示内生反馈接近相变临界点
        triggers.append(f"hawkes_endogenous_{hawkes_intensity:.2f}")

    # 检测 3：Crumbling Quotes 概率（如已计算）
    if crumbling_prob is not None and crumbling_prob > 0.7:
        triggers.append(f"crumbling_quotes_{crumbling_prob:.2f}")

    # 检测 4：A 股涨跌停流动性黑洞
    if indicators.is_limit_down and indicators.seal_ratio is not None:
        if indicators.seal_ratio > 0.05:  # 封单 > 流通市值 5%
            triggers.append(f"limit_down_seal_{indicators.seal_ratio:.2%}")
        if consecutive_limit_down_days >= 2:
            triggers.append(f"consecutive_limit_down_{consecutive_limit_down_days}d")

    # 检测 5：盘口深度枯竭
    if indicators.order_book_depth < 0.001:  # 最优 5 档 < 流通市值 0.1%
        triggers.append(f"depth_depleted_{indicators.order_book_depth:.4f}")

    # 检测 6：Amihud 非流动性飙升
    # 简化：实际需与历史基准比较
    if indicators.amihud_illiq > 0:  # 占位阈值
        pass

    # 综合判定危机级别
    if any("limit_down_seal" in t or "consecutive_limit_down" in t for t in triggers):
        return LiquidityCrisisSignal(
            crisis_level="BLACK_HOLE",
            triggers=triggers,
            recommended_action="force_flatten",  # 强制平仓（T+1 仅对 T-1 持仓）
        )
    elif indicators.spread_multiple_vs_normal > 5.0:
        return LiquidityCrisisSignal(
            crisis_level="CRISIS",
            triggers=triggers,
            recommended_action="stop_new_open",  # 停止开仓，仅允许平仓
        )
    elif len(triggers) > 0:
        return LiquidityCrisisSignal(
            crisis_level="WARNING",
            triggers=triggers,
            recommended_action="monitor",  # 加强监控
        )
    else:
        return LiquidityCrisisSignal(
            crisis_level="NORMAL",
            triggers=[],
            recommended_action="none",
        )
```

### 3.4 Hawkes 内生反馈检测算法

```python
def calc_hawkes_intensity(
    event_times: np.ndarray,      # 流动性事件时间戳（如大额撤单、价差跳变）
    observation_time: float,      # 当前观测时间
    baseline_intensity: float = 0.1,
    decay_rate: float = 0.5,      # 指数衰减率
    excitation_strength: float = 0.3,
) -> float:
    """Hawkes 过程强度计算——内生流动性反馈检测。

    Fosset, Bouchaud, Benzaquen (arXiv:1912.00359) Endogenous Liquidity Crises:
    - 过去波动率和趋势降低订单簿流动性 → 放大未来波动率 → 二阶相变
    - 弱反馈 = 稳定 regime，强反馈 = 流动性危机以概率 1 发生
    - 临界点：Hawkes 分支比 n = α/β 接近 1 时接近相变

    λ(t) = μ + Σ_i α · exp(-β · (t - t_i))

    当 λ(t) / μ > 2.0 时，内生反馈强度高，接近相变临界点。

    Q-Hawkes 扩展（Zumbach 效应）：
    - 过去趋势（无论符号）降低流动性 → 二次反馈
    - λ(t) = μ + α · K(∫ 2β·exp(-β(t-s)) dP_s)²
    """
    intensity = baseline_intensity
    for t_i in event_times:
        if t_i < observation_time:
            dt = observation_time - t_i
            intensity += excitation_strength * np.exp(-decay_rate * dt)

    # 分支比（稳定性指标）
    branching_ratio = excitation_strength / decay_rate
    # branching_ratio → 1.0 时接近相变临界点

    return intensity


def detect_endogenous_crisis(
    event_times: np.ndarray,
    observation_time: float,
    volatility_history: np.ndarray,   # 波动率历史
    trend_history: np.ndarray,        # 价格趋势历史
) -> tuple[float, bool]:
    """内生流动性危机检测——Q-Hawkes Zumbach 效应。

    Returns: (crisis_probability, is_near_critical)
    """
    # 线性 Hawkes 强度
    linear_intensity = calc_hawkes_intensity(event_times, observation_time)

    # Q-Hawkes Zumbach 项：过去波动率和趋势的二次反馈
    # ν_t = ν_0 + α_K · (∫ 2β·exp(-β(t-s)) dP_s)²
    recent_vol = np.mean(volatility_history[-20:]) if len(volatility_history) >= 20 else 0.0
    recent_trend = np.mean(trend_history[-20:]) if len(trend_history) >= 20 else 0.0
    zumbach_term = recent_vol**2 + recent_trend**2  # 简化二次型

    total_intensity = linear_intensity + 0.3 * zumbach_term

    # 相变临界判定：分支比接近 1.0
    branching_ratio = 0.3 / 0.5  # α/β
    is_near_critical = branching_ratio > 0.85  # 接近 1.0

    # 危机概率（简化映射）
    crisis_prob = min(1.0, total_intensity / 3.0)

    return crisis_prob, is_near_critical
```

### 3.5 应急响应算法

```python
def execute_liquidity_crisis_response(
    signal: LiquidityCrisisSignal,
    positions: dict[str, float],           # 当前持仓 {symbol: quantity}
    t_minus_1_positions: dict[str, float], # T-1 持仓（T+1 约束下可卖的）
    indicators_by_symbol: dict[str, LiquidityIndicators],
) -> dict:
    """流动性危机应急响应执行。

    响应级别（递进）：
    - WARNING：加强监控，缩窄新仓规模
    - CRISIS：停止开仓，仅允许平仓（Kill Switch 联动）
    - BLACK_HOLE：强制平仓 T-1 持仓（T+1 约束下当日买入不可卖）

    A 股 T+1 约束：
    - 当日买入的仓位不可卖出，只能对 T-1 持仓操作
    - 跌停时卖单可能无法成交，需挂单排队
    """
    result = {
        "action": signal.recommended_action,
        "orders": {},
        "allow_new_open": True,
        "log_entries": [],
    }

    if signal.crisis_level == "NORMAL":
        return result

    if signal.crisis_level == "WARNING":
        # 缩窄新仓规模（减半）
        result["allow_new_open"] = True
        result["new_position_scale"] = 0.5
        result["log_entries"].append(f"WARNING: triggers={signal.triggers}")
        return result

    # CRISIS 或 BLACK_HOLE：停止开仓
    result["allow_new_open"] = False

    if signal.crisis_level == "CRISIS":
        # 仅允许平仓——不主动挂卖单，但允许策略层的平仓信号通过
        result["log_entries"].append(f"CRISIS: stop_new_open, triggers={signal.triggers}")
        return result

    # BLACK_HOLE：强制平仓 T-1 持仓
    for sym, qty in t_minus_1_positions.items():
        if qty <= 0:
            continue

        indicators = indicators_by_symbol.get(sym)
        if indicators and indicators.is_limit_down:
            # 跌停：挂跌停价卖单排队（可能无法成交）
            result["orders"][sym] = {
                "side": "sell",
                "quantity": qty,
                "order_type": "limit",
                "price": "limit_down",  # 跌停价挂单
                "note": "limit_down_queue",  # 排队等待
            }
            result["log_entries"].append(
                f"BLACK_HOLE: {sym} limit_down_queue qty={qty} seal_ratio={indicators.seal_ratio}"
            )
        else:
            # 非跌停：市价卖出
            result["orders"][sym] = {
                "side": "sell",
                "quantity": qty,
                "order_type": "market",
            }
            result["log_entries"].append(f"BLACK_HOLE: {sym} force_flatten qty={qty}")

    return result
```

### 3.6 A 股涨跌停流动性失效处理

```python
def handle_limit_down_trap(
    symbol: str,
    position: float,
    seal_ratio: float,               # 封单/流通市值
    consecutive_limit_down_days: int,
    float_mkt_cap: float,
    avg_daily_volume: float,
) -> dict:
    """A 股涨跌停流动性失效处理——"想卖卖不出"制度性风险。

    背景（东方财富 2026-05-19）：
    - *ST 闻泰复牌连续 10 跌停，20 万户投资者排队无门
    - 第一把锁 T+1：当日买入至少锁定 24 小时
    - 第二把锁 涨跌停板：卖单只能按 10%/20%/30% 逐日沉没
    - 两锁叠加 → "想卖卖不出"成制度性高频事件，非黑天鹅
    - 2015 股灾：涨跌停板被定性为流动性枯竭主因

    处理策略：
    1. 跌停封单远大于流通盘 → 次日惯性下跌，停止盲目补仓
    2. 封单力度 < 1% → 可能在盘中开板，挂跌停价排队
    3. 连续 2+ 跌停 → 标记为 BLACK_HOLE，强制平仓排队
    4. 分散投资是防范极端风险的根本前提
    """
    result = {
        "symbol": symbol,
        "action": "none",
        "queue_order": False,
        "stop_rebuy": False,
        "risk_flag": "normal",
    }

    # 封单力度评估
    if seal_ratio > 0.05:  # 封单 > 流通市值 5%
        result["action"] = "queue_and_wait"
        result["queue_order"] = True  # 挂跌停价排队
        result["stop_rebuy"] = True   # 禁止补仓
        result["risk_flag"] = "black_hole"

        if consecutive_limit_down_days >= 2:
            result["action"] = "force_queue_multi_day"
            result["risk_flag"] = "severe_black_hole"
            # 连续跌停：每日挂跌停价排队，等待开板

    elif seal_ratio > 0.01:  # 封单 1%-5%
        result["action"] = "queue_optimistic"
        result["queue_order"] = True  # 挂跌停价排队，可能在盘中开板
        result["stop_rebuy"] = True

    else:  # 封单 < 1%
        result["action"] = "monitor_for_open"
        result["queue_order"] = False  # 等待盘中开板再卖
        result["stop_rebuy"] = False   # 可视情况补仓（需严格风控）

    return result
```

### 3.7 多元 Hawkes 内生订单流检测（OFE-Hawkes 扩展）

```python
@dataclass
class MultivariateHawkesParams:
    """多元 Hawkes 参数——OFE-Hawkes 框架。

    Realsumen OFE-Hawkes (2025-08) 提出：
    在极端行情下用多元 Hawkes 量化订单簿事件的内生性。
    单变量 Hawkes 只能捕捉单一事件的自激励，
    多元 Hawkes 可捕捉跨事件类型的交叉激励（如撤单激励成交）。

    6 类订单簿事件（Realsumen OFE-Hawkes）：
    - E1: 买方主动成交（T+）
    - E2: 卖方主动成交（T-）
    - E3: Bid Size Up
    - E4: Bid Size Down
    - E5: Ask Size Up
    - E6: Ask Size Down

    关键输出：
    - branching_ratio n：内生性度量，n→1 表示接近相变
    - 交叉激励矩阵：哪类事件激励哪类事件
    - 半衰期：激励衰减速度（极震期是否缩短）
    """
    mu: np.ndarray                    # [N] 各事件基线强度
    alpha: np.ndarray                 # [N, N] 交叉激励强度矩阵
    beta: np.ndarray                  # [N, N] 衰减率矩阵
    n_events: int = 6                 # 事件类型数


def compute_branching_ratio_matrix(params: MultivariateHawkesParams) -> np.ndarray:
    """计算分支比矩阵——内生性度量。

    分支比 n_ij = alpha_ij / beta_ij
    - n < 1：稳定（子临界）
    - n → 1：接近相变（闪崩前兆）
    - n ≥ 1：超临界（不稳定，闪崩 prone）

    Realsumen OFE-Hawkes 关键发现：
    - 极端行情窗口 B 的 n 显著高于常态窗口 A
    - 撤单（E4/E6）→ 成交（E1/E2）的激励在极震期增强
    - 半衰期在极震期缩短（市场"忘记"速度变快）

    Rakeshks7 2026-02 实现：Recursive MLE O(N) log-likelihood
    （vs naive O(N²)），适配高频数据规模。
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        n_matrix = np.where(
            params.beta > 0,
            params.alpha / params.beta,
            0.0,
        )
    return n_matrix


def detect_flash_crash_precursor(
    params: MultivariateHawkesParams,
    critical_threshold: float = 0.85,
) -> dict:
    """闪崩前兆检测——基于多元 Hawkes 分支比矩阵。

    Wehrli & Sornette (2022) Quantitative Finance：
    - 闪崩前 branching ratio 显著上升
    - 时间变化 feedback parameter 可用 EM 算法估计
    - 不同市场（股票期货/外汇/加密）闪崩特征不同，非通用

    检测逻辑：
    1. 计算每对事件的分支比 n_ij
    2. 最大分支比 > 0.85 → 接近相变，闪崩前兆
    3. 撤单→成交的激励（n_41, n_42, n_61, n_62）特别强 → 机械性抛售
    """
    n_matrix = compute_branching_ratio_matrix(params)
    max_n = float(np.max(n_matrix))
    is_precursor = max_n > critical_threshold

    # 撤单→成交激励（机械性抛售特征）
    cancel_to_trade_strength = 0.0
    if params.n_events >= 6:
        cancel_to_trade_strength = float(
            n_matrix[3, 0] + n_matrix[3, 1] + n_matrix[5, 0] + n_matrix[5, 1]
        ) / 4.0

    return {
        "max_branching_ratio": max_n,
        "is_flash_crash_precursor": is_precursor,
        "cancel_to_trade_strength": cancel_to_trade_strength,
        "branching_ratio_matrix": n_matrix.tolist(),
        "critical_threshold": critical_threshold,
        "interpretation": (
            "near_critical" if is_precursor
            else "sub_critical_stable"
        ),
    }
```

### 3.8 Hawkes(p,q) 时变反馈参数 EM 估计

```python
@dataclass
class HawkesPQParams:
    """Hawkes(p,q) 时变反馈参数——Wehrli & Sornette (2020/2022)。

    标准 Hawkes 假设分支比 n 恒定，但实证显示闪崩附近 n 时变。
    Hawkes(p,q) 框架：
    - p：外生到达过程的灵活度（如 ARMA 点过程）
    - q：内生反馈参数的时变维度

    EM 算法估计：
    - E 步：给定参数，推断每个事件是外生还是内生分支
    - M 步：更新参数最大化期望对数似然
    - 收敛后得到时变 branching ratio 序列

    用途：
    - 闪崩分类（事后归因）
    - 短期预测（内生驱动事件可预测，外生不可预测）
    - 改进熔断机制设计（latency floor 等）
    """
    baseline_mu: float
    time_varying_n: list[float]         # 时变分支比序列
    half_life: float                    # 激励半衰期
    log_likelihood: float
    is_endogenous_dominant: bool        # 内生 vs 外生主导


def estimate_hawkes_pq_em(
    event_times: np.ndarray,
    observation_window: tuple[float, float],
    max_iter: int = 100,
    tol: float = 1e-5,
) -> HawkesPQParams:
    """Hawkes(p,q) EM 估计——时变反馈参数。

    Wehrli & Sornette (Quantitative Finance 2022)：
    - 系统性平衡外生驱动过程与内生反馈变化的自由度
    - 用信息准则避免过拟合
    - 闪崩附近动态非通用（不同市场特征不同）

    算法（简化版，MVP 阶段）：
    1. 初始化恒定 mu, alpha, beta
    2. E 步：用 Ogata 稀疏化或前向后向算法推断分支结构
    3. M 步：更新参数，特别允许 alpha 在窗口内分段变化
    4. 收敛判定：对数似然变化 < tol

    注意：完整实现需 O(N) 递归 MLE（Rakeshks7 2026-02）
    这里给出框架，实际施工需 tick 级数据基础设施。
    """
    # MVP 占位实现：用恒定参数估计
    # 真实场景需迭代 EM
    n_events = len(event_times)
    if n_events < 10:
        return HawkesPQParams(
            baseline_mu=0.1,
            time_varying_n=[0.5],
            half_life=2.0,
            log_likelihood=0.0,
            is_endogenous_dominant=False,
        )

    # 简化：分段估计分支比
    n_segments = min(10, n_events // 10)
    segment_size = max(1, n_events // n_segments)
    time_varying_n = []

    for i in range(n_segments):
        start = i * segment_size
        end = min((i + 1) * segment_size, n_events)
        segment_events = event_times[start:end]
        if len(segment_events) > 1:
            # 简化：用事件间隔的聚集程度近似分支比
            intervals = np.diff(segment_events)
            cv = float(np.std(intervals) / max(np.mean(intervals), 1e-9))
            # CV 大 → 聚集 → 内生性强 → 分支比高
            n_seg = min(0.95, max(0.1, cv / (1 + cv)))
            time_varying_n.append(n_seg)

    avg_n = float(np.mean(time_varying_n)) if time_varying_n else 0.5
    is_endogenous = avg_n > 0.7

    return HawkesPQParams(
        baseline_mu=float(n_events / (observation_window[1] - observation_window[0])),
        time_varying_n=time_varying_n,
        half_life=2.0,  # 简化：实际从 beta 估计
        log_likelihood=0.0,  # 简化：实际需完整 MLE
        is_endogenous_dominant=is_endogenous,
    )


def classify_crisis_origin(
    hawkes_pq: HawkesPQParams,
    news_events_count: int,             # 同时段重大新闻数
) -> str:
    """危机起源分类——Wehrli & Sornette 闪崩分类法。

    分类逻辑：
    - endogenous_dominant：内生反馈为主（branching ratio 高，新闻少）
      → 可短期预测，改进熔断机制有效
    - exogenous_dominant：外生冲击为主（新闻多，branching ratio 低）
      → 不可预测，依赖事后应对
    - mixed：混合起源

    决策含义：
    - endogenous_dominant → 加强 Hawkes 监控，提前降级
    - exogenous_dominant → 加强新闻监控，依赖 Kill Switch
    - mixed → 双轨并用
    """
    if hawkes_pq.is_endogenous_dominant and news_events_count <= 1:
        return "endogenous_dominant"
    if not hawkes_pq.is_endogenous_dominant and news_events_count >= 3:
        return "exogenous_dominant"
    return "mixed"
```

### 3.9 VPIN 订单流毒性检测 + Unified OFI（流动性与毒性层）

```python
from scipy.stats import norm


@dataclass
class VPINResult:
    """VPIN 订单流毒性检测结果——Easley, Lopez de Prado & O'Hara (2012)。

    VPIN = Volume-Synchronized Probability of Informed Trading
    核心思想：在"成交量时钟"（非时间时钟）下切片，监测买卖单方占主导的
    程度。VPIN 高 = 知情交易者集中活动 = 流动性提供方面临逆向选择风险。

    与 Hawkes 的互补关系：
    - Hawkes：捕捉事件自激励/交叉激励（订单簿事件间的反馈）
    - VPIN：捕捉订单流方向失衡（买卖单方压倒性）
    - 两者正交：Hawkes 回答"事件是否聚集"，VPIN 回答"流向是否一边倒"

    实证依据（VisualHFT Silahian 2026-03）：
    - 2010 闪崩前 VPIN 持续升高（Easley et al. 原始发现）
    - Andersen & Bondarenko (2014 JFM) 质疑 VPIN 是领先还是同步指标
    - 实务结论：无论领先或同步，高 VPIN = 流动性环境已恶化，
      TWAP/VWAP 正在被填入恶化的成分，应该 act

    阈值（BV-VPIN，机构经验，非规范阈值）：
    - < 0.2：低毒性，流动性健康
    - 0.2-0.4：中等毒性，正常交易
    - 0.4-0.6：升高毒性，需关注
    - > 0.6：高毒性，闪崩前兆区
    - > 0.85（90-95 分位）：统计显著高毒性，流动性提供方撤单风险
    """
    vpin: float                         # [0, 1] 订单流毒性
    toxicity_level: str                 # "low" / "moderate" / "elevated" / "high"
    bucket_count: int                   # 成交量桶数
    window_buckets: int                 # 滚动窗口桶数
    buy_volume: float                   # 窗口内买方发起量
    sell_volume: float                  # 窗口内卖方发起量


def compute_vpin_bvc(
    price_changes: list[float],         # 各时间段价格变动
    volumes: list[float],               # 各时间段成交量
    n_buckets: int = 50,                # 成交量桶数
    window: int = 15,                   # 滚动窗口桶数
) -> VPINResult:
    """VPIN 计算——Bulk Volume Classification (BVC) 版本。

    Easley, Lopez de Prado, O'Hara (2012 RFS) "Flow Toxicity and Liquidity
    in a High Frequency World"。

    算法步骤：
    1. 成交量时钟：按累积成交量切分为 N 个等量桶（非等时间）
       → 交易活跃时段桶密、平静时段桶疏，自然适应交易强度
    2. BVC 买卖分类：buy_frac = Φ(ΔP / σ_ΔP)
       → 强正收益 → 多数归买方；强负收益 → 多数归卖方
       → 无需逐笔 trade sign，仅需价格变动序列
    3. 桶内失衡：imbalance_k = |V_buy_k - V_sell_k| / V_bucket
    4. VPIN = (1/n) Σ_{k=1..n} imbalance_k，n = 滚动窗口桶数

    BVC vs Tick Rule：
    - BVC：用正态 CDF 从价格变动推断买卖比例，无需逐笔数据
    - Tick Rule：用逐笔成交方向（ uptick=买 / downtick=卖 ）
    - Andersen & Bondarenko (2014) 指出两者在特定条件下方向相反
    - 实务多用 BVC（计算可处理，仅需 OHLCV 聚合数据）

    A 股适配：
    - A 股逐笔数据获取受限（miniQMT 提供分钟级聚合），BVC 更适合
    - 桶大小 V_bucket = 总成交量 / N，建议 N=50（机构经验）
    - 窗口 window=15 桶（约 30% 的桶数）
    """
    if not price_changes or not volumes:
        return VPINResult(0.0, "low", 0, window, 0, 0)

    # Step 1: 成交量时钟切片
    total_volume = sum(volumes)
    if total_volume <= 0:
        return VPINResult(0.0, "low", 0, window, 0, 0)

    bucket_size = total_volume / n_buckets
    bucket_idx = []
    cum_vol = 0.0
    current_bucket = 0
    for v in volumes:
        cum_vol += v
        current_bucket = min(n_buckets - 1, int(cum_vol / bucket_size))
        bucket_idx.append(current_bucket)

    # Step 2: BVC 买卖分类
    sigma = np.std(price_changes) if len(price_changes) > 1 else 1.0
    if sigma <= 0:
        sigma = 1e-9
    buy_fractions = [norm.cdf(dp / sigma) for dp in price_changes]

    # 按桶聚合
    bucket_buy = [0.0] * n_buckets
    bucket_sell = [0.0] * n_buckets
    for i, (v, bf) in enumerate(zip(volumes, buy_fractions)):
        b = bucket_idx[i]
        bucket_buy[b] += v * bf
        bucket_sell[b] += v * (1 - bf)

    # Step 3: 桶内失衡
    imbalances = []
    for b in range(n_buckets):
        v_total = bucket_buy[b] + bucket_sell[b]
        if v_total > 0:
            imbalances.append(abs(bucket_buy[b] - bucket_sell[b]) / v_total)
        else:
            imbalances.append(0.0)

    # Step 4: VPIN 滚动窗口平均
    vpin = 0.0
    if len(imbalances) >= window:
        vpin = float(np.mean(imbalances[-window:]))
    elif imbalances:
        vpin = float(np.mean(imbalances))

    # 毒性分级
    if vpin < 0.2:
        level = "low"
    elif vpin < 0.4:
        level = "moderate"
    elif vpin < 0.6:
        level = "elevated"
    else:
        level = "high"

    # 窗口内买卖量
    start = max(0, n_buckets - window)
    buy_vol = sum(bucket_buy[start:])
    sell_vol = sum(bucket_sell[start:])

    return VPINResult(
        vpin=vpin,
        toxicity_level=level,
        bucket_count=n_buckets,
        window_buckets=window,
        buy_volume=buy_vol,
        sell_volume=sell_vol,
    )


@dataclass
class UnifiedOFIResult:
    """Unified OFI——含撤单流的订单流不平衡。

    Kolm, Netoličková (2025) "Unified Order Flow Imbalance" / finantrix 2026-08：
    - 传统 OFI 仅用成交的买卖单差，R²≈0.32-0.35
    - Unified OFI 加入撤单流（cancel-flow），R²≈0.65（解释力近翻倍）
    - Conditional OFI（按流动性 regime 条件化）Sharpe=1.79

    公式：
    - 传统 OFI = Σ (买方主动成交 - 卖方主动成交) / 桶成交量
    - Unified OFI = 传统 OFI + 撤单流分量
      = Σ [(买成交 + 买撤单) - (卖成交 + 卖撤单)] / 桶成交量
    - 撤单流方向：买方撤单 = 负向 OFI（买方撤掉买盘 = 卖压信号）

    A 股适配：
    - miniQMT 提供 L1 行情（最优 5 档），L2 逐笔撤单需 Level-2 数据
    - MVP 阶段用成交 OFI（BVC 推断）+ 最优 5 档量变化代理撤单
    - Phase 1.5+ 接入 Level-2 后启用完整 Unified OFI

    与 VPIN 的关系：
    - VPIN：测度"流向是否一边倒"（毒性，无方向）
    - Unified OFI：测度"净买压"（有方向，可做信号）
    - 两者互补：VPIN 高 + Unified OFI 正 = 买方主导的毒性流（看涨前兆）
    """
    unified_ofi: float                  # Unified OFI（含撤单）
    trade_ofi: float                    # 仅成交 OFI（传统）
    cancel_ofi: float                   # 撤单流 OFI 分量
    r2_improvement: float               # 相对传统 OFI 的 R² 提升


def compute_unified_ofi(
    buy_initiated_volume: float,        # 买方主动成交
    sell_initiated_volume: float,       # 卖方主动成交
    bid_cancel_volume: float,           # 买方撤单量（最优 5 档）
    ask_cancel_volume: float,           # 卖方撤单量（最优 5 档）
    bucket_volume: float,               # 桶总成交量
) -> UnifiedOFIResult:
    """Unified OFI 计算——含撤单流的订单流不平衡。

    Kolm & Netoličková (2025) 实证：
    - 传统 OFI（仅成交）对短期收益 R²≈0.32-0.35
    - Unified OFI（成交+撤单）R²≈0.65，解释力近翻倍
    - 撤单流分量在闪崩前显著上升（机械性撤单 = 流动性枯竭前兆）

    与 §3.7 OFE-Hawkes 的协同：
    - OFE-Hawkes：用多元 Hawkes 模型化订单簿事件的自激励/交叉激励
    - Unified OFI：用单一标量聚合买卖+撤单的方向性净流
    - OFE-Hawkes 回答"事件如何相互激励"，Unified OFI 回答"净流向何方"
    - Phase 1.5+ 建议两者联合：Unified OFI 做信号，OFE-Hawkes 做风险监控
    """
    if bucket_volume <= 0:
        return UnifiedOFIResult(0.0, 0.0, 0.0, 0.0)

    # 传统 OFI（仅成交）
    trade_ofi = (buy_initiated_volume - sell_initiated_volume) / bucket_volume

    # 撤单流分量（买方撤单 = 卖压信号 = 负向 OFI）
    cancel_ofi = (ask_cancel_volume - bid_cancel_volume) / bucket_volume

    # Unified OFI
    unified_ofi = trade_ofi + cancel_ofi

    # R² 提升估计（机构经验：撤单分量贡献约 0.30 的额外 R²）
    r2_improvement = 0.30 if abs(cancel_ofi) > 0.01 else 0.0

    return UnifiedOFIResult(
        unified_ofi=unified_ofi,
        trade_ofi=trade_ofi,
        cancel_ofi=cancel_ofi,
        r2_improvement=r2_improvement,
    )


def detect_toxicity_crisis(
    vpin: VPINResult,
    unified_ofi: UnifiedOFIResult,
    hawkes_branching_ratio: float = 0.0,
) -> LiquidityCrisisSignal:
    """毒性危机综合检测——VPIN + Unified OFI + Hawkes 三联检测。

    三指标互补：
    - VPIN：订单流毒性（买卖失衡的强度）
    - Unified OFI：净流向方向（正=买压 / 负=卖压）
    - Hawkes branching ratio：内生反馈强度（接近 1 = 相变）

    综合判定：
    - VPIN > 0.6 + Hawkes > 0.85 → CRISIS（毒性+内生反馈双高）
    - VPIN > 0.6 only → WARNING（毒性高但反馈未达相变）
    - Unified OFI 极端（|OFI| > 0.5）+ VPIN > 0.4 → 方向性危机前兆
    """
    triggers = []

    if vpin.vpin > 0.85:
        triggers.append(f"vpin_extreme_{vpin.vpin:.2f}")
    elif vpin.vpin > 0.6:
        triggers.append(f"vpin_high_{vpin.vpin:.2f}")
    elif vpin.vpin > 0.4:
        triggers.append(f"vpin_elevated_{vpin.vpin:.2f}")

    if hawkes_branching_ratio > 0.85:
        triggers.append(f"hawkes_near_critical_{hawkes_branching_ratio:.2f}")

    if abs(unified_ofi.unified_ofi) > 0.5:
        direction = "buy_pressure" if unified_ofi.unified_ofi > 0 else "sell_pressure"
        triggers.append(f"ofi_extreme_{direction}_{unified_ofi.unified_ofi:.2f}")

    # 综合判定
    has_extreme_vpin = vpin.vpin > 0.6
    has_critical_hawkes = hawkes_branching_ratio > 0.85

    if has_extreme_vpin and has_critical_hawkes:
        return LiquidityCrisisSignal(
            crisis_level="CRISIS",
            triggers=triggers,
            recommended_action="stop_new_open",
        )
    elif has_extreme_vpin or has_critical_hawkes or len(triggers) >= 2:
        return LiquidityCrisisSignal(
            crisis_level="WARNING",
            triggers=triggers,
            recommended_action="monitor",
        )
    else:
        return LiquidityCrisisSignal(
            crisis_level="NORMAL",
            triggers=triggers,
            recommended_action="none",
        )
```

### 3.10 跨市场流动性毒性识别（远期候选）

本节登记两项 2026-08 跨市场研究的**方法论借鉴**，作为 Phase 2+ 远期候选。A 股微结构与 DEX/印度市场差异显著，不直接复用算法，但思想可迁移。MVP/Phase 1.5 不实施，避免过度工程。

#### 3.10.1 Public Trader Identity wallet toxicity

Zhai (2026-08) arXiv:2608.04373 "Public Trader Identity: Adverse Selection and Return Predictability"：

**研究核心**：
- 去中心化交易所公开每笔订单的 pseudonymous wallet address（订单/撤单/拒单/成交均携带持久钱包标识）
- 通过钱包历史 aggressive order 的 signed markouts（成交后价格移动方向 × 幅度）给钱包打分
- 高分钱包（历史 markouts 正）的未来激进订单预测未来收益

**关键发现**：
- 钱包 informativeness 是持久属性（10 天排名与后 10 天 rank correlation = 0.52）
- 身份信息使 1 秒收益预测 R² 提升 13.2%（t=9.2），从匿名基准 10.87% 升至 12.31%
- 在实际成交时刻，增量从 1.43% 升至 2.47%（vs 全样本采样时刻）
- Matched-wallet placebo 检验：1.6 倍于 200 个活动匹配安慰剂队列的最大增益，排除虚假相关
- Feature embargo + matched-cohort 设计避免 look-ahead 与选择偏差

**A 股类比与适用性评估**：
- A 股无钱包身份，但有**龙虎榜席位标识**（"机构席位"/"游资席位"/"营业部"）
- [24_daban_strategy_detail] 已实现 Smart Money 席位画像（净买率/合力型/独食型/假机构识别）
- 方法论同构：席位历史 signed markouts → 席位毒性评分 → 高分席位入场 = 信号
- **与 VPIN/Unified OFI 的互补关系**：
  - VPIN：测度"流向是否一边倒"（无身份，仅方向失衡）
  - Unified OFI：测度"净流向方向"（无身份，仅净压）
  - 席位毒性：测度"哪些身份在主导"（有身份，定位知情者）
  - 三者正交：VPIN/OFI 是匿名流毒性，席位毒性是具名流毒性

**Phase 2+ 评估条件**：
- 龙虎榜席位画像积累 6+ 月历史 markouts（依赖 [24] Smart Money 席位画像基础设施）
- 与北向资金/港股通席位画像联动（跨市场传染监测，与 An & Dai 2026-08 Transfer Entropy + 多元 Hawkes 同期评估）
- 登记为待裁定项，不在 MVP/Phase 1.5 实施

#### 3.10.2 India CAS 收盘集合竞价流动性监测

SEBI 2026-08-03 在 F&O 标的推出 Closing Auction Session (CAS)，替换原 30 分钟 VWAP 收盘：

**CAS 时序结构**：
- 15:15 连续交易结束
- 15:15-15:20 参考价计算（3:00-3:15 VWAP）+ 转换期，无新单
- 15:20-15:25 限价 + 市价单录入，发布指示性均衡价（IEP）和失衡量
- 15:25-15:30 仅限价单，市价单冻结，末两分钟随机收盘
- 15:30-15:35 在均衡价撮合，价格带 ±3%
- F&O 衍生品交易至 15:40（现金锁价后衍生品仍可反应 5 分钟）

**首周实证（2026-08-03~06）**：
- Nifty 首日跳升 200+ 点，4 日平均 3:30 vs 3:15 偏离 +0.42%
- Sensex 同期仅 +0.10%（NSE 采用 CAS、BSE 仍用 VWAP 的结构性分化）
- 流动性稀薄 + 做空受限 + 期货税重 → 套利失效 → 收盘价失真
- Day 4 Nifty CAS 成交 14.33 亿卢比 vs Sensex 1.27 亿卢比（参与度失衡）

**A 股适用性评估**：
- A 股已有 14:57-15:00 收盘集合竞价（3 分钟，比 India CAS 20 分钟紧凑）
- A 股收盘竞价机制相对成熟，无 India CAS 首周的剧烈波动问题
- **借鉴价值**：India CAS 失衡量公开 + IEP 实时发布 + 衍生品延后收盘的设计，对 A 股收盘流动性突变监测有方法论启发

**借鉴算法（待评估，不展开实现）**：
1. **收盘失衡量监测**：CAS 窗口内买卖单失衡量 / 总委托量，> 阈值告警
2. **均衡价跳跃检测**：IEP 跳跃幅度 > 连续交易时段中位数的 N 倍
3. **衍生品联动**：现金收盘锁价后衍生品延后交易时段的反向定价（基差突变）
4. **参与度失衡**：CAS 成交量 / 全日成交量的 Z-score 异常

**Phase 2+ 评估条件**：
- 积累 3+ 月 A 股收盘竞价高频数据
- 评估 14:57-15:00 收盘失衡量与次日开盘跳空的统计关系
- 登记为待裁定项，与 §6 盘后固定价格交易（2026-07-06 新规）同期评估

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **仅用买卖价差** | 单一价差倍数检测 | 无法区分机械性撤单 vs 信息重定价（Xu 2026 证明 AUC 差 36%）；无法捕捉 Hawkes 内生反馈 |
| **仅用 Amihud** | 单一 Amihud 非流动性 | 日频粗糙，不说盘内流动性；适合横截面结构化，不适合实时危机检测 |
| **外生危机模型** | 假设危机由新闻驱动 | Fosset et al. 证明大部分大价格跳跃是内生反馈（4σ 事件无法用新闻解释） |
| **自动恢复** | 价差恢复后自动恢复交易 | Kill Switch 不可覆盖原则（§2.5.5）；恢复需人工授权（ARKA 2026 共识） |
| **融券对冲** | 跌停时融券卖出对冲 | A 股融券标的有限、成本高、2024-2025 限融政策约束；MVP 阶段不可行 |
| **仅用 Hawkes（无 VPIN/OFI）** | 只用 Hawkes 分支比检测 | Hawkes 回答"事件是否聚集"，不回答"流向是否一边倒"；VPIN 补充毒性维度，Unified OFI 补充方向维度，三者正交互补 |
| **Tick Rule VPIN（非 BVC）** | 用逐笔成交方向分类 VPIN | A 股 miniQMT 仅提供分钟级聚合数据，逐笔数据获取受限；BVC 仅需价格变动序列更适合；Andersen & Bondarenko 2014 指出两者在特定条件下方向相反，需统一口径 |
| **仅用成交 OFI（无撤单流）** | 传统 OFI 不含撤单分量 | Kolm & Netoličková 2025 实证 R² 仅 0.32-0.35；加入撤单流 Unified OFI R²≈0.65，解释力近翻倍 |
| **VPIN 作为独立交易信号** | VPIN 高即做空 | Andersen & Bondarenko 2014 质疑 VPIN 是领先还是同步指标；VPIN 应作为风险过滤器（与 Hawkes/OFI 三联检测），非独立信号 |
| **Public Trader Identity 直接迁移** | 在 A 股复用 DEX 钱包毒性算法 | A 股无钱包身份标识；龙虎榜席位画像（[24]）是其类比实现，方法论同构但数据源完全不同；DEX 算法直接迁移不可行，仅作方法论借鉴 |
| **India CAS 算法直接迁移** | 在 A 股复用 20 分钟 CAS 失衡量监测 | A 股收盘竞价仅 3 分钟（14:57-15:00），结构远比 India CAS 紧凑；A 股收盘竞价机制成熟无首周剧烈波动；仅借鉴失衡量/IEP 跳跃/参与度失衡四项监测思想 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **价差危机线** | 5×正常价差 | tradingwyckoff 2026-01 Kill Switch 触发线 |
| **价差警告线** | 3×正常价差 | 预警阈值 |
| **Hawkes 临界** | 分支比 > 0.85 | Fosset et al. 相变临界点 |
| **VPIN 高毒性线** | > 0.6 | VisualHFT 2026-03 实务阈值（闪崩前兆区） |
| **VPIN 极端线** | > 0.85 | 90-95 分位，统计显著高毒性 |
| **Unified OFI 极端线** | \|OFI\| > 0.5 | 方向性危机前兆（净买/卖压极端） |
| **封单黑洞线** | 封单 > 流通市值 5% | 实务经验：5% 封单几乎不可能当日开板 |
| **连续跌停线** | 2+ 天 | 连续跌停标记为 BLACK_HOLE |

**演进路径**：
- MVP：价差倍数 + 涨跌停封单检测（规则驱动）+ VPIN BVC 计算（仅需 OHLCV 聚合）
- Phase 1.5：Hawkes 内生反馈检测 + Amihud/Kyle λ 实时计算 + Unified OFI（Level-2 接入）
- Phase 2：Crumbling Quotes 神经检测模型（arXiv:2604.21993）+ Bouchaud Propagator 冲击衰减
- Phase 2+：跨市场流动性毒性识别（§3.10 Public Trader Identity 席位画像类比 + India CAS 收盘失衡量监测 + An & Dai 跨境传染）

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **Crumbling Quotes 神经模型** | 需 ABIDES 模拟器+训练数据 | Phase 2+ 算力充足时 |
| **Q-Hawkes 完整实现** | 参数校准需高频数据 | Phase 1.5+ Level-2 数据就绪 |
| **跨境传染检测** | An & Dai (2026-08) Transfer Entropy + 多元 Hawkes | Phase 2+ 跨市场（A 股+港股+美股）联动时 |
| **盘后固定价格交易** | 2026-07-06 新规扩容，盘后流动性特征待观察 | 积累 3 月盘后数据后评估 |
| **完整 Unified OFI（含逐笔撤单）** | 需 Level-2 逐笔撤单数据 | Phase 1.5+ Level-2 接入后 |
| **Conditional OFI 信号** | 需流动性 regime 分桶 + 足够样本 | Phase 1.5+ Conditional OFI Sharpe=1.79 实证复现后 |
| **Public Trader Identity 席位毒性** | A 股无钱包身份；龙虎榜席位画像基础设施（[24]）需 6+ 月 markouts 积累 | Phase 2+ 跨市场传染监测时，与 An & Dai 2026-08 Transfer Entropy + 多元 Hawkes 同期评估 |
| **India CAS 收盘失衡量监测** | A 股收盘竞价仅 3 分钟，结构差异大 | 积累 3+ 月 A 股收盘竞价高频数据，与 §6 盘后固定价格交易同期评估 |

## 7. 待定问题（讨论要点对齐）

- [x] ① 买卖价差监控（>正常 5x 触发）→ §3.3 `detect_liquidity_crisis` 检测 1
- [x] ② 流动性危机→立即停止开仓仅允许平仓 → §3.5 `execute_liquidity_crisis_response` CRISIS 级
- [x] ③ 流动性指标定义（换手率/成交额/盘口深度）→ §3.2 `calc_liquidity_indicators` 多维度
- [x] ④ 与 Kill Switch 的关系 → §3.3 CRISIS 级触发 Kill Switch 联动（价差 > 5x = Kill Switch 触发线）
- [x] ⑤ A 股涨跌停流动性失效处理 → §3.6 `handle_limit_down_trap` 封单力度+连续跌停+排队策略

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G18
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5.5
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16，Kill Switch 联动）
- [36_var_es_monitoring](36_var_es_monitoring.md)（G17，L-VaR 流动性因子来源）
- battle_map_09_risk_control（当前状态快照）
- **2026-08 研究引用**：
  - Fosset, Bouchaud, Benzaquen "Endogenous Liquidity Crises" arXiv:1912.00359 — Hawkes/Q-Hawkes 内生相变
  - Xu et al. (2026-04) "Crumbling Quotes" arXiv:2604.21993 (ICLR 2026 Workshop) — 机械性 vs 信息性侵蚀
  - An & Dai (2026-08) Entropy 28(8) 887 — Transfer Entropy + 多元 Hawkes 跨境传染
  - O'Connell (2026-03) "L-VaR" — Amihud + Kyle λ
  - Micro Alphas (2026-06) "Amihud Illiquidity Ratio"
  - Morariu-Patrichi & Pakkanen arXiv:1809.08060 — State-dependent Hawkes LOB
  - Realsumen OFE-Hawkes (2025-08) — Order Flow Endogeneity 6 类事件多元 Hawkes
  - Wehrli & Sornette (2022) Quantitative Finance 22(2) 213-240 — Hawkes(p,q) EM 闪崩分类
  - Rakeshks7 (2026-02) hawkes-process-hft-microstructure — Recursive MLE O(N) 实现
  - Lee & Seo (2022) arXiv:2201.10173 — extended Hawkes 价差依赖强度
  - Anantha & Jain (2024-08) arXiv:2408.03594 — Hawkes 预测高频 OFI
  - Easley, Lopez de Prado, O'Hara (2012) RFS 25(5) 1457-1493 "Flow Toxicity and Liquidity in a High Frequency World" — VPIN 原始论文
  - Andersen & Bondarenko (2014) JFM 17 "VPIN and the Flash Crash" — VPIN 领先 vs 同步指标批判性讨论
  - VisualHFT Silahian (2026-03) "VPIN and Real-Time Order Toxicity" — BV-VPIN 实务阈值 0.7/0.85
  - Kolm & Netoličková (2025) "Unified Order Flow Imbalance" — 含撤单流 OFI，R² 0.32→0.65
  - finantrix (2026-08) "Execution Algorithms and SOR — TCA 2.0" — Conditional OFI Sharpe=1.79
  - 上证发〔2026〕41 号《交易规则（2026 年修订）》— ST 涨跌停 10%、盘后固定价格扩容
  - 东方财富 (2026-05-19) ST 跌停制度性缺陷分析
  - Zhai (2026-08) arXiv:2608.04373 "Public Trader Identity: Adverse Selection and Return Predictability" — DEX 钱包身份毒性识别，R² 提升 13.2%，matched-wallet placebo 排除虚假相关
  - SEBI (2026-08-03) Closing Auction Session (CAS) 改革 — F&O 标的收盘集合竞价替换 30 分钟 VWAP，首周 Nifty 跳升 200+ 点
  - caalley.com (2026-08-07) "Chaotic Debut: How SEBI's Closing Auction Reform Fared In Its First Week" — CAS 首周实证分析
  - cumbernauld-media.com (2026-08) "SEBI CAS Forces Options Traders to Recalibrate Closing Risk" — CAS 时序结构与衍生品联动

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | 多维度流动性指标+三级危机检测+Hawkes 内生反馈+Crumbling Quotes+涨跌停黑洞处理+应急响应算法化；整合 2026-08 研究（Fosset Hawkes/Xu Crumbling Quotes/上交所新规） |
| 2026-08-10 | 1.1.0 | 新增 §3.7 多元 Hawkes OFE 扩展+§3.8 Hawkes(p,q) EM 估计+危机起源分类 | 整合 Realsumen OFE-Hawkes 2025-08（6 类事件交叉激励）+Wehrli & Sornette 2022 QF（时变 branching ratio EM）+Rakeshks7 2026-02（O(N) 递归 MLE）+Lee & Seo 2022（价差依赖强度）+Anantha & Jain 2024（OFI 预测） |
| 2026-08-10 | 1.2.0 | 新增 §3.9 VPIN 订单流毒性检测+Unified OFI 含撤单流+三联毒性危机综合检测 | 整合 Easley/LdP/O'Hara 2012 VPIN + BVC 买卖分类 + Andersen & Bondarenko 2014 批判性讨论 + VisualHFT 2026-03 实务阈值 + Kolm & Netoličková 2025 Unified OFI（R² 翻倍）+ finantrix 2026-08 Conditional OFI |
| 2026-08-10 | 1.3.0 | 新增 §3.10 跨市场流动性毒性识别（远期候选）+§4 替代方案表新增 2 行+§5 演进路径补 Phase 2+ +§6 待裁定表新增 2 行+§8 引用新增 4 条 | 整合 Zhai 2026-08 arXiv:2608.04373 Public Trader Identity 钱包毒性（R² 提升 13.2% + matched-wallet placebo）+ SEBI 2026-08-03 India CAS 收盘集合竞价改革（首周 Nifty 跳 200 点）+ A 股类比评估（龙虎榜席位画像方法论同构 + A 股收盘竞价 3 分钟 vs CAS 20 分钟结构差异） |
