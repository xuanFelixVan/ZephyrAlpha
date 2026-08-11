---
ttl: permanent
doc_type: architecture_view
title: 事件驱动策略细节
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.1.0"
date: 2026-08-10
topic: event_driven_strategy_detail
scope: 07_trading_decision_architecture
---

# 事件驱动策略细节

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G10 主题组派生，将事件驱动策略的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：PEAD.txt（JFQA 2023 Meursault LLM 文本 PEAD）；SUE+EAR 双因子（Rockstead 2026-05）；Bi-Power Variation 噪声稳健跳跃检测（arXiv:2601.08962 2026-01）；Jump on PEAD（华泰金工 2026-04 IC=10.96%）；dReport 披露时点（招商证券+2026-08 见光死修正）；隔夜趋势因子（西部证券 2026-03 RankIC=-0.1687）；AStockEvent Feed（PyPI 0.2.1 2026-06）；异动雷达事件簇（国盛证券 2026-03 IR=2.92）；IT 因子知情交易微观行为（西部证券 2026-03 RankIC=0.064）。**v1.1.0 新增**：龙虎榜 Smart Money 因子（净买率>12%次日+3.10%/20日+5.11%，合力型vs独食型，假机构陷阱识别，席位身份画像）；EVOQUANT LLM 策略自演化优化（arXiv:2607.12455v1 2026-07，Sharpe -0.298→0.538，远期候选）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G10 事件驱动策略细节 |
| 所属 | 作战地图 05 |
| 依赖 | G04、G05（[20_first_batch_strategies](20_first_batch_strategies.md)） |
| 对标 | RavenPack 事件驱动 / 彭博事件策略 / 华泰金工业绩期因子 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P2 |
| 状态 | ✅ active — 六因子矩阵+事件冲击评分+信号生成流程已定稿 |

## 2. 背景

### 2.1 项目处境

事件驱动策略是 ZephyrAlpha 首批策略之一，核心逻辑：利用 A 股市场对公开信息（业绩公告/预告/重组/解禁等）的反应不足和反应过度获取 alpha。A 股事件驱动具有独特性：T+1 结算限制日内操作、涨跌停板影响事件反应的表达方式、散户占比高导致情绪化反应显著。

### 2.2 核心问题

1. **经典 PEAD 在 A 股的有效性争议**：Subrahmanyam (2026 JIM) 复现发现"all-but-microcaps 中 2000 年后 PEAD 接近为 0"——需用文本/ML 方法（PEAD.txt）或限制在微盘股使用。
2. **事件信号如何量化和组合**：多个事件因子（ORJ/PEAD/SUE/EAR/dReport/Jump/隔夜/异动）如何加权组合为统一信号。
3. **2026-08 "见光死"现象**：高位股预增公告后不涨反跌（江波龙预增622倍后跌22.63%），需股价位置过滤。
4. **事件源结构化**：公告原文→结构化事件流的转换，AStockEvent Feed 提供了 2026-06 最新方案。
5. **事件冲击衰减曲线**：不同事件类型的冲击衰减速度不同（业绩公告 5-60 天，异动 1-3 天），需差异化持有期。

### 2.3 约束条件

- **A 股 T+1**：事件当日买入不可当日卖出，持有期至少 1 天
- **涨跌停板**：事件反应可能被涨跌停板截断（利好涨停买不进、利空跌停卖不出）
- **换手率**：事件驱动换手率中等（2-3 天），介于打板（1-2 天）和多因子（3-5 天）之间
- **容量**：中等，可承载部分资金

## 3. 决策

### 3.1 架构定义

事件驱动策略由事件源层、因子计算层、信号合成层三层构成：

```
事件源层: 公告原文 → AStockEvent Feed → 结构化事件流
                                        ↓
因子计算层: ORJ | PEAD(SUE+EAR) | dReport | Jump on PEAD | 隔夜趋势 | 异动雷达
                                        ↓
信号合成层: 六因子矩阵 → event_impact_score → 选股信号 → 风控门控 → 订单
```

### 3.2 六因子矩阵

| 因子 | 全称 | 数据源 | 持有期 | 信号方向 | 2026 来源 |
|---|---|---|---|---|---|
| **ORJ** | Overreaction Jump 过度反应跳跃 | 公告日异常收益 | 1-5 天 | 反转（过度反应后修正） | 经典因子 |
| **PEAD** | Post-Earnings Announcement Drift | SUE + EAR 双因子 | 20-60 天 | 顺向（漂移延续） | Rockstead 2026 / PEAD.txt JFQA 2023 |
| **dReport** | 披露时点因子 | 公告日 vs 预期日 | 5-10 天 | 顺向（提前=利好） | 招商证券 + 2026-08 见光死修正 |
| **Jump on PEAD** | 公告后价格跳跃分量 | 5 日窗口 Bi-Power Variation | 5-20 天 | 顺向（跳跃方向延续） | 华泰金工 2026-04 IC=10.96% |
| **隔夜趋势** | 隔夜收益率因子 | T+1 机制隔夜负漂移 | 5-20 天 | 反向（隔夜负→做多） | 西部证券 2026-03 RankIC=-0.1687 |
| **异动雷达** | 异动事件簇信号 | 多资金通道相关系数 | 1-3 天 | 顺向（逆势上涨异动） | 国盛证券 2026-03 IR=2.92 |

### 3.3 PEAD 双因子算法（SUE + EAR）

