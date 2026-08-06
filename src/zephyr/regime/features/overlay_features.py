# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 D-SIGNAL-68
# [MODULE] zephyr.regime.features.overlay_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] MOD-REGIME-002(OverlaySignalsConstructor消费8转换评分→overlay_signals)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] score维度∈[0,100]; flag维度∈{0,1}; 无信号=0(平时不干预); PIT由调用方shift(1)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_overlay_signals_builder.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #discussion_001 §4 #D-SIGNAL-68 #Phase2b
"""overlay_signals 8 转换评分纯函数（MOD-REGIME-002 Phase 2b）。

把 HMM 6 特征 + 代理 OHLCV 映射成 8 转换（T1-T6/S1/S2）的各维度评分（0-100）或
标志（0/1），供 OverlaySignalsConstructor 组装 overlay_signals 喂 RegimeDetector._run_overlay。

设计原则（discussion_001 §4 + Phase 2b 计划 §C1不退化保护）：
  - **无信号 = 0**：平时所有维度评分 0 → 无转换触发 → overlay 不干预（C1 不退化前提）
  - **保守阈值**：维度 >= 60（触发门槛）只在明确信号时达到，避免常态误触发
  - **PIT 由调用方负责**：本模块函数纯计算，shift(1) 在 OverlaySignalsConstructor._precompute 统一做

31 个维度 key（对齐 TRANSITION_CONFIG 的 keys_gte）：
  可算 25 个：vix_panic/correlation/liquidity/flash_recover（S1）
              capitulation/vix/wyckoff/valuation/fund/spring/three_yang/break_sc_low/vix_new_high/fund_outflow（S2）
              bqs/rcs/frs（T1）, continue_decline（T2）
              volume_price/ma_trend/sentiment（T3）, shrink_flat（T4）
              leader_break/rebound_wrap（T5）, sudden_volume（T6）
  stub 6 个（=0）：bad_news_flat/policy（S2, NLP）, money_effect/mainline/leader/one_day_mainline（T3, 资金/板块）

依据: discussion_001 v1.3.1 §4 / Phase 2 计划 §Phase2b
Version: 0.1.0
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    # S1
    "s1_vix_panic_score",
    "s1_correlation_score",
    "s1_liquidity_score",
    "s1_flash_recover_flag",
    # S2
    "s2_capitulation_score",
    "s2_vix_score",
    "s2_wyckoff_score",
    "s2_valuation_score",
    "s2_fund_score",
    "s2_spring_flag",
    "s2_three_yang_flag",
    "s2_break_sc_low_flag",
    "s2_vix_new_high_flag",
    "s2_fund_outflow_flag",
    # T1
    "t1_bqs_score",
    "t1_rcs_score",
    "t1_frs_score",
    # T2
    "t2_continue_decline_flag",
    # T3
    "t3_volume_price_score",
    "t3_ma_trend_score",
    "t3_sentiment_score",
    # T4
    "t4_shrink_flat_flag",
    # T5
    "t5_leader_break_score",
    "t5_rebound_wrap_flag",
    # T6
    "t6_sudden_volume_flag",
]


# ---------------------------------------------------------------------------
# S1: Any → CRISIS（VIX Panic + Correlation + Liquidity）
# ---------------------------------------------------------------------------

def s1_vix_panic_score(vol_pct: pd.Series) -> pd.Series:
    """S1 vix_panic: vol_pct → 0-100（VIX 恐慌代理，vol_pct=实现波动率分位）。

    映射（对齐 S1 trigger 门槛 vix_panic>=60）：
      vol_pct>0.95 → 100  （极端恐慌）
      vol_pct>0.90 → 85   （危机级高波，触发门槛以上）
      vol_pct>0.85 → 65   （高波，刚过触发门槛）
      vol_pct>0.75 → 40   （偏高波，未达门槛）
      else        → 0     （正常，无恐慌）

    与 #1 realized_vol_coef 对齐：vol_pct>0.90+下跌→#1=0.30（危机地板），
    S1 vix_panic>85 → 与 #1 危机区重合，提供 overlay 层 CRISIS 概率叠加。
    """
    score = pd.Series(0.0, index=vol_pct.index)
    score[vol_pct > 0.75] = 40
    score[vol_pct > 0.85] = 65
    score[vol_pct > 0.90] = 85
    score[vol_pct > 0.95] = 100
    return score


def s1_correlation_score(corr: pd.Series) -> pd.Series:
    """S1 correlation: cross_asset_corr → 0-100（恐慌期相关性→1）。

    映射（对齐 S1 trigger 门槛 correlation>=60）：
      corr>0.97 → 95  （极端收敛，系统性恐慌）
      corr>0.95 → 80  （高相关，危机信号）
      corr>0.93 → 65  （刚过触发门槛）
      corr>0.85 → 30  （偏高相关，非危机常态）
      else     → 0    （正常分散）
    """
    score = pd.Series(0.0, index=corr.index)
    c = corr.fillna(0.0)
    score[c > 0.85] = 30
    score[c > 0.93] = 65
    score[c > 0.95] = 80
    score[c > 0.97] = 95
    return score


def s1_liquidity_score(vol_z: pd.Series) -> pd.Series:
    """S1 liquidity: volume_anomaly z-score → 0-100（流动性压力代理）。

    危机期成交量飙升（恐慌抛售）或枯竭（无人接盘）= 流动性压力。
    用 |vol_z| 衡量成交量异常程度（正负均算压力）。

    映射（对齐 S1 confirm 门槛 liquidity>=60）：
      |z|>3  → 90  （极端成交量异常）
      |z|>2  → 70  （严重异常，过门槛）
      |z|>1.5→ 45  （中度异常，未达门槛）
      else   → 0   （正常）
    """
    score = pd.Series(0.0, index=vol_z.index)
    az = vol_z.fillna(0.0).abs()
    score[az > 1.5] = 45
    score[az > 2.0] = 70
    score[az > 3.0] = 90
    return score


def s1_flash_recover_flag(pct_change: pd.Series, vol_pct: pd.Series) -> pd.Series:
    """S1 flash_recover: 闪崩恢复标志（0/1）。

    前一日 vol_pct>0.90（危机）+ 当日 pct_change>3%（暴力反弹）= 闪崩恢复。
    用于 S1 fail 判定：危机中突然反弹 → 可能是假危机（flash crash 恢复）。
    """
    flag = pd.Series(0.0, index=pct_change.index)
    prev_crisis = vol_pct.fillna(0.0).shift(1) > 0.90
    big_up = pct_change.fillna(0.0) > 0.03
    flag[prev_crisis & big_up] = 1.0
    return flag


# ---------------------------------------------------------------------------
# S2: CRISIS → RECOVERY（八维度见底）
# ---------------------------------------------------------------------------

def s2_capitulation_score(vol_z: pd.Series, pct_change: pd.Series) -> pd.Series:
    """S2 capitulation: 投降式抛售 → 0-100（成交量飙升 + 暴跌）。

    Capitulation = 被动强制清算，特征为成交量 3-5 倍均量 + 长下影线 + 暴跌。
    用 vol_z（量能异动 z-score）× pct_change（涨跌幅）交集衡量。

    映射（对齐 S2 trigger 门槛 capitulation>=60）：
      z>3 & 跌>4%  → 90  （极端投降抛售）
      z>2 & 跌>3%  → 70  （严重投降，过门槛）
      z>2 & 跌>1.5%→ 50  （放量下跌，未达门槛）
      else        → 0    （无投降信号）
    """
    score = pd.Series(0.0, index=vol_z.index)
    z = vol_z.fillna(0.0)
    pct = pct_change.fillna(0.0)
    score[(z > 2) & (pct < -0.015)] = 50
    score[(z > 2) & (pct < -0.03)] = 70
    score[(z > 3) & (pct < -0.04)] = 90
    return score


def s2_vix_score(vol_pct: pd.Series) -> pd.Series:
    """S2 vix: VIX 见顶回落 → 0-100（vol_pct 从高位下降）。

    VIX>35 后回落至<30 = 恐慌消退信号。用 vol_pct 代理：
    前一日 vol_pct>0.85（恐慌区）+ 当日 vol_pct 下降 → 见顶回落。

    映射（对齐 S2 trigger 门槛 vix>=40）：
      前日>0.90 & 当日降>0.10 → 80  （VIX 暴跌，恐慌消退）
      前日>0.85 & 当日降>0.05 → 60  （VIX 回落，过门槛）
      前日>0.85 & 当日降>0    → 40  （VIX 微降，刚达门槛）
      else                   → 0   （无回落信号）
    """
    score = pd.Series(0.0, index=vol_pct.index)
    vp = vol_pct.fillna(0.0)
    prev_vp = vp.shift(1)
    decline = prev_vp - vp
    was_crisis = prev_vp > 0.85
    score[was_crisis & (decline > 0)] = 40
    score[was_crisis & (decline > 0.05)] = 60
    score[(prev_vp > 0.90) & (decline > 0.10)] = 80
    return score


def s2_wyckoff_score(close: pd.Series, window: int = 20) -> pd.Series:
    """S2 wyckoff: Wyckoff 吸筹结构简化版 → 0-100（TR 收窄 + 价格在中上部）。

    MVP 简化：计算近 window 日的价格区间（high-low）/ close，
    区间收窄（低波动率震荡）+ 价格在区间上半部 = 吸筹结构。

    映射（对齐 S2 confirm 门槛 wyckoff>=60）：
      range<2% & pos>0.6 → 70  （窄幅整理+中上部，吸筹特征）
      range<3% & pos>0.5 → 50  （区间整理，未达门槛）
      range<5%           → 25  （波幅收窄，初步信号）
      else               → 0   （波幅过大，非吸筹）
    """
    score = pd.Series(0.0, index=close.index)
    rolling_high = close.rolling(window).max()
    rolling_low = close.rolling(window).min()
    range_pct = (rolling_high - rolling_low) / close
    pos = (close - rolling_low) / (rolling_high - rolling_low + 1e-8)
    score[range_pct < 0.05] = 25
    score[(range_pct < 0.03) & (pos > 0.5)] = 50
    score[(range_pct < 0.02) & (pos > 0.6)] = 70
    return score


def s2_valuation_score(close: pd.Series, window: int = 250) -> pd.Series:
    """S2 valuation: 估值极端 → 0-100（close 远低于 rolling_max = 深度折价）。

    pos = close / rolling_max(close, 250)。pos 越低 = 距高点越远 = 估值越有吸引力。

    映射（对齐 S2 confirm 门槛 valuation>=40）：
      pos<0.30 → 80  （距高点-70%，极端低估）
      pos<0.40 → 60  （距高点-60%，深度折价）
      pos<0.50 → 40  （距高点-50%，刚达门槛）
      pos<0.60 → 20  （中度回撤，未达门槛）
      else     → 0   （接近高点，无估值吸引力）
    """
    score = pd.Series(0.0, index=close.index)
    rolling_max = close.rolling(window).max()
    pos = close / rolling_max
    score[pos < 0.60] = 20
    score[pos < 0.50] = 40
    score[pos < 0.40] = 60
    score[pos < 0.30] = 80
    return score


def s2_fund_score(volume: pd.Series, window: int = 20) -> pd.Series:
    """S2 fund: 资金承接 → 0-100（成交量放大 = 资金流入）。

    MVP 代理：近 window 日均量 vs 前 window 日均量，放大 = 资金流入。
    完整版需 money_flow 表的净流入数据。

    映射（对齐 S2 confirm 门槛 fund>=50）：
      均量比>1.5 → 70  （量能显著放大，资金流入）
      均量比>1.2 → 50  （量能放大，刚达门槛）
      均量比>1.0 → 25  （量能微增，未达门槛）
      else       → 0   （量能萎缩，无资金承接）
    """
    score = pd.Series(0.0, index=volume.index)
    recent_avg = volume.rolling(window).mean()
    prev_avg = volume.shift(window).rolling(window).mean()
    ratio = recent_avg / (prev_avg + 1e-8)
    score[ratio > 1.0] = 25
    score[ratio > 1.2] = 50
    score[ratio > 1.5] = 70
    return score


def s2_spring_flag(close: pd.Series, window: int = 20) -> pd.Series:
    """S2 spring: Wyckoff Spring 震仓标志（0/1）。

    Spring = 价格跌破近 window 日低点后收回（假跌破诱空）。
    当日 low < rolling_min(low, window).shift(1) 但 close > rolling_min.shift(1)。
    简化：用 close 判断（无 low 数据时），close 跌破前低后当日收回。
    """
    flag = pd.Series(0.0, index=close.index)
    prior_low = close.rolling(window).min().shift(1)
    # 简化 Spring：当日 close 曾低于前低（close<prev_low.shift(1) 的 rolling min）
    # 但最终 close > prior_low（收回）。由于只有 close，用日内 close 判断：
    # 前一日 close < prior_low（跌破），当日 close > prior_low（收回）
    broke_prev = close.shift(1) < prior_low.shift(1)
    recovered = close > prior_low
    flag[broke_prev & recovered] = 1.0
    return flag


def s2_three_yang_flag(pct_change: pd.Series) -> pd.Series:
    """S2 three_yang: 三阳开泰标志（0/1）——连续 3 日上涨。

    底部连续 3 根阳线 = 需求信号（三阳开泰），S2 strong_confirm 条件之一。
    """
    flag = pd.Series(0.0, index=pct_change.index)
    up = pct_change.fillna(0.0) > 0
    three_up = up & up.shift(1) & up.shift(2)
    flag[three_up] = 1.0
    return flag


def s2_break_sc_low_flag(close: pd.Series, window: int = 20) -> pd.Series:
    """S2 break_sc_low: 跌破 SC（抛售高潮）低点标志（0/1）——S2 fail 条件。

    价格跌破近 window 日最低点 = 危机未尽，见底失败。
    """
    flag = pd.Series(0.0, index=close.index)
    prior_low = close.rolling(window).min().shift(1)
    flag[close < prior_low] = 1.0
    return flag


def s2_vix_new_high_flag(vol_pct: pd.Series, window: int = 60) -> pd.Series:
    """S2 vix_new_high: VIX 创新高标志（0/1）——S2 fail 条件。

    vol_pct 创 window 日新高 = 恐慌加剧，见底失败。
    """
    flag = pd.Series(0.0, index=vol_pct.index)
    rolling_max = vol_pct.rolling(window).max().shift(1)
    flag[vol_pct > rolling_max] = 1.0
    return flag


def s2_fund_outflow_flag(volume: pd.Series, pct_change: pd.Series, window: int = 20) -> pd.Series:
    """S2 fund_outflow: 资金流出标志（0/1）——S2 fail 条件。

    近 window 日均量下降 + 价格下跌 = 资金持续流出。
    """
    flag = pd.Series(0.0, index=volume.index)
    recent_avg = volume.rolling(window).mean()
    prev_avg = volume.shift(window).rolling(window).mean()
    vol_declining = recent_avg < prev_avg
    price_declining = pct_change.rolling(window).sum().fillna(0.0) < 0
    flag[vol_declining & price_declining] = 1.0
    return flag


# ---------------------------------------------------------------------------
# T1: Neutral-Medium → BREAKOUT（突破主升苗头）
# ---------------------------------------------------------------------------

def t1_bqs_score(close: pd.Series, volume: pd.Series, window: int = 60) -> pd.Series:
    """T1 bqs: 突破质量 → 0-100（价格破 rolling max + 量能确认）。

    映射（对齐 T1 trigger 门槛 bqs>=60）：
      破60日高 & 放量(z>2) → 80  （量价齐升突破，高质量）
      破60日高 & 放量(z>1) → 65  （量价配合，过门槛）
      破60日高             → 40  （突破但无量，未达门槛）
      else                 → 0   （无突破）
    """
    score = pd.Series(0.0, index=close.index)
    rolling_max = close.rolling(window).max().shift(1)
    breakout = close > rolling_max
    vol_z = (volume - volume.rolling(20).mean()) / (volume.rolling(20).std() + 1e-8)
    score[breakout] = 40
    score[breakout & (vol_z > 1)] = 65
    score[breakout & (vol_z > 2)] = 80
    return score


def t1_rcs_score(slope: pd.Series, hurst: pd.Series) -> pd.Series:
    """T1 rcs: 相对强度 → 0-100（斜率正 + Hurst>0.5 = 趋势确认）。

    映射（对齐 T1 confirm 门槛 rcs>=60）：
      slope>0 & hurst>0.55 → 70  （强趋势+持续性）
      slope>0 & hurst>0.50 → 55  （趋势+弱持续，未达门槛）
      slope>0              → 30  （正斜率，无持续确认）
      else                 → 0   （无趋势）
    """
    score = pd.Series(0.0, index=slope.index)
    s = slope.fillna(0.0)
    h = hurst.fillna(0.5)
    score[s > 0] = 30
    score[(s > 0) & (h > 0.50)] = 55
    score[(s > 0) & (h > 0.55)] = 70
    return score


def t1_frs_score(vol_pct: pd.Series, slope: pd.Series) -> pd.Series:
    """T1 frs: 失败风险 → 0-100（高波 + 斜率衰竭 = 突破可能失败）。

    映射（对齐 T1 fail 门槛 frs>=60）：
      vol_pct>0.85 & slope降 → 70  （高波+动能衰减，高风险）
      vol_pct>0.75 & slope降 → 55  （偏高波+衰减，未达门槛）
      vol_pct>0.85           → 40  （高波，初步风险）
      else                   → 0   （低波，风险低）
    """
    score = pd.Series(0.0, index=vol_pct.index)
    vp = vol_pct.fillna(0.0)
    s = slope.fillna(0.0)
    slope_declining = s < s.shift(5)
    score[vp > 0.85] = 40
    score[(vp > 0.75) & slope_declining] = 55
    score[(vp > 0.85) & slope_declining] = 70
    return score


# ---------------------------------------------------------------------------
# T2: Bear-Low → RECOVERY（冰点反核）
# ---------------------------------------------------------------------------

def t2_continue_decline_flag(slope: pd.Series, vol_pct: pd.Series) -> pd.Series:
    """T2 continue_decline: 持续下跌标志（0/1）——T2 fail 条件。

    斜率 < 0（下跌趋势）+ vol_pct > 0.75（高波动）= 继续下跌，未到冰点。
    """
    flag = pd.Series(0.0, index=slope.index)
    s = slope.fillna(0.0)
    vp = vol_pct.fillna(0.0)
    flag[(s < 0) & (vp > 0.75)] = 1.0
    return flag


# ---------------------------------------------------------------------------
# T3: RECOVERY → BREAKOUT（主升确立）
# ---------------------------------------------------------------------------

def t3_volume_price_score(pct_change: pd.Series, vol_z: pd.Series) -> pd.Series:
    """T3 volume_price: 量价配合 → 0-100（上涨 + 放量）。

    映射（对齐 T3 confirm 门槛 volume_price>=60）：
      涨>2% & z>2 → 80  （放量大涨，强配合）
      涨>1% & z>1 → 65  （量价齐升，过门槛）
      涨>0  & z>0 → 35  （正方向，未达门槛）
      else        → 0   （无量或下跌）
    """
    score = pd.Series(0.0, index=pct_change.index)
    pct = pct_change.fillna(0.0)
    z = vol_z.fillna(0.0)
    score[(pct > 0) & (z > 0)] = 35
    score[(pct > 0.01) & (z > 1)] = 65
    score[(pct > 0.02) & (z > 2)] = 80
    return score


def t3_ma_trend_score(close: pd.Series) -> pd.Series:
    """T3 ma_trend: 均线趋势 → 0-100（MA5 > MA20 > MA60 多头排列强度）。

    映射（对齐 T3 confirm 门槛 ma_trend>=50）：
      MA5>MA20>MA60 & MA5/MA60>1.05 → 70  （强多头排列）
      MA5>MA20>MA60                 → 60  （多头排列，过门槛）
      MA5>MA20                      → 30  （短期多头，未达门槛）
      else                          → 0   （非多头）
    """
    score = pd.Series(0.0, index=close.index)
    ma5 = close.rolling(5).mean()
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()
    short_up = ma5 > ma20
    full_up = (ma5 > ma20) & (ma20 > ma60)
    strong = full_up & (ma5 / ma60 > 1.05)
    score[short_up] = 30
    score[full_up] = 60
    score[strong] = 70
    return score


def t3_sentiment_score(ad_ratio: pd.Series) -> pd.Series:
    """T3 sentiment: 市场情绪 → 0-100（ad_ratio > 0 = 涨多跌少）。

    映射（对齐 T3 trigger 门槛 sentiment>=60）：
      ad_ratio>0.6  → 80  （普涨，强情绪）
      ad_ratio>0.3  → 65  （涨多跌少，过门槛）
      ad_ratio>0    → 35  （偏多，未达门槛）
      else          → 0   （偏空或中性）
    """
    score = pd.Series(0.0, index=ad_ratio.index)
    a = ad_ratio.fillna(0.0)
    score[a > 0] = 35
    score[a > 0.3] = 65
    score[a > 0.6] = 80
    return score


# ---------------------------------------------------------------------------
# T4: Bull-Medium → Bull-High（疯狂期赶顶）
# ---------------------------------------------------------------------------

def t4_shrink_flat_flag(vol_pct: pd.Series) -> pd.Series:
    """T4 shrink_flat: 波幅收窄标志（0/1）——T4 fail 条件。

    vol_pct 5 日均值 < 前 5 日均值 = 波动率下降（收窄），非赶顶特征。
    """
    flag = pd.Series(0.0, index=vol_pct.index)
    vp = vol_pct.fillna(0.0)
    recent = vp.rolling(5).mean()
    prev = vp.shift(5).rolling(5).mean()
    flag[recent < prev] = 1.0
    return flag


# ---------------------------------------------------------------------------
# T5: Bull-High → Bear-Medium（逃顶退潮）
# ---------------------------------------------------------------------------

def t5_leader_break_score(close: pd.Series, volume: pd.Series) -> pd.Series:
    """T5 leader_break: 领涨股破位 → 0-100（价格跌破 MA20 + 放量）。

    MVP 用市场代理代替领涨股：close < MA20 + 放量 = 破位信号。

    映射（对齐 T5 trigger 门槛 leader_break>=60）：
      close<MA20 & z>2 → 75  （放量跌破MA20，强破位）
      close<MA20 & z>1 → 60  （量价配合破位，过门槛）
      close<MA20       → 30  （跌破MA20无量，未达门槛）
      else             → 0   （在线上）
    """
    score = pd.Series(0.0, index=close.index)
    ma20 = close.rolling(20).mean()
    below = close < ma20
    vol_z = (volume - volume.rolling(20).mean()) / (volume.rolling(20).std() + 1e-8)
    score[below] = 30
    score[below & (vol_z > 1)] = 60
    score[below & (vol_z > 2)] = 75
    return score


def t5_rebound_wrap_flag(close: pd.Series) -> pd.Series:
    """T5 rebound_wrap: 反弹结束标志（0/1）——T5 fail 条件。

    价格反弹至 MA20 后回落（高点低于前高 = 反弹 wraps up）。
    简化：前日 close > MA20（反弹到线上），当日 close < MA20（重新跌破）。
    """
    flag = pd.Series(0.0, index=close.index)
    ma20 = close.rolling(20).mean()
    was_above = close.shift(1) > ma20.shift(1)
    now_below = close < ma20
    flag[was_above & now_below] = 1.0
    return flag


# ---------------------------------------------------------------------------
# T6: Bear-Medium → Bear-Low（退潮冰点）
# ---------------------------------------------------------------------------

def t6_sudden_volume_flag(vol_z: pd.Series, pct_change: pd.Series) -> pd.Series:
    """T6 sudden_volume: 突然放量标志（0/1）——T6 fail 条件。

    在下跌趋势中突然放量（z > 2）= 恐慌抛售 / 冰点放量，可能见底。
    要求前 5 日累计跌幅 < 0（下跌趋势中）。
    """
    flag = pd.Series(0.0, index=vol_z.index)
    z = vol_z.fillna(0.0)
    recent_trend = pct_change.rolling(5).sum().fillna(0.0)
    flag[(z > 2) & (recent_trend < 0)] = 1.0
    return flag
