---
ttl: permanent
doc_type: architecture_view
title: 板块轮动 spec
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.1"
date: 2026-08-11
topic: sector_rotation_spec
scope: 07_trading_decision_architecture
---

# 板块轮动 spec

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G06 主题组派生，将板块轮动的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：AQR sector momentum（行业动量因子 RS>1 跑赢大盘）；华泰板块轮动研报（相对强度+资金流+情绪三维度）；申万行业轮动（880xxx K 线体系，约 460 板块）；A 股板块虹吸效应（游资集中度模型）；板块轮动四阶段模型（启动/加速/见顶/回落）；mask-first 设计（板块级涨跌停过滤，[52_backtest_framework_docking](52_backtest_framework_docking.md) A 股 mask-first 前置设计）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G06 板块轮动 spec |
| 所属 | 作战地图 05（BM-SEL-08/09，MOD-SIG-026 板块分析器） |
| 依赖 | G04（板块是选股的输入特征，非独立层）、[15_data_feature_layer_spec](15_data_feature_layer_spec.md)（板块 K 线数据契约） |
| 对标 | AQR sector momentum / 华泰板块轮动研报 / 申万行业轮动 |
| 正交性 | ✅ 与 regime 正交（板块轮动是选股输入特征，非独立层；regime 只做 Shrinkage 风险节流，不参与选股） |
| 优先级 | P1 |
| 状态 | ✅ active — 板块强度+板块级回踩质量+调整周期+轮动序列+虹吸态+资金流+板块→个股传导 7 算法已定稿 |

## 2. 背景

### 2.1 项目处境

板块轮动是 A 股 alpha 的核心特征之一。A 股市场由约 460 个板块（同花顺 880xxx 板块 K 线体系，覆盖申万一级 31 + 申万二级 ~134 + 同花顺概念 ~295）构成，资金在不同板块间轮动形成结构性机会。板块强度是选股的关键输入特征——同一个个股 alpha 信号，在强势板块中胜率显著高于弱势板块。