```python
import numpy as np
from dataclasses import dataclass

@dataclass
class PEADSignal:
    """PEAD 双因子信号（Rockstead 2026-05 实证）。"""
    sue_score: float          # 标准化未预期盈余 [-1, 1]
    ear_score: float          # 公告日异常收益 [-1, 1]
    combined_score: float     # 双因子组合信号 [-1, 1]
    holding_period_days: int  # 建议持有期


def compute_pead_signal(
    actual_eps: float,           # 实际 EPS
    expected_eps: float,         # 预期 EPS（分析师一致预期 or 历史均值）
    eps_surprise_history: np.ndarray,  # 历史 EPS 意外序列（用于标准化）
    announcement_date_return: float,   # 公告日收益率
    benchmark_return: float,    # 基准收益率
    earnings_call_text: str = None,    # 电话会议文本（PEAD.txt 可选）
) -> PEADSignal:
    """PEAD 双因子计算——SUE + EAR 正交组合。

    Rockstead (2026-05) 实证（1996-2026, 508 股, 18881 观测）：
    - SUE 单因子 Q5-Q1 年化 +3.91%
    - EAR 单因子 Q5-Q1 年化 -3.39%（反转）
    - 双因子组合 Long 年化 +18.50%，Short 年化 +13.03%
    - SUE 与 EAR 相关性 ≈ 0.004，几乎正交 → 真正分散

    PEAD.txt 扩展（JFQA 2023 Meursault）：
    - 经典 PEAD 在 2000 年后接近为 0（Subrahmanyam 2026 JIM 确认）
    - PEAD.txt 用 LLM 嵌入盈余电话会议文本构造 SUE.txt
    - 捕捉"数字背后的基本面叙事"，在近年仍显著
    - MVP 阶段先用数值 SUE+EAR，Phase 1.5+ 接入 PEAD.txt
    """
    # SUE: 标准化未预期盈余
    surprise = actual_eps - expected_eps
    surprise_std = np.std(eps_surprise_history) if len(eps_surprise_history) > 0 else 1.0
    sue = surprise / surprise_std if surprise_std > 0 else 0.0
    sue_score = np.clip(sue / 3.0, -1.0, 1.0)  # 标准化到 [-1, 1]

    # EAR: 公告日异常收益
    car = announcement_date_return - benchmark_return
    ear_score = np.clip(car / 0.05, -1.0, 1.0)  # 5% 异常收益 = 满分

    # 双因子正交组合（SUE 顺向 + EAR 顺向，非反转）
    # Rockstead 2026: Long = SUE∈Q5 ∧ EAR∈Q5, Short = SUE∈Q1 ∧ EAR∈Q1
    combined = 0.6 * sue_score + 0.4 * ear_score  # SUE 权重更高（基本面 > 市场反应）
    combined = np.clip(combined, -1.0, 1.0)

    # 持有期：SUE 大且 EAR 顺向 → 长持有（60 天）；否则短持有
    if abs(combined) > 0.7:
        holding_period = 60  # 强信号长持有
    elif abs(combined) > 0.3:
        holding_period = 30
    else:
        holding_period = 10

    return PEADSignal(
        sue_score=sue_score,
        ear_score=ear_score,
        combined_score=combined,
        holding_period_days=holding_period,
    )
```

### 3.4 dReport 披露时点因子算法

```python
@dataclass
class DReportSignal:
    """dReport 披露时点因子信号——"靓女先嫁"效应量化。"""
    dreport_days: int         # 披露提前天数
    grade: str                # STRONG_EARLY / MEDIUM_EARLY / WEAK_EARLY / DELAYED
    signal_score: float       # [-1, 1]
    position_warning: str     # HIGH / MID / LOW（股价位置）
    effective: bool           # 信号是否有效（高位股信号无效化）


def compute_dreport_factor(
    actual_report_date,            # 实际公告日
    legal_deadline,                # 法定截止日
    last_year_report_date,         # 去年公告日
    pre_announcement: str,         # 业绩预告类型："预增"/"扭亏"/"续盈"/"预减"/"续亏"/"首亏"
    board_type: str,               # "main" / "star" / "gem" / "bse"
    ohlcv_close: float,            # 当前收盘价
    ohlcv_high_60d: float,         # 60 日最高价
) -> DReportSignal:
    """dReport 披露时点因子——"靓女先嫁"效应量化。

    招商证券 2009-2020 回测：年化超额 4.88% / Sharpe 1.44
    2026-08 头条研究：
    - 大幅提前 T+5 上涨概率 70-75%、超额 3.0-4.5%
    - 推迟 -1.0%~-1.5%
    - 见光死警示：高位股预增仍跌（江波龙预增622倍后跌22.63%）→ 须股价位置过滤
    雪球 2026-07：科创板/创业板预告自愿，主动预增信号强度 > 主板强制预告

    算法步骤：
    1. 计算披露提前天数（双维度取 max）
    2. 提前程度分级
    3. 业绩预告增强
    4. 2026-08 见光死修正（高位股信号无效化）
    """
    # 步骤 1：计算披露提前天数（双维度取 max）
    dreport_yoy = (last_year_report_date - actual_report_date).days
    dreport_to_deadline = (legal_deadline - actual_report_date).days
    dreport_days = max(dreport_yoy, dreport_to_deadline)

    # 步骤 2：提前程度分级（招商证券 10 年回测阈值）
    if dreport_days > 10:
        grade, base_score = "STRONG_EARLY", 1.0    # T+5 上涨概率 70-75%
    elif dreport_days > 5:
        grade, base_score = "MEDIUM_EARLY", 0.6    # 60-63%
    elif dreport_days > 1:
        grade, base_score = "WEAK_EARLY", 0.3      # 52-55%
    else:
        grade, base_score = "DELAYED", -0.5         # ~45%

    # 步骤 3：业绩预告增强
    pre_announcement_boost = {
        "预增": 0.2, "扭亏": 0.25, "续盈": 0.05,
        "预减": -0.3, "续亏": -0.4, "首亏": -0.5,
    }.get(pre_announcement, 0.0)

    # 双创板主动预告信号增强
    if board_type in ("star", "gem", "bse") and pre_announcement in ("预增", "扭亏"):
        pre_announcement_boost *= 1.3

    # 步骤 4：2026-08 见光死修正（高位股信号无效化）
    drawdown_from_high = (ohlcv_close - ohlcv_high_60d) / ohlcv_high_60d  # 负值

    if drawdown_from_high > -0.05:  # 距 60 日高点 < 5% = 高位
        position_warning, effective = "HIGH", False
        signal_score = 0.0  # 高位股信号无效
    elif drawdown_from_high > -0.15:  # 5-15% = 中位
        position_warning, effective = "MID", True
        signal_score = (base_score + pre_announcement_boost) * 0.7
    else:  # > 15% = 低位
        position_warning, effective = "LOW", True
        signal_score = (base_score + pre_announcement_boost) * 1.2

    signal_score = max(-1.0, min(1.0, signal_score))

    return DReportSignal(
        dreport_days=dreport_days,
        grade=grade,
        signal_score=signal_score,
        position_warning=position_warning,
        effective=effective,
    )
```

