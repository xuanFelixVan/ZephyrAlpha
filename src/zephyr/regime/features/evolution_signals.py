# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.6
# [MODULE] zephyr.regime.features.evolution_signals
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] 演进方向评估（未接入生产调用链，见模块 docstring 范围声明）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 评分∈[0,100]; flag∈{0,1}; 无信号=0; 纯 OHLCV 可算无需新数据; PIT由调用方shift(1)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入空Series->返回空/全0不抛; 滞回 enter<=exit->ValueError
# [TESTS] tests/regime/features/test_evolution_signals.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #14_regime_s2_diagnosis §4.6 演进方向 #3/#5/#6
# [ALGO_FLOW]
# I1: signal(衰减信号 Series, 滞回用)
# I2: open/high/low/close/volume(OHLCV 五序列, EVR/flush 用)
# F1: hysteresis_edge_trigger(双阈值状态机: >=enter 置1, <=exit 置0, 区间保持, NaN 保持)
# F2: s2_evr_score(EVR 核心60: 量>1.6x均量+实体极小; ADL 三模式: 经典背离80/吸筹脉冲70/隐形吸筹50; 四分量取 max)
# F3: s2_flush_flag(N日新低+收盘回前日区间+下影>50%+量>2x均量 四合取 → 0/1)
# O1: 滞回状态 Series{0,1} / EVR 评分 Series[0,100] / flush flag Series{0,1}
# [/ALGO_FLOW]
"""S2 演进方向小型组（14_regime_s2_diagnosis §4.6 #3/#5/#6，P2+ 函数级落地）。

三个 2026 研究发现的更优算法，纯 OHLCV 可算、无需新数据管道：

  1. **滞回边沿触发器**（Modgil, arXiv:2606.19386, 2026-06）：衰减信号做阈值触发时
     带滞回（触发 60/解除 40），避免衰减曲线在阈值附近震荡反复触发——ArXiv 实证
     滞回触发每轨迹仅 0-3 次 vs 持续报警 20/20。配 §4.1 capitulation 衰减加权和
     这类衰减信号使用（P1-E9 验证若发现反复触发再加，本批先交付函数）。

  2. **EVR 量价背离**（WyckoffTradingAgent 2026-05 + FibAlgo 2026-02 ADL 三模式）：
     EVR（Effort vs Result）= 量>1.6×均量 + 实体极小（平盘）= 主力暗中吸筹
     （放巨量但价格没动）。与 capitulation（恐慌卖出）互补，可作 S2 confirm 辅助
     维度或 wyckoff_score 加分项。ADL 可计算代理三模式：经典背离（价格新低但
     ADL 更高低 + 收盘位置由下 25% 改善至上 50%）/ 吸筹脉冲（大跌日 ADL 暴增，
     2020-03-23 新冠底实例）/ 隐形吸筹（ADL 走平微升而价格阴跌 7-10 日）。

  3. **flush 桥接信号**（TradingSim 2026-05）：capitulation 末端最终暴跌（扫掉最后
     弱手），是 capitulation（过程）→ spring（收回）的时序桥接：当日 low 创 N 日
     新低 + 收盘回前日区间 + 下影线>50% + 量>2×均量；可作 strong_confirm 时序前置。

**范围声明**：三函数未接入 overlay_signals_builder 生产调用链（_TRANSITION_DIMS
未注册新维度）——演进方向定位是"验证后按需启用"的备选算法库，接入需经
TRANSITION_CONFIG 评审（防过拟合铁律：禁止为跑分而加维度）。

依据: 14_regime_s2_diagnosis v0.5.2 §4.6
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "hysteresis_edge_trigger",
    "s2_evr_score",
    "s2_flush_flag",
]

_EPS = 1e-12


def hysteresis_edge_trigger(
    signal: pd.Series,
    enter: float = 60.0,
    exit: float = 40.0,
) -> pd.Series:
    """滞回边沿触发器（14 号 §4.6 #3，arXiv:2606.19386）→ 状态 Series {0.0, 1.0}。

    双阈值状态机：signal >= enter 进入（置 1），signal <= exit 解除（置 0），
    (exit, enter) 区间保持原状态——衰减信号在单阈值附近震荡时不再反复触发。
    NaN 保持原状态（数据缺口不翻转状态机）。

    Args:
        signal: 衰减/波动信号序列（如 capitulation 衰减加权和）。
        enter: 进入阈值（默认 60，对齐 S2 trigger 量级）。
        exit: 解除阈值（默认 40），必须 < enter。

    Returns:
        pd.Series(float64)：0.0=未触发 / 1.0=触发保持中。
    """
    if enter <= exit:
        raise ValueError(f"enter({enter}) 必须 > exit({exit})，滞回区间为空")
    values = signal.to_numpy(dtype=float)
    out = np.zeros(len(values), dtype=float)
    state = 0.0
    for i, v in enumerate(values):
        if not np.isnan(v):
            if v >= enter:
                state = 1.0
            elif v <= exit:
                state = 0.0
        out[i] = state
    return pd.Series(out, index=signal.index)


def s2_evr_score(
    open: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    vol_window: int = 20,
    vol_mult: float = 1.6,
    body_pct: float = 0.005,
    div_lookback: int = 60,
    div_span: int = 5,
    pulse_pct: float = -0.03,
    pulse_q: float = 0.95,
    pulse_window: int = 250,
    drift_days: int = 7,
) -> pd.Series:
    """S2 EVR 量价背离评分 → 0-100（14 号 §4.6 #5，四分量取 max）。

    分量（分值为信号强度，对齐 S2 维度 0-100 口径）：
      - **EVR 核心（60）**：量 > vol_mult×vol_window 均量 + 实体极小
        （|close-open|/prev_close < body_pct=0.5% 平盘）= 放巨量价格没动，
        主力暗中吸筹（WyckoffTradingAgent 2026-05：量>1.6×+实体极小）。
      - **ADL 经典背离（80）**：价格新低（近 div_span 日最低 < 前 div_lookback-div_span
        日最低，跨度≥div_span 日）但 ADL 更高低（近 div_span 日 ADL 最低 > 前窗 ADL
        最低），且当日收盘位置 (close-low)/(high-low) > 0.5（由下 25% 区间改善至上
        50%，FibAlgo 2026-02）。
      - **ADL 吸筹脉冲（70）**：大跌日（pct_change < -3%）ADL 单日增量 > 近
        pulse_window 日 pulse_q=95% 分位（2020-03-23 新冠底实例）。
      - **ADL 隐形吸筹（50）**：价格阴跌（close < close.shift(drift_days)）而 ADL
        走平/微升（adl >= adl.shift(drift_days)）。

    ADL = cumsum(mfm × volume)，mfm = [(close-low)-(high-close)]/(high-low)
    （纯 OHLCV 可算）。无信号 = 0（平时不干预）。
    """
    idx = close.index
    prev_close = close.shift(1)
    mfm = ((close - low) - (high - close)) / (high - low + _EPS)
    adl = (mfm * volume).cumsum()

    # 分量 1：EVR 核心——放巨量 + 平盘（effort 巨大 result 极小 = 吸筹）
    vol_surge = volume > volume.rolling(vol_window).mean() * vol_mult
    tiny_body = (close - open).abs() / (prev_close.abs() + _EPS) < body_pct
    evr_core = vol_surge & tiny_body

    # 分量 2：ADL 经典背离——价新低 + ADL 更高低 + 收盘位置改善
    price_ll = close.rolling(div_span).min() < close.shift(div_span).rolling(div_lookback - div_span).min()
    adl_hl = adl.rolling(div_span).min() > adl.shift(div_span).rolling(div_lookback - div_span).min()
    close_pos = (close - low) / (high - low + _EPS)
    divergence = price_ll & adl_hl & (close_pos > 0.5)

    # 分量 3：吸筹脉冲——大跌日 ADL 暴增
    pct_change = close.pct_change()
    adl_delta = adl.diff()
    pulse_thr = adl_delta.rolling(pulse_window, min_periods=60).quantile(pulse_q)
    pulse = (pct_change < pulse_pct) & (adl_delta > pulse_thr)

    # 分量 4：隐形吸筹——价格阴跌而 ADL 走平/微升
    hidden = (close < close.shift(drift_days)) & (adl >= adl.shift(drift_days))

    score = pd.Series(0.0, index=idx)
    score[hidden.fillna(False)] = 50
    score[evr_core.fillna(False)] = 60
    score[pulse.fillna(False)] = 70
    score[divergence.fillna(False)] = 80
    return score


def s2_flush_flag(
    open: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    window: int = 60,
    vol_window: int = 20,
    vol_mult: float = 2.0,
) -> pd.Series:
    """S2 flush 桥接信号 → {0.0, 1.0}（14 号 §4.6 #6，TradingSim 2026-05）。

    flush = capitulation 末端最终暴跌（扫掉最后弱手），是 capitulation（过程）
    → spring（收回）的时序桥接，可作 strong_confirm 时序前置条件。

    四条件合取（量化按 memo §4.6 #6）：
      1. 当日 low 创 window 日新低（low < 前 window 日最低 low）
      2. 收盘回前日区间（close >= 前日 low，卖盘被吸收收回）
      3. 下影线 > 50% K 线振幅（(min(open,close)-low)/(high-low) > 0.5）
      4. 量 > vol_mult×vol_window 日均量（2× 放量）
    """
    new_low = low < low.shift(1).rolling(window).min()
    recovered = close >= low.shift(1)
    wick_ratio = (np.minimum(open, close) - low) / (high - low + _EPS)
    strong_wick = wick_ratio > 0.5
    vol_surge = volume > volume.rolling(vol_window).mean() * vol_mult
    flag = new_low & recovered & strong_wick & vol_surge
    return flag.fillna(False).astype(float)