[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §1.3 明确指出："情绪周期（冰点/反核/主升/疯狂/退潮）是所有短周期策略的共同隐形驱动 → 策略间相关性可能高于直觉"。板块轮动是情绪周期的具象化载体——情绪周期驱动资金在板块间轮动，板块轮动序列是情绪周期的可观测投影。因此板块轮动不是独立策略层，而是所有 alpha 策略（[24_daban_strategy_detail](24_daban_strategy_detail.md) 打板、[25_multifactor_strategy_detail](25_multifactor_strategy_detail.md) 多因子、[26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) 事件驱动）的共同输入特征。

[41_buy_flow](41_buy_flow.md) §3.2 已定义个股级 `evaluate_pullback_quality`，本文档需扩展为板块级——板块级回踩质量决定买入优先级，是个股级回踩质量的上游门控。

### 2.2 核心问题

1. **板块强度量化**（BM-SEL-08）：460 板块的强度如何统一量化？单一指标（涨跌幅）易被噪声干扰，需多因子加权（相对强度+动量+资金流+领涨股占比）。
2. **板块级回踩质量**：[41_buy_flow](41_buy_flow.md) §3.2 的个股级 A/B/C 分级如何扩展到板块级？板块指数回踩 + 板块内个股一致性如何联合判定？
3. **调整周期追踪**（BM-SEL-09）：板块调整走到哪一步了？进度 ≥80% 才允许分批低吸，初期 <40% 直接拦截——进度如何定义？
4. **轮动序列追踪**：板块轮动有顺序（领涨→跟涨→补涨→领跌），如何检测当前轮动阶段和板块角色？历史模式能否匹配？
5. **虹吸态识别**：龙头板块吸金时，非龙头板块即使有 alpha 也难涨——虹吸态如何识别？对选股有何影响？
6. **板块资金流**：板块资金流是个股资金流的聚合，但聚合后的趋势（5/10/20 日均线）如何反映板块资金面？
7. **板块→个股传导**：板块强度如何加成个股信号？传导延迟（板块领先个股 1-3 天）和衰减如何量化？

### 2.3 约束条件

- **A 股 T+1**：板块 K 线 T+1 盘后更新，盘中只有实时板块指数（不含资金流明细）
- **涨跌停板**：板块内个股涨停潮/跌停潮时，板块信号失真——需 mask-first 过滤（[52_backtest_framework_docking](52_backtest_framework_docking.md) A 股 mask-first 前置设计）
- **460 板块 880xxx K 线**：同花顺板块 K 线代码体系（如 880301 半导体），提供板块级 OHLCV + 涨跌家数 + 资金流
- **与 regime 正交**：板块轮动是选股输入特征，非独立层；regime 只做 Shrinkage 风险节流，不参与选股（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2）
- **mask-first 前置**：板块级涨跌停过滤必须在信号生成前完成，避免追高涨停潮/接刀跌停潮
- **MVP 简化**：先做多因子加权评分 + 板块级 A/B/C + 调整进度 80% 阈值，Phase 1.5+ 再上 ML 板块轮动预测

## 3. 决策

### 3.1 架构定义

板块轮动由板块强度层、轮动追踪层、传导映射层三层构成：

```
板块强度层: 460 板块 880xxx K 线 → mask-first 涨跌停过滤 → 多因子加权评分 → 板块强度排序
                                                ↓
轮动追踪层: 调整周期追踪(进度≥80%) + 轮动阶段检测(4 阶段) + 轮动角色检测(领涨/跟涨/补涨/领跌)
            + 虹吸态识别 + 板块资金流趋势
                                                ↓
传导映射层: 板块强度 → 个股信号加成 + 传导延迟估计 + 传导衰减 → 增强后个股信号 → 下游选股/买入流
```

**与下游的接口契约**：
- 输出 `SectorStrength`（§3.2）、`SectorPullbackAssessment`（§3.3）、`SectorAdjustmentProgress`（§3.4）供 [41_buy_flow](41_buy_flow.md) §3.2 买入流消费
- 输出 `SectorStockConduction`（§3.8）供 [21_stock_selection_engine](21_stock_selection_engine.md) 选股引擎消费
- 输出 `SiphonState`（§3.6）供 [24_daban_strategy_detail](24_daban_strategy_detail.md) 打板策略消费（虹吸龙头板块加成）

### 3.2 板块强度算法（BM-SEL-08，460 板块 880xxx K 线）

```python
from enum import Enum
from dataclasses import dataclass, field
import numpy as np


class SectorUniverse(Enum):
    """A 股板块体系——同花顺 880xxx 板块 K 线（约 460 板块）。

    覆盖：
    - 申万一级 31 行业（880xxx 系列映射）
    - 申万二级 ~134 行业
    - 同花顺概念板块 ~295（含题材、地域等）

    板块 K 线特点：
    - 880xxx 代码（如 880301 为 "半导体"）
    - 提供板块级 OHLCV + 涨跌家数 + 资金流
    - T+1 数据更新（盘后）
    """
    SW_LEVEL1 = "sw_l1"           # 申万一级（31 个）
    SW_LEVEL2 = "sw_l2"           # 申万二级（~134 个）
    THS_CONCEPT = "ths_concept"   # 同花顺概念（~295 个）


@dataclass
class SectorStrength:
    """板块强度综合评分结果（BM-SEL-08）。"""
    sector_code: str                     # 板块代码（880xxx）
    sector_name: str
    # 维度 1：相对强度 RS（AQR sector momentum 核心因子）
    rs_5d: float                         # 5 日相对强度
    rs_20d: float                        # 20 日相对强度
    rs_60d: float                        # 60 日相对强度
    # 维度 2：多周期动量横截面排名
    momentum_rank_20d: int               # 20 日动量排名（1=最强）
    momentum_rank_60d: int               # 60 日动量排名
    momentum_rank_120d: int              # 120 日动量排名
    # 维度 3：资金流强度（华泰三维度之一）
    capital_flow_intensity: float        # 主力净流入/成交额
    capital_flow_trend: str              # "inflow" / "outflow" / "neutral"
    # 维度 4：领涨股占比（情绪维度）
    advancer_ratio: float                # 上涨家数/(上涨+下跌家数)
    # 综合评分
    composite_score: float               # 多因子加权综合评分 [0, 100]
    strength_level: str                  # "STRONG" / "MEDIUM" / "WEAK"
    # mask-first 过滤（52_backtest_framework_docking A 股 mask-first 前置设计）
    is_masked: bool                      # 是否被涨跌停 mask 过滤
    mask_reason: str                     # mask 原因


def calc_relative_strength(
    sector_close: np.ndarray,        # 板块收盘价序列
    benchmark_close: np.ndarray,     # 大盘收盘价序列（如沪深300/上证指数）
    window: int = 20,
) -> float:
    """相对强度 RS——AQR sector momentum 核心因子。

    RS = (1 + 板块累计收益) / (1 + 大盘累计收益)

    AQR 行业动量实证：
    - RS > 1.0：板块跑赢大盘，多头信号
    - RS < 1.0：板块跑输大盘，回避
    - 多周期 RS（5/20/60）组合优于单周期

    华泰板块轮动研报（2026）：RS 是板块轮动的最稳健单因子。
    """
    if len(sector_close) < window or len(benchmark_close) < window:
        return 1.0
    sector_ret = sector_close[-1] / sector_close[-window] - 1
    bench_ret = benchmark_close[-1] / benchmark_close[-window] - 1
    if abs(bench_ret) < 1e-8:
        return 1.0
    return (1 + sector_ret) / (1 + bench_ret)


def calc_momentum_rank(
    sector_returns: dict[str, float],   # {板块代码: 区间收益}
    target_sector: str,
) -> int:
    """多周期动量横截面排名——返回 target_sector 在所有板块中的排名（1=最强）。"""
    sorted_sectors = sorted(
        sector_returns.items(), key=lambda x: x[1], reverse=True
    )
    for rank, (code, _) in enumerate(sorted_sectors, 1):
        if code == target_sector:
            return rank
    return len(sorted_sectors)


def calc_capital_flow_intensity(
    main_net_inflow: float,             # 板块主力净流入（元）
    total_turnover: float,              # 板块成交额（元）
    history_inflow: np.ndarray = None,  # 历史主力净流入序列
) -> tuple[float, str]:
    """资金流强度——主力净流入占成交额比例 + 趋势判定。

    华泰板块轮动研报（2026）三维度之一：
    - intensity > 5% → 强势资金流入
    - intensity < -5% → 强势资金流出
    - MA5 > MA10 → inflow 趋势确认
    """
    if total_turnover <= 0:
        return 0.0, "neutral"
    intensity = main_net_inflow / total_turnover

    if history_inflow is not None and len(history_inflow) >= 10:
        ma5 = np.mean(history_inflow[-5:])
        ma10 = np.mean(history_inflow[-10:])
        if ma5 > ma10 * 1.1 and intensity > 0:
            trend = "inflow"
        elif ma5 < ma10 * 0.9 and intensity < 0:
            trend = "outflow"
        else:
            trend = "neutral"
    else:
        trend = "inflow" if intensity > 0.02 else ("outflow" if intensity < -0.02 else "neutral")

    return float(intensity), trend


def calc_advancer_ratio(
    advancing_count: int,           # 板块内上涨家数
    declining_count: int,           # 板块内下跌家数
    limit_up_count: int = 0,        # 涨停家数（mask-first 用）
    limit_down_count: int = 0,      # 跌停家数（mask-first 用）
) -> tuple[float, bool, str]:
    """领涨股占比 + mask-first 涨跌停过滤。

    领涨股占比 = 上涨家数 / (上涨 + 下跌家数)

    mask-first 设计（52_backtest_framework_docking A 股 mask-first 前置设计）：
    - 板块内涨停家数 > 30% → 板块信号 mask（避免追高涨停潮）
    - 板块内跌停家数 > 20% → 板块信号 mask（流动性危机风险）
    """
    total = advancing_count + declining_count
    if total == 0:
        return 0.5, True, "empty_sector"

    ratio = advancing_count / total

    # mask-first 涨跌停过滤
    is_masked = False
    mask_reason = ""
    if limit_up_count > total * 0.30:
        is_masked = True
        mask_reason = f"limit_up_cluster({limit_up_count}/{total}>30%)"
    elif limit_down_count > total * 0.20:
        is_masked = True
        mask_reason = f"limit_down_cluster({limit_down_count}/{total}>20%)"

    return float(ratio), is_masked, mask_reason


def evaluate_sector_strength(
    sector_code: str,
    sector_name: str,
    sector_close: np.ndarray,                    # 板块收盘价序列
    benchmark_close: np.ndarray,                 # 大盘收盘价序列
    sector_returns_by_period: dict[str, dict[str, float]],  # {period: {sector_code: return}}
    main_net_inflow: float,
    total_turnover: float,
    history_inflow: np.ndarray,
    advancing_count: int,
    declining_count: int,
    limit_up_count: int = 0,
    limit_down_count: int = 0,
    weights: dict = None,
) -> SectorStrength:
    """板块强度综合评分——BM-SEL-08 核心算法。

    多因子加权（华泰板块轮动研报 2026 三维度 + AQR 多周期动量）：
    | 维度 | 权重 | 来源 |
    | 相对强度 RS | 0.30 | AQR sector momentum |
    | 多周期动量 | 0.30 | AQR + 华泰 |
    | 资金流强度 | 0.25 | 华泰三维度 |
    | 领涨股占比 | 0.15 | 情绪维度 |

    评分映射：
    - composite_score ∈ [0, 100]
    - ≥75 → STRONG
    - 50-75 → MEDIUM
    - <50 → WEAK

    mask-first 过滤：被 mask 的板块强制降级为 WEAK（评分上限 40）。
    """
    if weights is None:
        weights = {"rs": 0.30, "momentum": 0.30, "capital_flow": 0.25, "advancer": 0.15}

    # ===== 维度 1：多周期相对强度 RS =====
    rs_5d = calc_relative_strength(sector_close, benchmark_close, window=5)
    rs_20d = calc_relative_strength(sector_close, benchmark_close, window=20)
    rs_60d = calc_relative_strength(sector_close, benchmark_close, window=60)

    def rs_to_score(rs: float) -> float:
        """RS > 1.2 → 满分；RS < 0.8 → 0 分；中间线性。"""
        if rs >= 1.2:
            return 100.0
        elif rs <= 0.8:
            return 0.0
        else:
            return (rs - 0.8) / 0.4 * 100

    rs_score = (rs_to_score(rs_5d) + rs_to_score(rs_20d) + rs_to_score(rs_60d)) / 3

    # ===== 维度 2：多周期动量横截面排名 =====
    n_sectors = len(next(iter(sector_returns_by_period.values()))) if sector_returns_by_period else 1
    rank_20d = calc_momentum_rank(sector_returns_by_period.get("20d", {}), sector_code)
    rank_60d = calc_momentum_rank(sector_returns_by_period.get("60d", {}), sector_code)
    rank_120d = calc_momentum_rank(sector_returns_by_period.get("120d", {}), sector_code)

    def rank_to_score(rank: int, total: int) -> float:
        """rank=1 → 满分；rank=n → 0 分。"""
        if total <= 1:
            return 50.0
        return (1 - (rank - 1) / (total - 1)) * 100

    momentum_score = (
        rank_to_score(rank_20d, n_sectors) +
        rank_to_score(rank_60d, n_sectors) +
        rank_to_score(rank_120d, n_sectors)
    ) / 3

    # ===== 维度 3：资金流强度 =====
    cf_intensity, cf_trend = calc_capital_flow_intensity(
        main_net_inflow, total_turnover, history_inflow
    )
    # intensity > 5% → 满分；< -5% → 0 分；中间线性
    if cf_intensity >= 0.05:
        cf_score = 100.0
    elif cf_intensity <= -0.05:
        cf_score = 0.0
    else:
        cf_score = (cf_intensity + 0.05) / 0.10 * 100
    # 趋势加成
    if cf_trend == "inflow":
        cf_score = min(100, cf_score + 10)
    elif cf_trend == "outflow":
        cf_score = max(0, cf_score - 10)

    # ===== 维度 4：领涨股占比 + mask-first =====
    adv_ratio, is_masked, mask_reason = calc_advancer_ratio(
        advancing_count, declining_count, limit_up_count, limit_down_count
    )
    advancer_score = adv_ratio * 100

    # ===== 综合评分 =====
    composite = (
        weights["rs"] * rs_score +
        weights["momentum"] * momentum_score +
        weights["capital_flow"] * cf_score +
        weights["advancer"] * advancer_score
    )

    # 强度等级
    if composite >= 75:
        level = "STRONG"
    elif composite >= 50:
        level = "MEDIUM"
    else:
        level = "WEAK"

    # mask-first 过滤：被 mask 的板块强制降级为 WEAK
    if is_masked:
        level = "WEAK"
        composite = min(composite, 40)

    return SectorStrength(
        sector_code=sector_code,
        sector_name=sector_name,
        rs_5d=float(rs_5d),
        rs_20d=float(rs_20d),
        rs_60d=float(rs_60d),
        momentum_rank_20d=rank_20d,
        momentum_rank_60d=rank_60d,
        momentum_rank_120d=rank_120d,
        capital_flow_intensity=float(cf_intensity),
        capital_flow_trend=cf_trend,
        advancer_ratio=float(adv_ratio),
        composite_score=float(composite),
        strength_level=level,
        is_masked=is_masked,
        mask_reason=mask_reason,
    )
```

### 3.3 板块级回踩质量等级 A/B/C 判定（扩展 41_buy_flow.md §3.2 个股级）

```python
class SectorPullbackQuality(Enum):
    """板块级回踩质量分级（扩展 41_buy_flow.md §3.2 个股级 PullbackQuality）。

    与个股级的关系：
    - 41_buy_flow.md §3.2 evaluate_pullback_quality 是个股级
    - 本节扩展为板块级：板块指数 OHLCV + 板块内个股一致性
    - 板块级 A 级 + 个股级 A 级 = 买入信号最强加成
    - 板块级 C 级 → 个股信号强制降级（即使个股 A 级也降为 B 级）
    """
    GRADE_A = "A"   # 优质板块回踩：缩量回踩均线 + 板块内多数个股同步回踩 + 支撑明确
    GRADE_B = "B"   # 中等板块回踩：放量回踩但板块指数守住关键位 + 部分个股破位
    GRADE_C = "C"   # 差质板块回踩：板块指数放量破位 + 多数个股破位 + 支撑失效


@dataclass
class SectorPullbackAssessment:
    """板块级回踩质量评估结果。"""
    sector_code: str
    quality: SectorPullbackQuality
    # 板块指数级指标
    near_ma: bool                          # 是否回踩均线
    volume_shrink: bool                    # 是否缩量
    ma_rising: bool                        # 均线是否上升
    is_breakdown: bool                     # 是否破位
    # 板块内个股一致性
    stock_pullback_consistency: float      # 板块内个股回踩一致性 [0, 1]
    breakdown_stock_ratio: float           # 破位个股占比
    # 关键支撑
    support_level: float                   # 关键支撑位
    support_held: bool                     # 是否守住支撑
    # 个股级信号加成规则（联动 §3.8 传导映射）
    stock_signal_modifier: float           # 个股信号调整系数（A=1.2/B=1.0/C=0.3）


def evaluate_sector_pullback_quality(
    sector_index_close: np.ndarray,         # 板块指数收盘价序列
    sector_index_volume: np.ndarray,        # 板块指数成交量序列
    sector_stocks_pullback: list[dict],     # 板块内个股回踩状态 [{symbol, near_ma, is_breakdown, ...}]
    sector_code: str = "",
    ma_period: int = 20,
    volume_shrink_threshold: float = 0.8,
    support_lookback: int = 60,             # 支撑位回看周期
    breakdown_threshold: float = 0.03,      # 破位阈值（跌破均线 3%）
) -> SectorPullbackAssessment:
    """板块级回踩质量评估——扩展 41_buy_flow.md §3.2 个股级。

    板块级 vs 个股级差异：
    - 个股级（41_buy_flow.md §3.2）：单只股票 OHLCV
    - 板块级（本节）：板块指数 OHLCV + 板块内个股一致性

    板块级 A/B/C 判定规则：
    - A 级（优质板块回踩）：
      * 板块指数缩量回踩均线
      * 均线方向向上
      * 板块内 ≥60% 个股同步回踩（一致性高）
      * 破位个股 <10%
      * 守住关键支撑位
    - B 级（中等板块回踩）：
      * 板块指数放量回踩但均线方向仍向上
      * 板块内 30-60% 个股同步回踩
      * 破位个股 10-30%
      * 守住关键支撑位
    - C 级（差质板块回踩）：
      * 板块指数放量破位（跌破均线 >3%）
      * 均线方向向下
      * 破位个股 >30%
      * 关键支撑失效

    与个股级信号的协同（§3.8 传导映射）：
    - 板块 A + 个股 A → 买入信号 ×1.2 加成
    - 板块 A + 个股 B → 买入信号 ×1.0
    - 板块 B + 个股 A → 买入信号 ×1.0
    - 板块 B + 个股 B → 买入信号 ×0.7
    - 板块 C + 个股 A → 买入信号 ×0.3（强制降级）
    - 板块 C + 个股 B/C → 不买入
    """
    if len(sector_index_close) < ma_period + 1:
        return SectorPullbackAssessment(
            sector_code=sector_code, quality=SectorPullbackQuality.GRADE_C,
            near_ma=False, volume_shrink=False, ma_rising=False, is_breakdown=True,
            stock_pullback_consistency=0.0, breakdown_stock_ratio=1.0,
            support_level=float(sector_index_close[-1]) if len(sector_index_close) > 0 else 0.0,
            support_held=False, stock_signal_modifier=0.3,
        )

    # 均线
    ma = np.convolve(sector_index_close, np.ones(ma_period) / ma_period, mode="valid")
    current_price = sector_index_close[-1]
    current_ma = ma[-1]
    prev_ma = ma[-2] if len(ma) > 1 else current_ma

    # 量比（vs 5 日均量）
    if len(sector_index_volume) >= 6:
        avg_vol_5d = np.mean(sector_index_volume[-6:-1])
    else:
        avg_vol_5d = np.mean(sector_index_volume) if len(sector_index_volume) > 0 else 0
    volume_ratio = sector_index_volume[-1] / avg_vol_5d if avg_vol_5d > 0 else 1.0
    is_volume_shrink = volume_ratio < volume_shrink_threshold

    # 回踩均线判定
    near_ma = abs(current_price - current_ma) / current_ma < 0.02

    # 均线方向
    ma_rising = current_ma > prev_ma

    # 破位判定
    is_breakdown = current_price < current_ma * (1 - breakdown_threshold)

    # 关键支撑位（近 support_lookback 日的最低点，排除最近 5 日避免噪声）
    lookback = min(support_lookback, len(sector_index_close))
    if lookback > 5:
        support_level = float(np.min(sector_index_close[-lookback:-5]))
    else:
        support_level = float(np.min(sector_index_close))
    support_held = current_price >= support_level * 0.98  # 容忍 2% 假跌破

    # 板块内个股一致性
    total_stocks = len(sector_stocks_pullback)
    if total_stocks > 0:
        near_ma_count = sum(1 for s in sector_stocks_pullback if s.get("near_ma", False))
        breakdown_count = sum(1 for s in sector_stocks_pullback if s.get("is_breakdown", False))
        stock_pullback_consistency = near_ma_count / total_stocks
        breakdown_stock_ratio = breakdown_count / total_stocks
    else:
        stock_pullback_consistency = 0.0
        breakdown_stock_ratio = 1.0

    # ===== 综合判定 =====
    if is_breakdown or not support_held or breakdown_stock_ratio > 0.30:
        quality = SectorPullbackQuality.GRADE_C
        modifier = 0.3
    elif (near_ma and is_volume_shrink and ma_rising and
          stock_pullback_consistency >= 0.60 and breakdown_stock_ratio < 0.10):
        quality = SectorPullbackQuality.GRADE_A
        modifier = 1.2
    elif near_ma and ma_rising and stock_pullback_consistency >= 0.30:
        quality = SectorPullbackQuality.GRADE_B
        modifier = 1.0
    else:
        quality = SectorPullbackQuality.GRADE_C
        modifier = 0.3

    return SectorPullbackAssessment(
        sector_code=sector_code,
        quality=quality,
        near_ma=near_ma,
        volume_shrink=is_volume_shrink,
        ma_rising=ma_rising,
        is_breakdown=is_breakdown,
        stock_pullback_consistency=float(stock_pullback_consistency),
        breakdown_stock_ratio=float(breakdown_stock_ratio),
        support_level=support_level,
        support_held=support_held,
        stock_signal_modifier=modifier,
    )
```

### 3.4 调整周期追踪（BM-SEL-09，进度 ≥80% 激活分批）

```python
@dataclass
class SectorAdjustmentProgress:
    """板块调整周期追踪结果（BM-SEL-09）。"""
    sector_code: str
    high_price: float                      # 调整起始高点
    low_price: float                       # 调整低点
    current_price: float
    adjustment_progress: float             # 调整进度 [0, 1+]（>1 为破位）
    progress_pct: float                    # 调整进度百分比
    days_in_adjustment: int                # 调整天数
    # 分批建仓激活
    batch_activation: bool                 # 是否激活分批建仓
    activation_reason: str                 # 激活/未激活原因
    # 质量等级联动（来自 §3.3）
    pullback_quality: SectorPullbackQuality = None


def track_sector_adjustment(
    sector_code: str,
    sector_close: np.ndarray,               # 板块收盘价序列
    high_lookback: int = 60,                # 高点回看周期
    activation_threshold: float = 0.80,     # 进度 ≥80% 激活
    min_adjustment_days: int = 5,           # 最小调整天数
    early_block_threshold: float = 0.40,    # 初期 <40% 直接拦截
    breakdown_warning_threshold: float = 1.10,  # 进度 >110% 破位警告
) -> SectorAdjustmentProgress:
    """板块调整周期追踪——BM-SEL-09。

    调整进度公式：
        progress = (high - current) / (high - low)

    进度解释：
    - progress = 0：板块刚见高点，调整刚开始
    - progress = 0.5：板块调整到中段
    - progress = 1.0：板块调整到低点
    - progress > 1.0：板块创新低（破位，可能转入下跌趋势）

    激活规则（BM-SEL-09）：
    - progress < 40% → 直接拦截（初期，调整未充分）
    - 40% ≤ progress < 80% → 观望
    - progress ≥ 80% → 激活分批建仓信号
    - progress > 110% → 破位警告（不激活，可能不是调整而是下跌）

    与 §3.3 板块回踩质量联动：
    - 激活分批建仓后，仍需通过 §3.3 评估回踩质量
    - A 级回踩 + 进度 ≥80% → 全仓位分批
    - B 级回踩 + 进度 ≥80% → 半仓位分批
    - C 级回踩 → 不激活（即使进度 ≥80%）
    """
    if len(sector_close) < 5:
        return SectorAdjustmentProgress(
            sector_code=sector_code, high_price=0, low_price=0,
            current_price=float(sector_close[-1]) if len(sector_close) > 0 else 0,
            adjustment_progress=0, progress_pct=0, days_in_adjustment=0,
            batch_activation=False, activation_reason="insufficient_data",
        )

    lookback = min(high_lookback, len(sector_close))
    lookback_prices = sector_close[-lookback:]
    high_idx = int(np.argmax(lookback_prices))
    high_price = float(lookback_prices[high_idx])

    # 低点：高点之后的最低点
    post_high_prices = lookback_prices[high_idx:]
    if len(post_high_prices) < 2:
        low_price = high_price * 0.95
    else:
        low_price = float(np.min(post_high_prices))

    current_price = float(sector_close[-1])
    days_in_adjustment = len(lookback_prices) - high_idx - 1

    # 调整进度
    if high_price - low_price > 1e-8:
        progress = (high_price - current_price) / (high_price - low_price)
    else:
        progress = 0.0

    # 激活判定
    batch_activation = False
    if days_in_adjustment < min_adjustment_days:
        activation_reason = f"adjustment_too_short({days_in_adjustment}d<{min_adjustment_days}d)"
    elif progress > breakdown_warning_threshold:
        activation_reason = f"breakdown_warning(progress={progress:.1%}>{breakdown_warning_threshold:.0%})_破位风险"
    elif progress < early_block_threshold:
        activation_reason = f"early_block(progress={progress:.1%}<{early_block_threshold:.0%})_初期拦截"
    elif progress >= activation_threshold:
        batch_activation = True
        activation_reason = f"progress_activated({progress:.1%}>={activation_threshold:.0%})"
    else:
        activation_reason = f"progress_observing({progress:.1%})_观望"

    return SectorAdjustmentProgress(
        sector_code=sector_code,
        high_price=high_price,
        low_price=low_price,
        current_price=current_price,
        adjustment_progress=float(progress),
        progress_pct=float(progress * 100),
        days_in_adjustment=days_in_adjustment,
        batch_activation=batch_activation,
        activation_reason=activation_reason,
    )
```

### 3.5 轮动序列追踪

```python
class SectorRotationStage(Enum):
    """板块轮动阶段标记（板块轮动四阶段模型 + 底部）。"""
    LAUNCH = "启动"            # 板块刚启动，领涨初现
    ACCELERATION = "加速"      # 板块加速上涨，主升浪
    PEAKING = "见顶"           # 板块见顶，放量滞涨
    PULLBACK = "回落"          # 板块回落调整
    BOTTOMING = "底部"         # 板块筑底，蓄势待发


class RotationRole(Enum):
    """板块在轮动序列中的角色。"""
    LEADER = "领涨"            # 板块率先启动，领涨大盘
    FOLLOWER = "跟涨"          # 跟随领涨板块上涨
    CATCH_UP = "补涨"          # 滞后板块补涨（往往是轮动末期信号）
    LAGGARD = "领跌"           # 板块率先下跌，领跌大盘


@dataclass
class SectorRotationTrack:
    """板块轮动序列追踪结果。"""
    sector_code: str
    stage: SectorRotationStage              # 当前轮动阶段
    role: RotationRole                       # 当前轮动角色
    stage_duration: int                      # 当前阶段持续天数
    # 历史模式匹配
    matched_historical_pattern: str          # 匹配的历史轮动模式名
    pattern_confidence: float                # 模式匹配置信度 [0, 1]
    # 轮动序列位置
    sequence_position: int                   # 在当前轮动序列中的位置（1=最先启动）
    next_likely_sectors: list[str]           # 基于历史模式，下一个可能启动的板块


def detect_rotation_stage(
    sector_close: np.ndarray,
    sector_volume: np.ndarray,
    benchmark_close: np.ndarray,
    window_short: int = 5,
    window_long: int = 20,
) -> SectorRotationStage:
    """轮动阶段检测——四阶段模型（启动/加速/见顶/回落）+ 底部。

    判定逻辑：
    - 启动：板块 RS 从 <1 升至 >1，量能温和放大
    - 加速：板块 RS >1.1，量能持续放大，均线多头排列
    - 见顶：板块高位放量滞涨（量增价不增）
    - 回落：板块 RS <1，量能萎缩
    - 底部：板块长期低位横盘，量能极度萎缩
    """
    if len(sector_close) < window_long + 1 or len(benchmark_close) < window_long + 1:
        return SectorRotationStage.BOTTOMING

    # 相对强度变化
    rs_now = (1 + (sector_close[-1] / sector_close[-window_short] - 1)) / \
             (1 + (benchmark_close[-1] / benchmark_close[-window_short] - 1))
    rs_prev = (1 + (sector_close[-window_short] / sector_close[-window_long] - 1)) / \
              (1 + (benchmark_close[-window_short] / benchmark_close[-window_long] - 1))

    # 量能变化
    vol_now = np.mean(sector_volume[-window_short:])
    vol_prev = np.mean(sector_volume[-window_long:-window_short]) if len(sector_volume) > window_long else vol_now
    vol_ratio = vol_now / vol_prev if vol_prev > 0 else 1.0

    # 价格变化
    price_change_short = sector_close[-1] / sector_close[-window_short] - 1
    price_change_long = sector_close[-1] / sector_close[-window_long] - 1

    # 见顶：高位放量滞涨（最危险，优先判定）
    if price_change_long > 0.15 and abs(price_change_short) < 0.02 and vol_ratio > 1.3:
        return SectorRotationStage.PEAKING

    # 加速：RS > 1.1 + 量能放大 + 上涨
    if rs_now > 1.1 and vol_ratio > 1.1 and price_change_short > 0.03:
        return SectorRotationStage.ACCELERATION

    # 启动：RS 从 <1 升至 >1
    if rs_prev < 1.0 and rs_now >= 1.0 and price_change_short > 0:
        return SectorRotationStage.LAUNCH

    # 回落：RS < 1 + 下跌
    if rs_now < 0.95 and price_change_short < -0.02:
        return SectorRotationStage.PULLBACK

    # 底部：长期低位横盘 + 量能萎缩
    if abs(price_change_long) < 0.05 and vol_ratio < 0.7:
        return SectorRotationStage.BOTTOMING

    # 默认分类
    if rs_now > 1.0:
        return SectorRotationStage.ACCELERATION
    return SectorRotationStage.PULLBACK


def detect_rotation_role(
    sector_returns: dict[str, float],           # {板块代码: 当日收益}
    sector_returns_prev: dict[str, float],      # {板块代码: 前日收益}
    target_sector: str,
) -> RotationRole:
    """板块在轮动序列中的角色检测。

    轮动序列（领涨→跟涨→补涨→领跌）：
    - 领涨：当日板块收益排名前 10%
    - 跟涨：领涨板块启动后 1-2 日跟进，排名前 30%
    - 补涨：前日排名靠后，今日排名靠前（往往是轮动末期信号）
    - 领跌：连续 N 日板块收益排名后 10%
    """
    n_sectors = len(sector_returns)
    if n_sectors == 0:
        return RotationRole.FOLLOWER

    sorted_sectors = sorted(sector_returns.items(), key=lambda x: x[1], reverse=True)
    target_rank = next(
        (i + 1 for i, (code, _) in enumerate(sorted_sectors) if code == target_sector),
        n_sectors
    )

    top_10pct = max(1, n_sectors // 10)
    bottom_10pct = max(1, n_sectors // 10)
    top_30pct = max(1, n_sectors * 3 // 10)

    # 领跌（优先判定）
    if target_rank > n_sectors - bottom_10pct:
        return RotationRole.LAGGARD

    # 领涨：排名前 10%
    if target_rank <= top_10pct:
        return RotationRole.LEADER

    # 补涨：前日排名靠后，今日排名靠前（轮动末期信号）
    sorted_prev = sorted(sector_returns_prev.items(), key=lambda x: x[1], reverse=True)
    prev_rank = next(
        (i + 1 for i, (code, _) in enumerate(sorted_prev) if code == target_sector),
        n_sectors
    )
    if prev_rank > n_sectors * 0.6 and target_rank <= top_30pct:
        return RotationRole.CATCH_UP

    # 跟涨：排名前 30%
    if target_rank <= top_30pct:
        return RotationRole.FOLLOWER

    return RotationRole.FOLLOWER


def match_historical_rotation_pattern(
    current_pattern: dict[str, RotationRole],   # {板块代码: 当前角色}
    historical_patterns: list[dict],            # 历史轮动模式列表 [{name, roles, next_sectors}]
    min_confidence: float = 0.6,
) -> tuple[str, float, list[str]]:
    """历史轮动模式匹配——基于板块角色序列匹配历史相似轮动。

    返回 (匹配模式名, 置信度, 下一个可能启动的板块列表)

    匹配方法：
    - 提取当前领涨/跟涨板块角色序列
    - 与历史模式中同期序列做相似度比较
    - 相似度 = 角色匹配数 / 总板块数
    - 置信度 ≥ 0.6 才返回有效匹配
    """
    if not historical_patterns:
        return "no_historical_data", 0.0, []

    best_match = None
    best_score = 0.0

    for pattern in historical_patterns:
        historical_roles = pattern.get("roles", {})
        if not historical_roles:
            continue

        # 角色匹配
        matched = 0
        total = 0
        for sector, role in current_pattern.items():
            if sector in historical_roles:
                total += 1
                if historical_roles[sector] == role:
                    matched += 1

        score = matched / total if total > 0 else 0.0
        if score > best_score:
            best_score = score
            best_match = pattern

    if best_match is None or best_score < min_confidence:
        return "no_match", float(best_score), []

    return (
        best_match.get("name", "unnamed"),
        float(best_score),
        best_match.get("next_sectors", []),
    )
```

### 3.6 虹吸态识别

```python
@dataclass
class SiphonState:
    """板块虹吸态识别结果。"""
    is_siphon: bool                         # 是否处于虹吸态
    siphon_sectors: list[str]               # 虹吸龙头板块代码列表
    siphon_intensity: float                 # 虹吸强度
    # 影响范围
    drained_sectors: list[str]              # 被虹吸（资金流出）的板块列表
    drained_outflow_ratio: float            # 被虹吸板块资金流出比例
    # 持续性
    siphon_duration: int                    # 虹吸持续天数
    sustainability: str                     # "HIGH" / "MEDIUM" / "LOW"


def detect_siphon_state(
    sector_turnovers: dict[str, float],         # {板块代码: 当日成交额}
    sector_turnovers_prev: dict[str, float],    # {板块代码: 前日成交额}
    total_market_turnover: float,               # 全市场成交额
    total_market_turnover_prev: float,          # 全市场前日成交额
    siphon_threshold: float = 0.15,             # 虹吸强度阈值
    min_siphon_sectors: int = 1,                # 最少虹吸板块数
    siphon_concentration_ratio: float = 0.20,   # 龙头板块成交额占比阈值
) -> SiphonState:
    """板块虹吸态识别——龙头板块吸金效应。

    虹吸态定义：
        虹吸强度 = Σ(龙头板块成交额增量) / 全市场成交额增量
        当 虹吸强度 > 阈值 且 龙头板块成交额占比 > 20% → 虹吸态
        → 非龙头板块资金被虹吸流出

    A 股板块虹吸效应（游资集中度模型）：
    - 龙头板块（1-3 个）成交额占比突变（>20%）
    - 非龙头板块成交额萎缩
    - 虹吸态期间，非龙头板块即使有 alpha 也难上涨

    识别规则：
    - siphon_intensity > 0.15 → 虹吸态
    - 虹吸龙头板块成交额占比 > 20%
    - 非龙头板块成交额萎缩（增量 < 0）

    与 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §1.3 的关系：
    情绪周期是隐形驱动，虹吸态是其可观测的资金面投影——
    疯狂期龙头板块吸金、退潮期资金从非龙头板块流出。
    """
    market_delta = total_market_turnover - total_market_turnover_prev
    if abs(market_delta) < 1e-8:
        return SiphonState(
            is_siphon=False, siphon_sectors=[], siphon_intensity=0.0,
            drained_sectors=[], drained_outflow_ratio=0.0,
            siphon_duration=0, sustainability="LOW",
        )

    # 计算各板块成交额增量
    sector_deltas = {}
    for code, turnover in sector_turnovers.items():
        prev = sector_turnovers_prev.get(code, 0)
        sector_deltas[code] = turnover - prev

    # 识别龙头板块（成交额占比 > 阈值 且 增量为正）
    siphon_sectors = []
    for code, turnover in sector_turnovers.items():
        if (turnover / total_market_turnover > siphon_concentration_ratio
                and sector_deltas.get(code, 0) > 0):
            siphon_sectors.append(code)

    if len(siphon_sectors) < min_siphon_sectors:
        return SiphonState(
            is_siphon=False, siphon_sectors=[], siphon_intensity=0.0,
            drained_sectors=[], drained_outflow_ratio=0.0,
            siphon_duration=0, sustainability="LOW",
        )

    # 虹吸强度 = Σ(龙头板块成交额增量) / 全市场成交额增量
    siphon_delta = sum(sector_deltas[code] for code in siphon_sectors)
    siphon_intensity = siphon_delta / market_delta if market_delta != 0 else 0.0

    # 识别被虹吸板块（非龙头 + 增量为负）
    drained_sectors = [
        code for code, delta in sector_deltas.items()
        if code not in siphon_sectors and delta < 0
    ]

    drained_outflow = sum(abs(sector_deltas[code]) for code in drained_sectors)
    drained_outflow_ratio = drained_outflow / total_market_turnover if total_market_turnover > 0 else 0.0

    # 虹吸态判定
    is_siphon = siphon_intensity > siphon_threshold

    # 持续性评估（基于虹吸强度）
    if siphon_intensity > 0.30:
        sustainability = "HIGH"
    elif siphon_intensity > 0.20:
        sustainability = "MEDIUM"
    else:
        sustainability = "LOW"

    return SiphonState(
        is_siphon=is_siphon,
        siphon_sectors=siphon_sectors,
        siphon_intensity=float(siphon_intensity),
        drained_sectors=drained_sectors,
        drained_outflow_ratio=float(drained_outflow_ratio),
        siphon_duration=0,  # 需要历史状态追踪（Phase 1.5+）
        sustainability=sustainability,
    )
```

### 3.7 板块资金流算法

```python
@dataclass
class SectorCapitalFlow:
    """板块资金流计算结果。"""
    sector_code: str
    # 当日资金流
    main_net_inflow: float               # 主力净流入（元）
    retail_net_inflow: float             # 散户净流入（元）
    northbound_net_inflow: float         # 北向净流入（元）
    # 资金流趋势（5/10/20 日均线）
    ma5_inflow: float
    ma10_inflow: float
    ma20_inflow: float
    trend_direction: str                 # "inflow" / "outflow" / "neutral"
    trend_strength: float                # 趋势强度 [0, 1]
    # 资金流强度（联动 §3.2 板块强度四维度之一）
    flow_intensity: float                # main_net_inflow / total_turnover


def calc_main_net_inflow(
    large_order_buy: float,              # 大单买入额（元）
    large_order_sell: float,             # 大单卖出额（元）
) -> float:
    """主力净流入 = 大单买入 - 大单卖出。

    A 股大单定义（同花顺/东方财富标准）：
    - 超大单：单笔成交金额 ≥ 1000 万元
    - 大单：单笔成交金额 100-1000 万元
    - 中单：单笔成交金额 4-100 万元
    - 小单：单笔成交金额 < 4 万元

    主力 = 超大单 + 大单（即单笔 ≥ 100 万元）
    """
    return large_order_buy - large_order_sell


def calc_sector_capital_flow(
    sector_code: str,
    stock_capital_flows: list[dict],     # 板块内个股资金流 [{symbol, main_net, retail_net, northbound_net, turnover}]
    history_main_inflow: np.ndarray,     # 历史主力净流入序列
) -> SectorCapitalFlow:
    """板块资金流算法——板块内个股资金流聚合 + 趋势分析。

    板块资金流 = Σ(板块内个股主力净流入)

    资金流趋势（5/10/20 日均线）：
    - MA5 > MA10 > MA20 → 强势流入
    - MA5 < MA10 < MA20 → 强势流出
    - 交叉 → 趋势转换

    与 §3.2 板块强度的协同：
    - 资金流强度是板块强度四维度之一（权重 25%）
    - 资金流趋势 → 板块强度评分的趋势加成
    """
    # 聚合个股资金流
    main_net = sum(s.get("main_net", 0) for s in stock_capital_flows)
    retail_net = sum(s.get("retail_net", 0) for s in stock_capital_flows)
    northbound_net = sum(s.get("northbound_net", 0) for s in stock_capital_flows)
    total_turnover = sum(s.get("turnover", 0) for s in stock_capital_flows)

    # 资金流强度
    flow_intensity = main_net / total_turnover if total_turnover > 0 else 0.0

    # 趋势分析
    if len(history_main_inflow) >= 20:
        ma5 = float(np.mean(history_main_inflow[-5:]))
        ma10 = float(np.mean(history_main_inflow[-10:]))
        ma20 = float(np.mean(history_main_inflow[-20:]))

        if ma5 > ma10 > ma20 and ma5 > 0:
            trend_direction = "inflow"
            trend_strength = float(min(1.0, (ma5 - ma20) / (abs(ma20) + 1.0)))
        elif ma5 < ma10 < ma20 and ma5 < 0:
            trend_direction = "outflow"
            trend_strength = float(min(1.0, (ma20 - ma5) / (abs(ma20) + 1.0)))
        else:
            trend_direction = "neutral"
            trend_strength = 0.0
    else:
        ma5 = ma10 = ma20 = float(main_net)
        trend_direction = "inflow" if main_net > 0 else ("outflow" if main_net < 0 else "neutral")
        trend_strength = 0.0

    return SectorCapitalFlow(
        sector_code=sector_code,
        main_net_inflow=float(main_net),
        retail_net_inflow=float(retail_net),
        northbound_net_inflow=float(northbound_net),
        ma5_inflow=ma5,
        ma10_inflow=ma10,
        ma20_inflow=ma20,
        trend_direction=trend_direction,
        trend_strength=trend_strength,
        flow_intensity=float(flow_intensity),
    )
```

### 3.8 板块→个股传导映射

```python
@dataclass
class SectorStockConduction:
    """板块→个股传导映射结果。"""
    symbol: str
    sector_code: str
    # 板块强度（来自 §3.2）
    sector_strength_score: float
    sector_strength_level: str            # "STRONG" / "MEDIUM" / "WEAK"
    # 个股信号加成
    base_signal_score: float              # 个股原始信号得分 [0, 100]
    enhanced_signal_score: float          # 板块加成后的信号得分
    signal_enhancement: float             # 信号加成系数
    # 传导延迟
    conduction_delay_days: int            # 估计的传导延迟（板块领先个股天数）
    # 传导强度衰减
    conduction_decay: float               # 传导强度衰减系数 [0, 1]
    # 综合买入建议
    buy_recommendation: str               # "STRONG_BUY" / "BUY" / "HOLD" / "AVOID"


def estimate_conduction_delay(
    sector_close: np.ndarray,
    stock_close: np.ndarray,
    max_delay: int = 5,
) -> int:
    """传导延迟估计——板块领先个股多少天。

    方法：互相关分析
    - 计算板块收益与个股收益在不同延迟下的相关系数
    - 取最大相关系数对应的延迟

    A 股板块→个股传导规律（2026-08 研究）：
    - 龙头股：延迟 0-1 天（与板块同步）
    - 跟随股：延迟 1-3 天
    - 边缘股：延迟 3-5 天
    """
    if len(sector_close) < max_delay + 10 or len(stock_close) < max_delay + 10:
        return 0

    # 计算日收益率
    sector_ret = np.diff(np.log(sector_close[sector_close > 0]))
    stock_ret = np.diff(np.log(stock_close[stock_close > 0]))

    min_len = min(len(sector_ret), len(stock_ret))
    if min_len < max_delay + 5:
        return 0
    sector_ret = sector_ret[-min_len:]
    stock_ret = stock_ret[-min_len:]

    best_corr = -1
    best_delay = 0

    for delay in range(max_delay + 1):
        if delay == 0:
            if len(sector_ret) >= 2:
                corr = float(np.corrcoef(sector_ret, stock_ret)[0, 1])
            else:
                corr = 0
        else:
            if len(sector_ret[:-delay]) >= 2:
                corr = float(np.corrcoef(sector_ret[:-delay], stock_ret[delay:])[0, 1])
            else:
                corr = 0

        if not np.isnan(corr) and corr > best_corr:
            best_corr = corr
            best_delay = delay

    return best_delay


def calc_conduction_decay(
    conduction_delay: int,
) -> float:
    """传导强度衰减——延迟越长，传导强度越弱。

    衰减公式：
        decay = exp(-delay / 3)

    - delay=0：decay=1.00（无衰减，板块与个股同步）
    - delay=1：decay=0.72
    - delay=3：decay=0.37
    - delay=5：decay=0.19
    """
    return float(np.exp(-conduction_delay / 3.0))


def map_sector_to_stock_signal(
    symbol: str,
    sector_code: str,
    base_signal_score: float,                   # 个股原始信号得分 [0, 100]
    sector_strength: SectorStrength,             # §3.2 板块强度
    sector_pullback: SectorPullbackAssessment,   # §3.3 板块回踩质量
    sector_close: np.ndarray,
    stock_close: np.ndarray,
    siphon_state: SiphonState = None,            # §3.6 虹吸态（可选）
) -> SectorStockConduction:
    """板块→个股传导映射——板块强度增强个股信号。

    传导逻辑：
    1. 板块强 + 个股强 = 买入信号增强（加成系数 >1）
    2. 板块弱 + 个股强 = 买入信号衰减（加成系数 <1）
    3. 板块强 + 个股弱 = 观望（板块正吸金，但个股未启动）
    4. 板块弱 + 个股弱 = 不买入

    板块回踩质量（§3.3）的协同：
    - 板块 A 级回踩 → 个股信号 ×1.2
    - 板块 B 级回踩 → 个股信号 ×1.0
    - 板块 C 级回踩 → 个股信号 ×0.3

    虹吸态（§3.6）的影响：
    - 个股所在板块是虹吸龙头 → 信号增强（×1.2）
    - 个股所在板块被虹吸 → 信号衰减（×0.5），即使个股自身强也难涨

    综合加成系数 = 板块强度加成 × 板块回踩质量加成 × 传导衰减 × 虹吸态加成
    """
    # 板块强度加成
    if sector_strength.strength_level == "STRONG":
        strength_enhancement = 1.15
    elif sector_strength.strength_level == "MEDIUM":
        strength_enhancement = 1.0
    else:  # WEAK
        strength_enhancement = 0.6

    # 板块回踩质量加成（来自 §3.3，A=1.2 / B=1.0 / C=0.3）
    quality_modifier = sector_pullback.stock_signal_modifier

    # 传导延迟与衰减
    delay = estimate_conduction_delay(sector_close, stock_close)
    decay = calc_conduction_decay(delay)

    # 虹吸态影响
    siphon_modifier = 1.0
    if siphon_state and siphon_state.is_siphon:
        if sector_code in siphon_state.siphon_sectors:
            siphon_modifier = 1.2  # 虹吸龙头板块加成
        elif sector_code in siphon_state.drained_sectors:
            siphon_modifier = 0.5  # 被虹吸板块衰减

    # 综合信号加成
    signal_enhancement = strength_enhancement * quality_modifier * decay * siphon_modifier
    enhanced_score = base_signal_score * signal_enhancement
    enhanced_score = max(0, min(100, enhanced_score))  # 截断到 [0, 100]

    # 买入建议
    if enhanced_score >= 80 and sector_strength.strength_level != "WEAK":
        recommendation = "STRONG_BUY"
    elif enhanced_score >= 60 and sector_pullback.quality != SectorPullbackQuality.GRADE_C:
        recommendation = "BUY"
    elif enhanced_score >= 40:
        recommendation = "HOLD"
    else:
        recommendation = "AVOID"

    return SectorStockConduction(
        symbol=symbol,
        sector_code=sector_code,
        sector_strength_score=sector_strength.composite_score,
        sector_strength_level=sector_strength.strength_level,
        base_signal_score=float(base_signal_score),
        enhanced_signal_score=float(enhanced_score),
        signal_enhancement=float(signal_enhancement),
        conduction_delay_days=delay,
        conduction_decay=decay,
        buy_recommendation=recommendation,
    )
```

### 3.9 与下游的协同

板块轮动必须与以下下游模块协同：

- **[41_buy_flow](41_buy_flow.md) §3.2 买入流**：本节 §3.3 板块级 `evaluate_sector_pullback_quality` 扩展 41_buy_flow.md §3.2 个股级 `evaluate_pullback_quality`。买入流消费板块级 A/B/C 作为个股级的上游门控——板块 C 级时，即使个股 A 级也降级为 B 级（§3.3 `stock_signal_modifier=0.3`）。
- **[24_daban_strategy_detail](24_daban_strategy_detail.md) §3.7 打板策略**：打板策略 §3.7 `classify_sector_state`（WyckoffTradingAgent 2026-07）与本节 §3.2 `evaluate_sector_strength` 互补——前者是板块状态分类（共识高潮/派发风险等），后者是板块强度评分（0-100）。打板策略消费虹吸态（§3.6）识别龙头板块吸金效应。
- **[25_multifactor_strategy_detail](25_multifactor_strategy_detail.md) 多因子策略**：多因子策略 §3.2 行业中性化是被动行业暴露控制；本节板块轮动是主动板块选择。两者正交——行业中性化消除行业 beta 污染，板块轮动提供板块 alpha 加成。
- **[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §1.3 情绪周期**：板块轮动是情绪周期的具象化载体。情绪周期（冰点/反核/主升/疯狂/退潮）驱动资金在板块间轮动，板块轮动序列（§3.5）是情绪周期的可观测投影。
- **[52_backtest_framework_docking](52_backtest_framework_docking.md) A 股 mask-first 前置设计**：本节 §3.2 `calc_advancer_ratio` 实现板块级 mask-first 涨跌停过滤，与回测框架的 mask-first 设计一致。

### 3.10 多元 Hawkes 传染矩阵

**背景**：板块间情绪传染建模——不仅看单个板块的涨跌，更看板块间的事件传染效应（如龙头板块涨停潮如何激发跟风板块涨停潮）。Hawkes 过程是自激发点过程，事件的发生会提升后续事件的瞬时强度，自然刻画"事件簇"现象。多元 Hawkes 把单板块自激发扩展为跨板块互激发——龙头板块的事件不仅抬高自身后续事件强度，也通过激发矩阵抬高其他板块的强度。

**算法说明**：

- **一元 Hawkes 强度**：λ_i(t) = λ₀_i + Σ_j ∫ α_ij · exp(-β_ij · (t - s)) · dN_j(s)
- **离散形式**：λ_i(t) = λ₀_i + Σ_j Σ_{t_j < t} α_ij · exp(-β_ij · (t - t_j))
- **多元 Hawkes 矩阵**：N 个板块间的 N×N 激发矩阵（α、β 均为 N×N）
  - α_ij：板块 j 事件对板块 i 的激发幅度（j→i 的传染强度）
  - β_ij：板块 j 事件对板块 i 的衰减速率（越大衰减越快）
- **分支比**：η_i = Σ_j α_ij / β_ij
  - η_i < 1：稳态（事件最终衰减）
  - η_i ≥ 1：爆发态（事件自激失控，传染失控）
- **传染爆发检测**：某板块 η_i 超过预警阈值（0.8）→ 传染爆发态

```python
from dataclasses import dataclass, field
from typing import Sequence
import numpy as np


@dataclass
class MultivariateHawkesParams:
    """多元 Hawkes 过程参数（N 板块 × N 板块 激发矩阵）。

    一元 Hawkes 强度公式：
        λ_i(t) = λ₀_i + Σ_j Σ_{t_j < t} α_ij · exp(-β_ij · (t - t_j))

    其中：
    - λ₀_i：板块 i 的基线强度（无条件事件发生率）
    - α_ij：板块 j 事件对板块 i 的激发幅度（j→i 的传染强度）
    - β_ij：板块 j 事件对板块 i 的衰减速率（越大衰减越快）
    - N：板块数（Phase 1.0 = 5 大核心板块；Phase 2.0 扩展到全 460 板块）

    分支比：
        η_i = Σ_j α_ij / β_ij
    - η_i < 1：稳态（事件最终衰减）
    - η_i ≥ 1：爆发态（事件自激失控，传染失控）
    """
    n_sectors: int                              # 板块数 N
    sector_codes: list[str]                     # 板块代码列表（长度 N）
    baseline: np.ndarray                        # 基线强度 λ₀，shape (N,)
    excitation: np.ndarray                      # 激发幅度矩阵 α，shape (N, N)
    decay: np.ndarray                           # 衰减速率矩阵 β，shape (N, N)


@dataclass
class HawkesIntensityVector:
    """多元 Hawkes 瞬时强度向量。"""
    timestamp: float                            # 时间戳（秒）
    sector_codes: list[str]                     # 板块代码列表
    intensity: np.ndarray                       # N 个板块的瞬时强度向量，shape (N,)
    above_baseline: list[bool]                  # 各板块强度是否超过基线（事件激发态）


def compute_hawkes_intensity_matrix(
    params: MultivariateHawkesParams,
    events: dict[str, list[float]],             # {板块代码: 事件时间戳列表}
    current_time: float,
) -> HawkesIntensityVector:
    """计算 N 个板块的瞬时强度向量。

    λ_i(t) = λ₀_i + Σ_j Σ_{t_j < t} α_ij · exp(-β_ij · (t - t_j))

    对每个板块 i：
    1. 取基线 λ₀_i
    2. 遍历所有板块 j 的事件历史
    3. 对每个 t_j < t，累加 α_ij · exp(-β_ij · (t - t_j))

    时间复杂度：O(N² · M)，M 为平均事件数。N=5 时极快，N=460 时需稀疏化/截断。

    与 §3.7 板块资金流算法的协同：
    - §3.7 的板块主力净流入脉冲（>5% 成交额的大单）作为 Hawkes 的事件输入
    - 资金流事件强度（inflow/outflow）映射为事件符号（正向/负向）
    """
    n = params.n_sectors

    intensity = params.baseline.copy()

    # 遍历每个激发源板块 j
    for j, src_code in enumerate(params.sector_codes):
        src_events = events.get(src_code, [])
        # 只考虑 current_time 之前的事件
        valid_events = [t for t in src_events if t < current_time]
        if not valid_events:
            continue

        # 对每个目标板块 i，累加激发项
        for i in range(n):
            alpha_ij = params.excitation[i, j]
            beta_ij = params.decay[i, j]
            if alpha_ij <= 0 or beta_ij <= 0:
                continue
            # Σ α_ij · exp(-β_ij · (t - t_j))
            excitation_sum = sum(
                alpha_ij * float(np.exp(-beta_ij * (current_time - t_j)))
                for t_j in valid_events
            )
            intensity[i] += excitation_sum

    above_baseline = [
        bool(intensity[i] > params.baseline[i] * 1.5)
        for i in range(n)
    ]

    return HawkesIntensityVector(
        timestamp=current_time,
        sector_codes=params.sector_codes,
        intensity=intensity,
        above_baseline=above_baseline,
    )


@dataclass
class BranchingRatioMatrix:
    """多元 Hawkes 分支比矩阵评估结果。"""
    sector_codes: list[str]
    branching_ratio: np.ndarray                 # 分支比向量 η_i = Σ_j α_ij/β_ij，shape (N,)
    ratio_matrix: np.ndarray                    # 详细 α_ij/β_ij 矩阵，shape (N, N)
    is_stable: list[bool]                       # 各板块是否稳态（η_i < 1）
    outbreak_sectors: list[str]                 # 爆发态板块（η_i ≥ 1）


def estimate_branching_ratio_matrix(
    params: MultivariateHawkesParams,
    stability_threshold: float = 1.0,
) -> BranchingRatioMatrix:
    """估计 N×N 分支比矩阵。

    分支比定义：
        η_i = Σ_j α_ij / β_ij

    含义：板块 i 上每个事件平均能激发多少个后续事件。
    - η_i < 1：稳态，事件最终衰减（每事件激发 < 1 个后续事件）
    - η_i ≥ 1：爆发态，事件自激失控（每事件激发 ≥ 1 个后续事件）

    与稳态判定：
    - stability_threshold 默认 1.0（Hawkes 理论稳态条件）
    - 实际传染爆发预警用更保守的阈值（0.8，见 detect_contagion_outbreak）
    """
    n = params.n_sectors

    # α_ij / β_ij 矩阵
    ratio_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if params.decay[i, j] > 1e-8:
                ratio_matrix[i, j] = params.excitation[i, j] / params.decay[i, j]

    # η_i = Σ_j α_ij / β_ij（行和）
    branching_ratio = ratio_matrix.sum(axis=1)

    is_stable = [bool(eta < stability_threshold) for eta in branching_ratio]
    outbreak_sectors = [
        params.sector_codes[i]
        for i in range(n)
        if branching_ratio[i] >= stability_threshold
    ]

    return BranchingRatioMatrix(
        sector_codes=params.sector_codes,
        branching_ratio=branching_ratio,
        ratio_matrix=ratio_matrix,
        is_stable=is_stable,
        outbreak_sectors=outbreak_sectors,
    )


@dataclass
class ContagionOutbreak:
    """板块传染爆发检测结果。"""
    is_outbreak: bool                           # 是否爆发
    outbreak_sectors: list[str]                 # 爆发源板块列表
    outbreak_intensity: float                   # 爆发强度（最大分支比）
    affected_sectors: list[str]                 # 受波及板块列表（强度被显著抬升）
    # 应对建议
    risk_level: str                             # "LOW" / "MEDIUM" / "HIGH" / "CRITICAL"
    recommendation: str                         # 应对建议（如 "暂停追高/降仓位/不动"）


def detect_contagion_outbreak(
    params: MultivariateHawkesParams,
    intensity: HawkesIntensityVector,
    branching_ratio_threshold: float = 0.8,     # 分支比预警阈值（< 1.0 保守预警）
    intensity_multiplier_threshold: float = 3.0,  # 强度超过基线 N 倍判定为受波及
) -> ContagionOutbreak:
    """检测传染爆发——分支比超过阈值且强度显著抬升。

    爆发判定规则：
    1. 分支比 η_i ≥ 0.8（保守阈值，提前预警）
    2. 该板块当前强度 > 基线 × 3（确认事件已实际激发）

    风险等级：
    - LOW：无爆发
    - MEDIUM：1 个板块爆发，影响范围小
    - HIGH：2-3 个板块爆发
    - CRITICAL：≥4 板块爆发或多板块 η ≥ 1（理论失控）

    与 §3.6 虹吸态识别的协同：
    - 虹吸态是资金面集中度（成交额维度）
    - 传染爆发是事件面激发强度（Hawkes 维度）
    - 两者可同时发生（虹吸龙头 + 传染爆发 = 极端情绪）
    """
    branching = estimate_branching_ratio_matrix(params, stability_threshold=1.0)

    outbreak_sectors = []
    outbreak_intensity = 0.0

    for i, code in enumerate(params.sector_codes):
        # 分支比超阈值 + 强度显著超基线
        if (branching.branching_ratio[i] >= branching_ratio_threshold
                and intensity.intensity[i] > params.baseline[i] * intensity_multiplier_threshold):
            outbreak_sectors.append(code)
            outbreak_intensity = max(outbreak_intensity, float(branching.branching_ratio[i]))

    # 受波及板块（强度被显著抬升但非爆发源）
    affected_sectors = []
    for i, code in enumerate(params.sector_codes):
        if code in outbreak_sectors:
            continue
        if intensity.intensity[i] > params.baseline[i] * intensity_multiplier_threshold:
            affected_sectors.append(code)

    # 风险等级
    n_outbreak = len(outbreak_sectors)
    has_unstable = any(eta >= 1.0 for eta in branching.branching_ratio)

    if n_outbreak == 0:
        risk_level = "LOW"
        recommendation = "正常交易，按既有板块强度信号操作"
    elif n_outbreak == 1 and not has_unstable:
        risk_level = "MEDIUM"
        recommendation = "关注爆发源板块的情绪扩散，非爆发板块正常操作"
    elif n_outbreak <= 3 and not has_unstable:
        risk_level = "HIGH"
        recommendation = "暂停追高爆发板块，受波及板块降仓位 50%"
    else:
        risk_level = "CRITICAL"
        recommendation = "全板块降仓位 50%+，禁止追高，等待分支比回落"

    return ContagionOutbreak(
        is_outbreak=n_outbreak > 0,
        outbreak_sectors=outbreak_sectors,
        outbreak_intensity=outbreak_intensity,
        affected_sectors=affected_sectors,
        risk_level=risk_level,
        recommendation=recommendation,
    )


@dataclass
class SectorContagionScore:
    """板块传染评分——综合强度+持续时间+波及范围。"""
    sector_code: str
    # 三个维度
    intensity_score: float                      # 强度维度评分 [0, 100]
    duration_score: float                       # 持续时间维度评分 [0, 100]
    spread_score: float                         # 波及范围维度评分 [0, 100]
    # 综合
    composite_score: float                      # 综合传染评分 [0, 100]
    contagion_level: str                        # "LOW" / "MEDIUM" / "HIGH" / "EXTREME"


def compute_sector_contagion_score(
    sector_code: str,
    params: MultivariateHawkesParams,
    intensity_series: list[HawkesIntensityVector],  # 时间序列强度向量
    sector_index: int,                          # 目标板块在 params 中的索引
    lookback_window: int = 20,                  # 评分回看窗口（事件数）
    intensity_threshold: float = 2.0,           # 强度超基线倍数阈值
    weights: dict = None,
) -> SectorContagionScore:
    """板块传染评分——综合强度+持续时间+波及范围。

    评分三维度：
    1. 强度维度（40%）：板块强度峰值 / 基线
       - 峰值 / 基线 ≥ 5 → 满分
       - 峰值 / 基线 = 1 → 0 分
    2. 持续时间维度（30%）：强度持续超阈值的事件数
       - 持续 ≥ lookback_window → 满分
       - 持续 0 → 0 分
    3. 波及范围维度（30%）：该板块对其他板块的激发贡献（α_ij 行和）
       - 激发 ≥ 5 个其他板块 → 满分
       - 激发 0 → 0 分

    与 §3.8 板块→个股传导映射的协同：
    - Hawkes 传染评分作为传导映射的权重加成
    - EXTREME 传染评分 → 个股信号 ×1.3（强传染加成）
    - HIGH 传染评分 → 个股信号 ×1.15
    - MEDIUM 传染评分 → 个股信号 ×1.0
    - LOW 传染评分 → 个股信号 ×0.9（无传染，衰减）
    """
    if weights is None:
        weights = {"intensity": 0.40, "duration": 0.30, "spread": 0.30}

    n = params.n_sectors
    lookback = min(lookback_window, len(intensity_series))

    # ===== 维度 1：强度维度 =====
    if lookback > 0:
        recent_intensities = [
            intensity_series[-(k + 1)].intensity[sector_index]
            for k in range(lookback)
        ]
        peak_intensity = max(recent_intensities)
        baseline = params.baseline[sector_index]
        peak_ratio = peak_intensity / baseline if baseline > 1e-8 else 1.0
        # peak_ratio ≥ 5 → 满分；= 1 → 0 分
        if peak_ratio >= 5.0:
            intensity_score = 100.0
        elif peak_ratio <= 1.0:
            intensity_score = 0.0
        else:
            intensity_score = (peak_ratio - 1.0) / 4.0 * 100
    else:
        intensity_score = 0.0

    # ===== 维度 2：持续时间维度 =====
    if lookback > 0:
        baseline = params.baseline[sector_index]
        sustained_count = sum(
            1 for k in range(lookback)
            if intensity_series[-(k + 1)].intensity[sector_index] > baseline * intensity_threshold
        )
        duration_score = min(100.0, sustained_count / max(1, lookback) * 100)
    else:
        duration_score = 0.0

    # ===== 维度 3：波及范围维度 =====
    # 该板块对其他板块的激发贡献（α_ij 行和的归一化）
    row_excitation = params.excitation[sector_index, :]
    # 显著激发阈值：α_ij > 行内最大值的 20%
    if row_excitation.max() > 1e-8:
        threshold = row_excitation.max() * 0.20
        spread_count = int(np.sum(row_excitation > threshold))
    else:
        spread_count = 0
    # spread_count ≥ 5 → 满分
    spread_score = min(100.0, spread_count / 5.0 * 100)

    # ===== 综合评分 =====
    composite = (
        weights["intensity"] * intensity_score +
        weights["duration"] * duration_score +
        weights["spread"] * spread_score
    )

    if composite >= 80:
        level = "EXTREME"
    elif composite >= 60:
        level = "HIGH"
    elif composite >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return SectorContagionScore(
        sector_code=sector_code,
        intensity_score=float(intensity_score),
        duration_score=float(duration_score),
        spread_score=float(spread_score),
        composite_score=float(composite),
        contagion_level=level,
    )
```

**上限声明**：
- **Phase 1.0**：仅做 5 大核心板块间的 Hawkes（如半导体/新能源/医药/消费/金融），计算量限制（N=5 → 25 维参数矩阵，实时计算可行）
- **Phase 2.0**：扩展到全 460 板块（需稀疏化处理 + GPU 加速；N=460 → 211600 维参数矩阵，无法稠密计算）

**与其他小节的协同**：
- **与 §3.7 板块资金流算法的协同**：§3.7 的板块主力净流入脉冲（>5% 成交额的大单）作为 Hawkes 的事件输入；资金流趋势（inflow/outflow）决定事件符号。
- **与 §3.8 板块→个股传导映射的协同**：Hawkes 传染评分（`SectorContagionScore.contagion_level`）作为传导映射的权重加成——EXTREME ×1.3 / HIGH ×1.15 / MEDIUM ×1.0 / LOW ×0.9，扩展 §3.8 `map_sector_to_stock_signal` 的加成系数链。
- **与 §3.6 虹吸态识别的协同**：虹吸态是资金面集中度（成交额维度），传染爆发是事件面激发强度（Hawkes 维度），两者可同时发生（虹吸龙头 + 传染爆发 = 极端情绪）。

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **单一涨跌幅排序** | 板块强度只按涨跌幅排序 | 易被噪声干扰；不考虑资金流和领涨股占比；AQR 实证 RS 多周期组合优于单周期 |
| **板块级 MVO 优化** | 用协方差矩阵做板块配置 | 与 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §3.1 拒绝 firm 层 MVO 同理——协方差估计是研究课题，放大噪声，归因纠缠；且板块轮动是选股输入特征，非独立层 |
| **ML 板块轮动预测** | XGBoost/LSTM 预测板块轮动 | MVP 阶段过度工程；先做多因子加权评分，Phase 1.5+ 积累数据后再上 ML |
| **板块级 Kelly 仓位** | 根据板块强度用 Kelly 分配板块仓位 | 与 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.1 分层裁定矛盾——板块轮动是选股输入特征，仓位决策在组合层 Kelly 精裁决（[31_position_sizing](31_position_sizing.md)） |
| **个股级回踩质量直接用** | 不扩展板块级，直接用 41_buy_flow.md §3.2 个股级 | 缺少板块内个股一致性维度；板块级 C 级（破位）时个股级可能误判为 A 级；需板块级作为上游门控 |
| **固定权重多因子** | 板块强度四维度用固定经验权重 | 权重需按市场阶段校准（华泰研报建议）；MVP 先用经验权重，Phase 1.5+ 数据驱动校准 |
| **无 mask-first 过滤** | 板块涨停潮/跌停潮时不 mask | 涨停潮时板块信号失真（追高风险）；与 [52_backtest_framework_docking](52_backtest_framework_docking.md) mask-first 前置设计不一致 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **板块数量** | ~460（880xxx 体系） | 同花顺板块 K 线覆盖范围；申万一级 31 + 二级 ~134 + 概念 ~295 |
| **板块强度评分** | [0, 100] | 多因子加权综合评分 |
| **强度等级阈值** | STRONG ≥75 / MEDIUM 50-75 / WEAK <50 | 经验阈值，Phase 1.5+ 数据驱动校准 |
| **调整进度激活阈值** | ≥80% 激活分批 / <40% 拦截 / >110% 破位警告 | BM-SEL-09 设计态参数 |
| **mask-first 涨停阈值** | 板块内涨停 >30% → mask | 避免追高涨停潮 |
| **mask-first 跌停阈值** | 板块内跌停 >20% → mask | 流动性危机风险 |
| **虹吸强度阈值** | >0.15 → 虹吸态 | 游资集中度模型经验值 |
| **传导延迟上限** | 5 天 | A 股板块→个股传导规律（边缘股 3-5 天） |
| **板块回踩质量加成** | A=1.2 / B=1.0 / C=0.3 | 个股信号调整系数 |
| **Hawkes 板块数（Phase 1.0）** | 5 大核心板块 | 计算量限制（N=5 → 25 维参数矩阵，实时计算可行） |
| **Hawkes 分支比预警阈值** | 0.8 | 保守预警阈值（< 1.0 理论稳态条件，提前预警传染爆发） |
| **Hawkes 传染评分加成** | EXTREME ×1.3 / HIGH ×1.15 / MEDIUM ×1.0 / LOW ×0.9 | 个股信号传染加成系数链（联动 §3.8 传导映射） |

**演进路径**：
- **MVP**：板块强度多因子加权 + 板块级 A/B/C + 调整进度 80% 阈值 + 轮动阶段检测 + 虹吸态识别 + 板块→个股传导映射
- **Phase 1.0**：多元 Hawkes 传染矩阵（5 大核心板块 N×N 激发矩阵 + 分支比估计 + 传染爆发检测 + 板块传染评分）；与 §3.7 资金流/§3.8 传导映射协同
- **Phase 1.5**：历史轮动模式匹配（需积累 6 月+ 板块轮动数据）+ 资金流趋势 ML 预测 + 权重数据驱动校准
- **Phase 2**：ML 板块轮动预测（XGBoost/LSTM）+ 虹吸态持续性追踪 + 跨市场板块轮动（港股/A 股联动）+ Hawkes 扩展到全 460 板块（稀疏化 + GPU 加速）

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **ML 板块轮动预测** | MVP 先做多因子加权评分 | Phase 1.5+ 积累 6 月板块轮动数据后 |
| **历史轮动模式匹配** | 需积累历史轮动模式库 | Phase 1.5+ 历史数据沉淀后 |
| **板块强度权重数据驱动校准** | MVP 用经验权重（0.30/0.30/0.25/0.15） | Phase 1.5+ 积累 IC 数据后用 IC 加权校准 |
| **虹吸态持续性追踪** | 当前仅当日判定，无持续性追踪 | Phase 1.5+ 历史状态机就绪后 |
| **跨市场板块轮动** | MVP 仅 A 股板块 | Phase 2+ 港股/A 股联动数据接入后 |
| **板块级 Kelly 仓位** | 与分层裁定矛盾，板块轮动是输入特征非独立层 | 永不（架构裁定） |

## 7. 待定问题（讨论要点对齐）

- [x] ① 板块强度算法（BM-SEL-08，460 板块 880xxx K 线）→ §3.2 `evaluate_sector_strength` 多因子加权（RS+动量+资金流+领涨股占比）+ mask-first 过滤
- [x] ② 回踩质量等级 A/B/C 判定 → §3.3 `evaluate_sector_pullback_quality` 板块级（扩展 41_buy_flow.md §3.2 个股级）+ 板块内个股一致性
- [x] ③ 调整周期追踪（BM-SEL-09，进度 ≥80% 激活分批）→ §3.4 `track_sector_adjustment`（进度公式 + 80% 激活 + 40% 拦截 + 110% 破位警告）
- [x] ④ 轮动序列追踪 → §3.5 `detect_rotation_stage`（4 阶段+底部）+ `detect_rotation_role`（领涨/跟涨/补涨/领跌）+ `match_historical_rotation_pattern`
- [x] ⑤ 虹吸态识别（30_multi_strategy_concurrency §1.3 提到情绪周期隐形驱动）→ §3.6 `detect_siphon_state`（虹吸强度 + 龙头板块识别 + 被虹吸板块衰减）
- [x] ⑥ 板块资金流 → §3.7 `calc_sector_capital_flow`（个股聚合 + 5/10/20 日均线趋势）
- [x] ⑦ 板块→个股的传导映射 → §3.8 `map_sector_to_stock_signal`（板块强度加成 + 回踩质量加成 + 传导延迟/衰减 + 虹吸态加成）

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G06
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §1.3（情绪周期隐形驱动）+ §2.2（regime 正交性）+ §3.1（拒绝 MVO）
- [41_buy_flow](41_buy_flow.md) §3.2（个股级 `evaluate_pullback_quality`，本节扩展为板块级）
- [24_daban_strategy_detail](24_daban_strategy_detail.md) §3.7（板块状态分类，与本节 §3.2 互补）
- [25_multifactor_strategy_detail](25_multifactor_strategy_detail.md) §3.2（行业中性化，与本节板块轮动正交）
- [31_position_sizing](31_position_sizing.md)（G12 仓位，板块轮动是输入特征非独立层）
- [52_backtest_framework_docking](52_backtest_framework_docking.md)（A 股 mask-first 前置设计）
- [15_data_feature_layer_spec](15_data_feature_layer_spec.md)（G01 板块 K 线数据契约）
- [21_stock_selection_engine](21_stock_selection_engine.md)（G05 选股引擎，下游消费者）
- battle_map_05_stock_selection（BM-SEL-08/09 + MOD-SIG-026 板块分析器当前状态快照）
- **2026-08 研究引用**：
  - AQR Capital Management — sector momentum（行业动量因子，RS > 1 跑赢大盘）
  - 华泰证券 (2026) 板块轮动研报 — 相对强度+资金流+情绪三维度
  - 申万行业轮动体系 — 880xxx K 线（约 460 板块）
  - A 股板块虹吸效应研究 — 游资集中度模型（龙头板块吸金）
  - 板块轮动四阶段模型 — 启动/加速/见顶/回落
  - 52_backtest_framework_docking — A 股 mask-first 前置设计（板块级涨跌停过滤）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G06 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | 板块强度多因子加权+板块级 A/B/C（扩展个股级）+调整周期追踪+轮动序列四阶段+虹吸态识别+板块资金流+板块→个股传导映射 7 算法化；整合 2026-08 研究（AQR sector momentum/华泰三维度/申万 880xxx/虹吸效应/四阶段模型/mask-first）；与 regime 正交，作为选股输入特征非独立层 |
| 2026-08-11 | 1.0.1 | 新增 §3.10 多元 Hawkes 传染矩阵 | 新增 §3.10 多元 Hawkes 传染矩阵（N×N 激发矩阵+分支比估计+传染爆发检测+板块传染评分）；与 §3.7 资金流/§3.8 传导映射协同；Phase 1.0 限制 5 大核心板块，分支比预警阈值 0.8 |