### 3.5 Jump on PEAD 价格跳跃分量算法

```python
@dataclass
class JumpOnPEADSignal:
    """Jump on PEAD 信号——公告后价格跳跃分量。"""
    jump_component: float      # 跳跃分量（正值=利好跳跃）
    continuous_drift: float    # 连续漂移分量
    car_5d: float              # 5 日累计异常收益
    jump_ratio: float          # 跳跃纯度（跳跃/总变异）
    signal_score: float        # [-1, 1]


def compute_jump_on_pead(
    ohlcv,                         # 公告后 OHLCV 数据
    benchmark_returns,             # 基准收益率序列
    announcement_date,             # 公告日
    window: int = 5,               # 窗口天数（华泰金工 IC=10.96% 用 5 日）
) -> JumpOnPEADSignal:
    """Jump on PEAD——Bi-Power Variation 分离跳跃 vs 漂移。

    华泰金工 2026-04：5 日窗口 IC=10.96%，随窗口拉长衰减
    → 个股动态跟踪 > 横截面使用（个股信息消化进度不同）

    Zhou & Zhu (2012 FAJ): long positive-jump + short negative-jump
    年化 15.3% / Sharpe 1.52

    Barndorff-Nielsen & Shephard (2004): BPV 分离跳跃与连续漂移的标准方法
    - RV (已实现波动率) = Σ r²  （含跳跃）
    - BPV (双幂变异) = (π/2) · Σ |r_i| · |r_{i-1}|  （仅连续漂移）
    - 跳跃方差 = max(0, RV - BPV)

    2026-01 改进（arXiv:2601.08962）：预平均子抽样 BPV 噪声稳健版
    - 经典 BNS 在有微结构噪声和跳跃聚集时严重低估跳跃
    - 预平均 + 子抽样在有限样本下稳健
    - MVP 阶段先用经典 BNS，Phase 1.5+ 升级预平均版
    """
    # 步骤 1：计算公告后窗口超额收益
    ann_idx = ohlcv.index.get_loc(announcement_date)
    post_window = ohlcv.iloc[ann_idx + 1 : ann_idx + 1 + window]
    stock_returns = post_window['close'].pct_change().dropna().values
    bench_returns = benchmark_returns.reindex(post_window.index).pct_change().dropna().values

    # 对齐长度
    min_len = min(len(stock_returns), len(bench_returns))
    r = stock_returns[:min_len] - bench_returns[:min_len]  # 超额收益

    if len(r) < 3:
        return JumpOnPEADSignal(0, 0, 0, 0, 0)

    # 步骤 2：Bi-Power Variation 分离跳跃分量
    RV = np.sum(r ** 2)                                       # 含跳跃的已实现波动率
    BPV = (np.pi / 2) * np.sum(np.abs(r[1:]) * np.abs(r[:-1]))  # 仅连续漂移
    jump_variance = max(0, RV - BPV)                          # 跳跃贡献的方差

    # 步骤 3：跳跃方向判定（2σ 阈值识别跳跃日）
    jump_threshold = np.sqrt(BPV / len(r)) * 2.0 if BPV > 0 else np.std(r) * 2
    jump_days = np.abs(r) > jump_threshold
    jump_component = float(np.sum(r[jump_days])) if jump_days.sum() > 0 else 0.0
    continuous_drift = float(np.sum(r[~jump_days])) if jump_days.sum() > 0 else float(np.sum(r))

    # 步骤 4：信号标准化（跳跃纯度修正）
    total_variation = abs(jump_component) + abs(continuous_drift)
    jump_ratio = abs(jump_component) / total_variation if total_variation > 0 else 0
    purity_mult = 1.0 if jump_ratio > 0.5 else (0.6 if jump_ratio > 0.3 else 0.3)

    # 步骤 5：跳跃幅度分级（3%/1% 阈值）
    if jump_component > 0.03:
        base = 1.0
    elif jump_component > 0.01:
        base = 0.5
    elif jump_component < -0.03:
        base = -1.0
    elif jump_component < -0.01:
        base = -0.5
    else:
        base = 0.0

    signal_score = base * purity_mult

    return JumpOnPEADSignal(
        jump_component=jump_component,
        continuous_drift=continuous_drift,
        car_5d=float(np.sum(r)),
        jump_ratio=jump_ratio,
        signal_score=signal_score,
    )
```

### 3.6 隔夜趋势因子算法

```python
@dataclass
class OvernightTrendSignal:
    """隔夜趋势因子信号。"""
    overnight_mean_20d: float    # 20 日隔夜收益均值
    momentum_signal: float       # 隔夜动量信号
    correlation_signal: float    # 滞后日内价差与收盘价相关信号
    combined_score: float        # [-1, 1]


def compute_overnight_trend(
    ohlcv,                        # OHLCV 数据（至少 200 天）
    window_mean: int = 20,        # 隔夜均值窗口
    window_momentum_short: int = 5,
    window_momentum_long: int = 20,
    window_corr: int = 200,       # 相关性窗口
) -> OvernightTrendSignal:
    """隔夜趋势因子——A 股 T+1 机制下的隔夜负漂移。

    西部证券 2026-03《用隔夜交易策略增强指数增强》：
    - A 股隔夜收益率为负的根源是 T+1 机制
      "昨收买、今开卖"包含一个当日可卖权力，需付出成本
    - 合成隔夜因子 = -[成交量冲击 + 日内收益率 + 振幅 + 流动性因子]（等权）
    - Rank IC = -0.1687
    - 沪深 300 增强：年化超额 +4.66%，跟踪误差 1.17%，最大回撤 0.49%

    三维隔夜信号（CSDN Alpha#037 2026）：
    1. 20 日滚动隔夜均值
    2. 隔夜动量（MA5 - MA20）
    3. 200 日滞后日内价差与收盘价的相关性
    """
    close = ohlcv['close'].values
    open_ = ohlcv['open'].values
    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]

    # 隔夜收益率 = 今开 / 昨收 - 1
    overnight_returns = open_[1:] / prev_close[1:] - 1

    # 维度 1：20 日滚动隔夜均值
    overnight_mean = np.mean(overnight_returns[-window_mean:])

    # 维度 2：隔夜动量（MA5 - MA20）
    ma_short = np.mean(overnight_returns[-window_momentum_short:])
    ma_long = np.mean(overnight_returns[-window_momentum_long:])
    momentum = ma_short - ma_long

    # 维度 3：200 日滞后日内价差与收盘价的相关性
    # 日内价差 = (close - open) / open
    intraday_spread = (close[1:] - open_[1:]) / open_[1:]
    lagged_spread = np.roll(intraday_spread, 1)
    lagged_spread[0] = 0

    if len(close[-window_corr:]) >= window_corr:
        corr = np.corrcoef(lagged_spread[-window_corr:], close[-window_corr:])[0, 1]
    else:
        corr = 0.0

    # 合成信号（西部证券 Rank IC = -0.1687，负向因子）
    # 隔夜收益越负 → 信号越强（做多）
    mean_score = np.clip(-overnight_mean * 50, -1, 1)     # 负漂移 → 正信号
    momentum_score = np.clip(-momentum * 100, -1, 1)      # 负动量 → 正信号
    corr_score = np.clip(-corr, -1, 1)                    # 负相关 → 正信号

    combined = 0.4 * mean_score + 0.3 * momentum_score + 0.3 * corr_score

    return OvernightTrendSignal(
        overnight_mean_20d=float(overnight_mean),
        momentum_signal=float(momentum),
        correlation_signal=float(corr),
        combined_score=float(np.clip(combined, -1, 1)),
    )
```

### 3.7 AStockEvent Feed 事件消费算法

```python
SEV_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}

@dataclass
class EventImpactScore:
    """AStockEvent Feed 事件冲击评分。"""
    event_type: str            # 事件类型
    severity_rank: int         # 严重度等级 1-4
    sentiment: float           # 情绪 [-1, 1]
    confidence_tier: str       # verified / likely / uncertain
    impact_score: float        # 综合冲击评分 [-1, 1]
    suggested_action: str      # "long" / "short" / "neutral" / "exit"


# 事件类型→交易信号映射表
EVENT_SIGNAL_MAP = {
    "业绩预告": {"预增": 0.8, "扭亏": 0.9, "续盈": 0.2, "预减": -0.7, "续亏": -0.8, "首亏": -0.9},
    "减持": -0.6,
    "增持": 0.5,
    "回购": 0.7,
    "限售解禁": -0.5,
    "重组": 0.4,   # 不确定性高，默认轻度利好
    "ST": -0.9,
    "撤销ST": 0.8,
    "监管函": -0.6,
    "违规处罚": -0.8,
    "停复牌": 0.0,  # 需看具体原因
    "质押": -0.3,   # 质押比例高 = 风险
    "分红": 0.2,
    "可转债": 0.1,
}


def consume_astockevent_feed(event: dict) -> EventImpactScore:
    """消费 AStockEvent Feed 结构化事件流。

    AStockEvent Feed (PyPI 0.2.1 2026-06-08)：
    - 将巨潮/东财公告原文转为 AI Agent 可直接消费的结构化语义事件
    - 通过 MCP 协议提供 16 个查询工具
    - 覆盖 13+ 事件类型
    - 3 级置信度：verified / likely / uncertain
    - 免费 100 次/天

    事件 JSON 结构：
    {
      "event_type": "业绩预告|减持|重组|...",
      "structured_payload": { ... },
      "confidence_tier": "verified|likely|uncertain",
      "ai_summary": "...",
      "ai_context": { "severity": ..., "sentiment": ... },
      "timeline": [ ... ]
    }
    """
    event_type = event.get("event_type", "")
    ai_context = event.get("ai_context", {})
    confidence_tier = event.get("confidence_tier", "uncertain")
    structured_payload = event.get("structured_payload", {})

    # 严重度映射
    severity_str = ai_context.get("severity", "low")
    severity_rank = SEV_RANK.get(severity_str, 1)

    # 情绪映射
    sentiment = ai_context.get("sentiment", 0.0)

    # 事件类型→信号映射
    if event_type == "业绩预告":
        # 业绩预告需看具体类型
        pre_announcement = structured_payload.get("pre_announcement", "")
        base_signal = EVENT_SIGNAL_MAP["业绩预告"].get(pre_announcement, 0.0)
    else:
        base_signal = EVENT_SIGNAL_MAP.get(event_type, 0.0)

    # 置信度调整
    confidence_mult = {"verified": 1.0, "likely": 0.7, "uncertain": 0.4}.get(confidence_tier, 0.4)

    # 严重度调整
    severity_mult = 0.5 + 0.5 * (severity_rank / 4.0)  # 1→0.625, 4→1.0

    # 综合冲击评分
    impact_score = base_signal * confidence_mult * severity_mult
    impact_score = max(-1.0, min(1.0, impact_score))

    # 建议动作
    if impact_score > 0.3:
        action = "long"
    elif impact_score < -0.3:
        action = "short"  # A 股无做空，实际为"退出/不入场"
    elif impact_score < -0.6:
        action = "exit"   # 强利空→退出持仓
    else:
        action = "neutral"

    return EventImpactScore(
        event_type=event_type,
        severity_rank=severity_rank,
        sentiment=sentiment,
        confidence_tier=confidence_tier,
        impact_score=impact_score,
        suggested_action=action,
    )
```

### 3.8 六因子矩阵信号合成算法

```python
@dataclass
class EventDrivenSignal:
    """事件驱动策略综合信号。"""
    symbol: str
    pead_score: float          # PEAD 双因子
    dreport_score: float       # dReport 披露时点
    jump_score: float          # Jump on PEAD 跳跃
    overnight_score: float     # 隔夜趋势
    event_score: float         # AStockEvent 事件冲击
    orj_score: float           # ORJ 过度反应（简化：公告日异常收益反转）
    combined_score: float      # 加权综合信号 [-1, 1]
    suggested_holding: int     # 建议持有期（天）
    confidence: str            # HIGH / MEDIUM / LOW


def synthesize_event_signal(
    symbol: str,
    pead: PEADSignal,
    dreport: DReportSignal,
    jump: JumpOnPEADSignal,
    overnight: OvernightTrendSignal,
    event: EventImpactScore,
    orj_score: float = 0.0,    # ORJ 简化：公告日过度反应反转信号
) -> EventDrivenSignal:
    """六因子矩阵信号合成——加权组合为统一交易信号。

    权重设计原则：
    - PEAD 是核心因子（基本面漂移），权重最高
    - dReport 和 Jump on PEAD 是辅助确认因子
    - 隔夜趋势是结构性因子（T+1 机制），独立于事件
    - AStockEvent 事件冲击是即时触发因子
    - ORJ 是短线反转因子

    信号一致性检查：
    - 多数因子同向 → 高置信度
    - 因子分歧 → 低置信度，缩窄仓位
    """
    # 因子权重（总和=1.0）
    weights = {
        'pead': 0.25,        # PEAD 双因子（核心）
        'dreport': 0.15,     # dReport 披露时点
        'jump': 0.15,        # Jump on PEAD 跳跃
        'overnight': 0.15,   # 隔夜趋势
        'event': 0.20,       # AStockEvent 事件冲击
        'orj': 0.10,         # ORJ 过度反应
    }

    # dReport 有效性过滤
    dreport_effective_score = dreport.signal_score if dreport.effective else 0.0

    # 加权合成
    combined = (
        weights['pead'] * pead.combined_score +
        weights['dreport'] * dreport_effective_score +
        weights['jump'] * jump.signal_score +
        weights['overnight'] * overnight.combined_score +
        weights['event'] * event.impact_score +
        weights['orj'] * orj_score
    )
    combined = max(-1.0, min(1.0, combined))

    # 信号一致性 → 置信度
    scores = [pead.combined_score, dreport_effective_score, jump.signal_score,
              overnight.combined_score, event.impact_score, orj_score]
    same_direction = sum(1 for s in scores if (s > 0.1) == (combined > 0)) if combined != 0 else 0
    if same_direction >= 5:
        confidence = "HIGH"
    elif same_direction >= 3:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    # 持有期：取 PEAD 建议期与事件类型的加权平均
    suggested_holding = pead.holding_period_days

    return EventDrivenSignal(
        symbol=symbol,
        pead_score=pead.combined_score,
        dreport_score=dreport.signal_score,
        jump_score=jump.signal_score,
        overnight_score=overnight.combined_score,
        event_score=event.impact_score,
        orj_score=orj_score,
        combined_score=combined,
        suggested_holding=suggested_holding,
        confidence=confidence,
    )
```

### 3.9 异动雷达事件簇算法（辅助因子）

```python
def compute_anomaly_radar(
    stock_minute_flows: np.ndarray,    # 个股分钟资金流序列
    index_minute_flows: np.ndarray,    # 基准指数分钟资金流序列
    stock_minute_returns: np.ndarray,  # 个股分钟收益率
    index_minute_returns: np.ndarray,  # 基准指数分钟收益率
) -> dict:
    """异动雷达事件簇信号——国盛证券 2026-03。

    回测（2016-2026, 中证 800）：
    - 年化超额 7.51%，IR 2.48
    - 叠加负向筛选后年化超额 9.77%，IR 2.92

    核心逻辑：
    - 多维度资金流指标计算个股日内与基准指数分钟序列相关系数
    - 相关系数 < 0 触发异动
    - 按超额收益方向分为"逆势上涨/逆势下跌"
    - 合成综合信号（多类资金通道信号，有效性+相关性筛选后）
    """
    # 分钟级相关系数
    min_len = min(len(stock_minute_flows), len(index_minute_flows))
    corr = np.corrcoef(stock_minute_flows[:min_len], index_minute_flows[:min_len])[0, 1]

    # 异动触发
    is_anomaly = corr < 0

    # 超额收益方向
    stock_return = np.sum(stock_minute_returns)
    index_return = np.sum(index_minute_returns)
    excess_return = stock_return - index_return

    if is_anomaly:
        if excess_return > 0:
            anomaly_type = "逆势上涨"  # 逆势上涨异动 → 看多信号
            signal = min(1.0, abs(excess_return) * 20)
        else:
            anomaly_type = "逆势下跌"  # 逆势下跌异动 → 看空信号
            signal = max(-1.0, -abs(excess_return) * 20)
    else:
        anomaly_type = "无异动"
        signal = 0.0

    return {
        "correlation": float(corr),
        "is_anomaly": is_anomaly,
        "anomaly_type": anomaly_type,
        "excess_return": float(excess_return),
        "signal_score": float(signal),
    }
```

### 3.10 龙虎榜 Smart Money 因子算法（2026-08 回测验证）

```python
from dataclasses import dataclass
from enum import Enum


class SeatIdentity(Enum):
    """龙虎榜席位身份标签——基于 Smart Money Profiler (quantskills 2026-06)。"""
    INSTITUTIONAL = "机构专用"      # 公募/社保/保险/券商自营
    NORTHBOUND = "沪深股通"          # 北向资金
    HOT_MONEY = "游资营业部"         # 知名游资
    RETAIL_CLUSTER = "散户集中营"    # 如东方财富拉萨系
    QUANT = "量化席位"              # 如华鑫上海分公司
    UNKNOWN = "未识别"


@dataclass
class DragonTigerFactor:
    """龙虎榜 Smart Money 因子——事件驱动的第 7 个辅助因子。

    2026-08 研究整合：
    - 东方财富回测（2026-08）：净买率>12% → 次日+3.10%，20日均收+5.11%
    - 买方前五总额≥卖方1.5倍 + 净买入占当日成交>3% = 真强势信号
    - 合力型（买一至买五分布均匀）优于独食型（买一>50%），后者次日易低开
    - 假机构陷阱：买入金额整齐（888万等）+尾盘突击+次日快速出货
    - Smart Money Profiler（quantskills 2026-06）：席位身份+跨期行为画像

    与打板策略的分工：
    - 打板策略（24号）：用龙虎榜做"次日是否接力"判定
    - 事件驱动（本号）：用龙虎榜做"机构/游资资金意愿"事件因子
    两者正交：打板看短线接力，事件驱动看中期资金布局
    """
    symbol: str
    net_buy_ratio: float          # 净买率 = 净买入 / 当日成交额
    buy_sell_ratio: float         # 买方总额 / 卖方总额
    structure_type: str           # "合力型" / "独食型" / "分歧型"
    dominant_seat_type: SeatIdentity  # 主导席位类型
    institutional_net_buy: float  # 机构席位净买入（万）
    northbound_net_buy: float     # 北向席位净买入（万）
    hot_money_net_buy: float      # 游资席位净买入（万）
    is_fake_institutional: bool   # 假机构陷阱
    has_wash_trade: bool          # 对倒嫌疑
    smart_money_score: float      # 综合评分 [-1, 1]
    factor_signal: str            # "bullish" / "neutral" / "bearish" / "avoid"


def compute_dragon_tiger_factor(
    symbol: str,
    total_turnover: float,               # 当日成交额
    buyer_seats: list[dict],             # 买方前五席位
    seller_seats: list[dict],            # 卖方前五席位
) -> DragonTigerFactor:
    """龙虎榜 Smart Money 因子计算——资金结构+席位画像综合评分。

    数据时效：龙虎榜 16:30-19:00 发布，T 日盘后获取 → T+1 日开盘使用
    持有期建议：3-10 日（中期资金布局信号，非短线接力）

    评分逻辑：
    - 净买率 > 12% 且合力型 + 机构/北向主导 → bullish (+0.5~1.0)
    - 净买率 3%-12% 且买方≥卖方 → neutral (+0.0~0.3)
    - 净卖出 或 独食型 → bearish (-0.3~0.0)
    - 假机构/对倒 → avoid (-1.0)
    """
    total_buy = sum(s.get("buy_amount", 0) for s in buyer_seats)
    total_sell = sum(s.get("sell_amount", 0) for s in seller_seats)
    net_buy = total_buy - total_sell
    net_buy_ratio = net_buy / total_turnover if total_turnover > 0 else 0.0
    buy_sell_ratio = total_buy / total_sell if total_sell > 0 else float("inf")

    # ===== 席位身份分类汇总 =====
    seat_net_by_type: dict[SeatIdentity, float] = {}
    for seat in buyer_seats + seller_seats:
        seat_type = seat.get("seat_type", SeatIdentity.UNKNOWN)
        net = seat.get("buy_amount", 0) - seat.get("sell_amount", 0)
        seat_net_by_type[seat_type] = seat_net_by_type.get(seat_type, 0) + net

    institutional_net = seat_net_by_type.get(SeatIdentity.INSTITUTIONAL, 0)
    northbound_net = seat_net_by_type.get(SeatIdentity.NORTHBOUND, 0)
    hot_money_net = seat_net_by_type.get(SeatIdentity.HOT_MONEY, 0)

    # 主导席位类型（净买入最大的类型）
    dominant_seat_type = max(
        seat_net_by_type, key=seat_net_by_type.get, default=SeatIdentity.UNKNOWN
    )

    # ===== 结构判定 =====
    buy_amounts = [s.get("buy_amount", 0) for s in buyer_seats]
    top1_buy = max(buy_amounts) if buy_amounts else 0
    top1_ratio = top1_buy / total_buy if total_buy > 0 else 0

    if top1_ratio > 0.50:
        structure_type = "独食型"
    elif buy_sell_ratio >= 1.5:
        structure_type = "合力型"
    else:
        structure_type = "分歧型"

    # ===== 假机构陷阱识别 =====
    is_fake_inst = False
    for seat in buyer_seats:
        if seat.get("seat_type") == SeatIdentity.INSTITUTIONAL:
            amt = seat.get("buy_amount", 0)
            if amt > 0:
                amt_wan = amt / 10000
                is_tidy = any(
                    abs(amt_wan - nice) < 1.0
                    for nice in [888, 666, 999, 520, 1314, 168]
                )
                if is_tidy:
                    is_fake_inst = True
                    break

    # ===== 对倒嫌疑 =====
    buyer_names = {s["seat_name"] for s in buyer_seats}
    seller_names = {s["seat_name"] for s in seller_seats}
    has_wash_trade = len(buyer_names & seller_names) > 0

    # ===== 综合评分 =====
    score = 0.0

    # 净买率贡献
    if net_buy_ratio > 0.12:
        score += 0.4
    elif net_buy_ratio > 0.03:
        score += 0.2
    elif net_buy_ratio < -0.05:
        score -= 0.3

    # 结构贡献
    if structure_type == "合力型":
        score += 0.2
    elif structure_type == "独食型":
        score -= 0.1

    # 席位身份贡献
    if dominant_seat_type in (SeatIdentity.INSTITUTIONAL, SeatIdentity.NORTHBOUND):
        score += 0.2  # 机构/北向主导 = 中期看好
    elif dominant_seat_type == SeatIdentity.RETAIL_CLUSTER:
        score -= 0.2  # 散户集中营主导 = 合力弱
    elif dominant_seat_type == SeatIdentity.QUANT:
        score -= 0.1  # 量化扎堆 = 走势反人性

    # 危险信号扣分
    if is_fake_inst:
        score -= 0.8
    if has_wash_trade:
        score -= 0.5

    score = max(-1.0, min(1.0, score))

    # ===== 信号判定 =====
    if is_fake_inst or has_wash_trade:
        signal = "avoid"
    elif score >= 0.5:
        signal = "bullish"
    elif score >= 0.1:
        signal = "neutral"
    else:
        signal = "bearish"

    return DragonTigerFactor(
        symbol=symbol,
        net_buy_ratio=net_buy_ratio,
        buy_sell_ratio=buy_sell_ratio,
        structure_type=structure_type,
        dominant_seat_type=dominant_seat_type,
        institutional_net_buy=institutional_net,
        northbound_net_buy=northbound_net,
        hot_money_net_buy=hot_money_net,
        is_fake_institutional=is_fake_inst,
        has_wash_trade=has_wash_trade,
        smart_money_score=score,
        factor_signal=signal,
    )
```

### 3.11 EVOQUANT LLM 策略自演化优化（远期候选）

```python
@dataclass
class EvoQuantConfig:
    """EVOQUANT LLM 策略自演化优化配置——远期候选。

    来源：arXiv:2607.12455v1（2026-07-14, HKUST(GZ) + Paradoox AI Research）
    核心能力：LLM 诊断策略瓶颈 → 生成受控候选编辑 → 多阶段验证 → 蒸馏优化经验

    实验结果（A股+比特币 7 策略）：
    - 平均测试 Sharpe: -0.298 → 0.538
    - 最佳策略相对提升 199%
    - 含 walk-forward 验证 + 交易成本压力测试

    四模块架构：
    1. Strategy Ingestion: 策略代码→AST+依赖图+历史回测指标
    2. Baseline Evaluation: 瓶颈诊断（weak signal / overfitting / regime mismatch）
    3. Strategy Optimization: LLM 生成受控候选编辑（语义约束=不改变策略核心逻辑）
    4. Iterative Refinement: 多阶段验证（回测→WFA→OOS）+ 经验蒸馏

    与现有 52_backtest_framework_docking 的关系：
    - 52号 IS→WFA→OOS 验证流程是 EVOQUANT 第四模块的基础
    - EVOQUANT 在验证流程之上增加 LLM 自动诊断+生成+蒸馏
    - Phase 2+ 候选：MVP 阶段人工调参，Phase 2+ 评估 EVOQUANT 自动化
    """
    enabled: bool = False               # MVP 阶段关闭
    max_iterations: int = 10            # 最大迭代轮次
    verification_stages: list[str] = None  # ["backtest", "wfa", "oos"]
    cost_stress_test: bool = True       # 交易成本压力测试
    semantic_constraint: bool = True    # 语义约束（不改变策略核心逻辑）
    experience_distillation: bool = True  # 经验蒸馏为可复用知识


def evoquant_optimize_strategy(
    strategy_code: str,                 # 策略源码
    backtest_results: dict,             # 历史回测指标
    config: EvoQuantConfig = None,
) -> dict:
    """EVOQUANT 策略自演化优化——远期候选，MVP 阶段不施工。

    本函数仅作为 Phase 2+ 评估的接口占位。

    工作流程（Phase 2+ 落地）：
    1. 策略摄入：源码→AST+依赖图+指标快照
    2. 瓶颈诊断：LLM 分析 weak signal / overfitting / regime mismatch
    3. 候选生成：LLM 在语义约束下生成参数调整/信号增强/风控改进候选
    4. 多阶段验证：回测→WFA→OOS（复用52号验证流程）
    5. 经验蒸馏：将成功优化模式蒸馏为可复用知识库

    约束：
    - 语义约束：候选编辑不改变策略核心逻辑（如动量策略不改均值回归）
    - 成本压力测试：所有候选必须在 2x 交易成本下仍盈利
    - Walk-forward：必须通过 WFA 才进入 OOS 验证
    """
    if config is None or not config.enabled:
        return {
            "status": "deferred",
            "reason": "EVOQUANT is Phase 2+ candidate, MVP uses manual tuning",
            "reference": "arXiv:2607.12455v1 (2026-07-14)",
        }

    # Phase 2+ 实现占位
    raise NotImplementedError(
        "EVOQUANT LLM optimization is Phase 2+ feature. "
        "See arXiv:2607.12455v1 for implementation details."
    )
```

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **仅用经典 SUE PEAD** | 单一数值 SUE 因子 | Subrahmanyam (2026 JIM) 确认 2000 年后 PEAD≈0；需文本/ML 方法 |
| **PEAD.txt LLM 文本** | 盈余电话会议文本嵌入 | MVP 阶段无 LLM 基础设施；Phase 1.5+ 接入 |
| **CNN 可视化盈余** | 8 季度 EPS 柱状图→CNN | 过度工程，MVP 阶段不采纳 |
| **单一事件因子** | 仅用 ORJ 或 PEAD | 单因子信号弱、覆盖面窄；六因子矩阵分散+正交 |
| **横截面 Jump on PEAD** | 横截面排序使用跳跃因子 | 华泰金工 2026-04 明确：个股动态跟踪 > 横截面使用 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **持有期** | 1-60 天 | 事件驱动中等换手（2-3 天核心），PEAD 最长 60 天 |
| **单标的仓位** | ≤ 5% | 事件驱动容量中等，需分散 |
| **信号阈值** | combined_score > 0.3 入场 | 过低阈值噪声大 |
| **置信度缩仓** | LOW 置信度仓位减半 | 因子分歧时缩窄风险敞口 |

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **PEAD.txt LLM 文本** | MVP 无 LLM 基础设施 | Phase 1.5+ LLM 层就绪后 |
| **CNN 可视化盈余** | 过度工程 | Phase 2+ 深度学习平台就绪 |
| **预平均子抽样 BPV** | 经典 BNS 已足够 MVP | Phase 1.5+ 高频数据就绪 |
| **异动雷达全量接入** | 需分钟级资金流数据 | Phase 1.5+ Level-2 数据就绪 |

## 7. 待定问题（讨论要点对齐）

- [x] ① 事件源（公告/新闻/龙虎榜/异动）→ §3.7 AStockEvent Feed + §3.9 异动雷达
- [x] ② 事件分类（业绩/并购/政策/突发事件）→ §3.7 EVENT_SIGNAL_MAP 13+ 类型
- [x] ③ 事件冲击衰减曲线 → 六因子差异化持有期（PEAD 60 天/异动 1-3 天/dReport 5-10 天）
- [x] ④ 事件信号→选股映射 → §3.8 `synthesize_event_signal` 六因子矩阵合成
- [x] ⑤ 事件驱动换手率（中，2-3 天）→ §5 持有期上限 1-60 天
- [x] ⑥ news_data 多源情绪接入 → AStockEvent Feed MCP 协议 + ai_context.sentiment

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G10
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- [15_data_feature_layer_spec](15_data_feature_layer_spec.md)（G01 因子工程）
- battle_map_05_stock_selection（当前状态快照）
- **2026-08 研究引用**：
  - Meursault et al. (2023) "PEAD.txt" JFQA 58(6) — LLM 文本 PEAD
  - Subrahmanyam (2026) "Keeping It Simple" JIM 15(1) — PEAD 2000 年后失效
  - Kaczmarek & Zaremba (2025) "Reviving PEAD with ML" Finance Research Letters 86
  - Rockstead (2026-05) "SUE+EAR Two-Factor PEAD" — Long +18.50%, Short +13.03%
  - 华泰金工 (2026-04) "业绩期价格跳跃中的 Alpha 信号" — IC=10.96%
  - arXiv:2601.08962 (2026-01) "Warp Speed Price Moves: Jumps after Earnings" — 预平均 BPV
  - 西部证券 (2026-03) "用隔夜交易策略增强指数增强" — RankIC=-0.1687
  - 国盛证券 (2026-03) "异动雷达事件簇" — IR=2.92
  - 西部证券 (2026-03) "知情交易微观行为 IT 因子" — RankIC=0.064
  - AStockEvent Feed PyPI 0.2.1 (2026-06-08) — 13+ 事件类型结构化
  - 招商证券 (2009-2020 回测) dReport 年化超额 4.88% / Sharpe 1.44
  - Zhou & Zhu (2012 FAJ) long positive-jump + short negative-jump 年化 15.3%
  - Barndorff-Nielsen & Shephard (2004) BPV 双幂变异

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | 六因子矩阵(PEAD/dReport/Jump/隔夜/AStockEvent/异动雷达)+事件冲击评分+信号合成算法化；整合 2026-08 研究（PEAD.txt/Rockstead 双因子/华泰 JumpPEAD/西部隔夜/国盛异动/AStockEvent Feed） |
| 2026-08-10 | 1.1.0 | 新增 §3.10-§3.11 | 龙虎榜Smart Money因子（净买率>12%次日+3.10%/20日+5.11%，合力型vs独食型，假机构陷阱识别，席位身份画像，第7辅助因子）；EVOQUANT LLM策略自演化优化（arXiv:2607.12455v1 2026-07，Sharpe -0.298→0.538，Phase 2+远期候选） |
