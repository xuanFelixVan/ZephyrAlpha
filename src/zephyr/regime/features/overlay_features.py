# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 D-SIGNAL-68
# [MODULE] zephyr.regime.features.overlay_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] MOD-REGIME-002(OverlaySignalsConstructor消费8转换评分→overlay_signals)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] score维度∈[0,100]; flag维度∈{0,1}; 无信号=0(平时不干预); PIT由调用方shift(1)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_overlay_signals_builder.py; tests/regime/test_overlay_features.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4 #D-SIGNAL-68 #Phase2b
"""overlay_signals 8 转换评分纯函数（MOD-REGIME-002 Phase 2b）。

把 HMM 6 特征 + 代理 OHLCV 映射成 8 转换（T1-T6/S1/S2）的各维度评分（0-100）或
标志（0/1），供 OverlaySignalsConstructor 组装 overlay_signals 喂 RegimeDetector._run_overlay。

设计原则（10_regime_detector_spec §4 + Phase 2b 计划 §C1不退化保护）：
  - **无信号 = 0**：平时所有维度评分 0 → 无转换触发 → overlay 不干预（C1 不退化前提）
  - **保守阈值**：维度 >= 60（触发门槛）只在明确信号时达到，避免常态误触发
  - **PIT 由调用方负责**：本模块函数纯计算，shift(1) 在 OverlaySignalsConstructor._precompute 统一做

31 个维度 key（对齐 TRANSITION_CONFIG 的 keys_gte）：
  可算 29 个：vix_panic/correlation/liquidity/flash_recover（S1）
              capitulation/vix/wyckoff/valuation/fund/spring/three_yang/break_sc_low/vix_new_high/fund_outflow（S2）
              bqs/rcs/frs（T1）, continue_decline（T2）
              volume_price/ma_trend/sentiment/money_effect/mainline/leader/one_day_mainline（T3）
              shrink_flat（T4）, leader_break/rebound_wrap（T5）, sudden_volume（T6）
  stub 2 个（=0）：bad_news_flat/policy（S2, NLP，待 NLP 管道）
  Phase 2c：money_effect/mainline/leader/one_day_mainline 从 stub 升级为可算（接 money_flow/kline_sector/limit_up_down）

依据: 10_regime_detector_spec v1.3.1 §4 / Phase 2 计划 §Phase2b
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
    "s2_policy_score",
    "s2_bad_news_flat_score",
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
    "t3_money_effect_score",
    "t3_mainline_score",
    "t3_leader_score",
    "t3_one_day_mainline_flag",
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


def s1_vix_panic_score(vol_pct: pd.Series, vix_pct: pd.Series | None = None) -> pd.Series:
    """S1 vix_panic: VIX 恐慌代理 → 0-100。

    Phase 2c：vix_pct（合成 VIX 历史分位）非空时优先用，回退 vol_pct
    （实现波动率分位）。两者接口同构（∈[0,1]），阈值不变。

    per-element 回退：vix_pct 在 warmup 期（前 hv_window+pct_window≈270 日）
    或局部缺失时为 NaN，此时该日回退 vol_pct——避免 warmup 期 vix_panic 错误
    归零（warmup 内 vol_pct 仍是有效信号，与 Phase 2a/2b 行为一致，C1 不退化）。

    映射（对齐 S1 trigger 门槛 vix_panic>=60）：
      >0.95 → 100  （极端恐慌）
      >0.90 → 85   （危机级高波，触发门槛以上）
      >0.85 → 65   （高波，刚过触发门槛）
      >0.75 → 40   （偏高波，未达门槛）
      else  → 0    （正常，无恐慌）

    与 #1 realized_vol_coef 对齐：vol_pct>0.90+下跌→#1=0.30（危机地板），
    S1 vix_panic>85 → 与 #1 危机区重合，提供 overlay 层 CRISIS 概率叠加。
    """
    if vix_pct is not None and not vix_pct.empty:
        # vix_pct 优先；其 NaN 处（warmup/局部缺失）per-element 回退 vol_pct
        src = vix_pct.combine_first(vol_pct)
    else:
        src = vol_pct
    score = pd.Series(0.0, index=src.index)
    score[src > 0.75] = 40
    score[src > 0.85] = 65
    score[src > 0.90] = 85
    score[src > 0.95] = 100
    return score


def s1_correlation_score(corr: pd.Series) -> pd.Series:
    """S1 correlation: cross_asset_corr → 0-100（恐慌期相关性→1）。

    P1 校准（12_regime_phase2_validation §9）：原 corr>0.93→65 门槛过高，A 股三大指数
    （沪深300/中证500/创业板指）危机期 corr 多在 0.86-0.93，导致 529 天
    vix_panic 达标但 correlation<60（B4 全部漏触发）。校准后 corr>0.85 即
    过 trigger 门槛（65），让系统性危机的高相关信号能被捕获。

    映射（对齐 S1 trigger 门槛 correlation>=60）：
      corr>0.97 → 100 （极端收敛，系统性恐慌）
      corr>0.95 → 90  （高相关，强危机信号）
      corr>0.90 → 80  （危机级高相关）
      corr>0.85 → 65  （偏高相关，刚过触发门槛）
      else     → 0    （正常分散）

    安全性：S1 trigger 需 vix_panic≥60 AND correlation≥60 双达标，vix_panic
    （合成 VIX 下行半偏差分位）已过滤常态低波动期，降低 corr 门槛不致误触发。
    """
    score = pd.Series(0.0, index=corr.index)
    c = corr.fillna(0.0)
    score[c > 0.85] = 65
    score[c > 0.90] = 80
    score[c > 0.95] = 90
    score[c > 0.97] = 100
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
      z>1 & 跌>3%  → 70  （严重投降，过门槛）
      z>1 & 跌>1.5%→ 50  （放量下跌，未达门槛）
      else        → 0    （无投降信号）

    注：原阈值 z>2 在持续高量危机期经验性不可达——2015 股灾期 vol_z max=1.79
   （z-score 对持续高量滚窗均值被抬高，单日 z 被压低）。2026-08-08 降至 z>1
   （~1σ，全局仍仅 ~16% 日达标，选择性足够）。
    """
    score = pd.Series(0.0, index=vol_z.index)
    z = vol_z.fillna(0.0)
    pct = pct_change.fillna(0.0)
    score[(z > 1) & (pct < -0.015)] = 50
    score[(z > 1) & (pct < -0.03)] = 70
    score[(z > 3) & (pct < -0.04)] = 90
    return score


def s2_vix_score(vol_pct: pd.Series, vix_pct: pd.Series | None = None) -> pd.Series:
    """S2 vix: VIX 见顶回落 → 0-100（从高位下降）。

    Phase 2c：vix_pct（合成 VIX 历史分位）非空时优先用，回退 vol_pct。
    VIX>35 后回落至<30 = 恐慌消退信号。前一日高位 + 当日下降 → 见顶回落。

    per-element 回退：vix_pct 在 warmup 期或局部缺失时为 NaN，该日回退 vol_pct
    （与 s1_vix_panic_score 一致，避免 warmup 期错误归零）。

    映射（对齐 S2 trigger 门槛 vix>=40）：
      前日>0.90 & 当日降>0.10 → 80  （VIX 暴跌，恐慌消退）
      前日>0.85 & 当日降>0.05 → 60  （VIX 回落，过门槛）
      前日>0.85 & 当日降>0    → 40  （VIX 微降，刚达门槛）
      else                   → 0   （无回落信号）
    """
    if vix_pct is not None and not vix_pct.empty:
        # vix_pct 优先；NaN 处（warmup/局部缺失）per-element 回退 vol_pct
        src = vix_pct.combine_first(vol_pct)
    else:
        src = vol_pct
    score = pd.Series(0.0, index=src.index)
    vp = src.fillna(0.0)
    prev_vp = vp.shift(1)
    decline = prev_vp - vp
    was_crisis = prev_vp > 0.85
    score[was_crisis & (decline > 0)] = 40
    score[was_crisis & (decline > 0.05)] = 60
    score[(prev_vp > 0.90) & (decline > 0.10)] = 80
    return score


def s2_wyckoff_score(
    close: pd.Series,
    high: pd.Series | None = None,
    low: pd.Series | None = None,
    volume: pd.Series | None = None,
    pct_change: pd.Series | None = None,
    vol_z: pd.Series | None = None,
    window: int = 60,
) -> pd.Series:
    """S2 wyckoff: Wyckoff 吸筹评分 → 0-100（Phase 2c 完整版优先，回退 MVP）。

    Phase 2c 完整版：提供 high/low/volume/pct_change/vol_z 时委托 wyckoff_engine
    做 6 阶段事件识别 + 累加评分（PS/SC/AR/ST/Spring/Test，Spring+40 是关键转折）。
    MVP 回退：仅 close 时用原简化版（TR 收窄 + 中上部位置），识别力弱但保证不抛错。

    映射（对齐 S2 confirm 门槛 wyckoff>=60）：
      完整版：Spring 出现累加 ≥60（过门槛）；MVP：range<2% & pos>0.6 → 70。
    """
    if high is not None and low is not None and volume is not None and pct_change is not None and vol_z is not None:
        from zephyr.regime.features.wyckoff_engine import wyckoff_score

        return wyckoff_score(close, high, low, volume, pct_change, vol_z, window)
    # MVP 简化版回退（仅 close，window 固定 20）
    score = pd.Series(0.0, index=close.index)
    rolling_high = close.rolling(20).max()
    rolling_low = close.rolling(20).min()
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
    # min_periods=20：避免 warmup 期（数据起点 < window）rolling_max=NaN → pos=NaN → 误零。
    # 实测 000300 kline 数据起点晚于 data_load_start，2015 年 rolling(250) 不足 250 非 NaN → 全零。
    rolling_max = close.rolling(window, min_periods=20).max()
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


def t3_money_effect_score(inflow_pct: pd.Series, limit_up_count: pd.Series) -> pd.Series:
    """T3 money_effect: 资金效应 → 0-100（主力净流入 + 涨停数共振）。

    Phase 2c：原 stub=0，现接入 money_flow + limit_up_down 真实数据。
    主力净流入占比 + 涨停家数共振 = 资金驱动主线确立信号。

    映射（对齐 T3 confirm 门槛 money_effect>=50）：
      inflow>5% & 涨停>100 → 80  （强资金+广涨停，主线确立）
      >3% & >50            → 65  （中度资金+涨停，过 trigger 门槛）
      >2% & >30            → 50  （温和资金，过 confirm 门槛）
      >0                   → 25  （净流入但弱，未达门槛）
      else                 → 0   （净流出，无资金效应）

    Parameters
    ----------
    inflow_pct     : 全市场主力净流入占比序列（%，如 3.5 表示 3.5%）。
    limit_up_count : 每日涨停家数序列。

    Returns
    -------
    pd.Series，值 ∈ {0, 25, 50, 65, 80}。
    """
    score = pd.Series(0.0, index=inflow_pct.index)
    inflow = inflow_pct.fillna(0.0)
    lu = limit_up_count.reindex(inflow_pct.index).fillna(0.0)
    score[inflow > 0] = 25
    score[(inflow > 2) & (lu > 30)] = 50
    score[(inflow > 3) & (lu > 50)] = 65
    score[(inflow > 5) & (lu > 100)] = 80
    return score


def t3_mainline_score(sector_hhi: pd.Series, top_sector_pct: pd.Series) -> pd.Series:
    """T3 mainline: 主线效应 → 0-100（板块涨幅集中度 HHI + 头部板块涨幅）。

    Phase 2c：原 stub=0，现接入 kline_sector 真实数据。
    主线 = 板块涨幅集中（少数板块领涨）+ 头部板块涨幅显著。
    HHI = Σ(share_i²)，share_i = |ret_i| / Σ|ret_j|，越高越集中。

    映射（对齐 T3 trigger 门槛 mainline>=60）：
      HHI>0.15 & Top>3% → 80  （强集中+强领涨，主线明确）
      >0.10 & >2%       → 65  （中度集中，过 trigger 门槛）
      >0.08 & >1%       → 35  （弱集中，未达门槛）
      else              → 0   （散乱无主线）

    Parameters
    ----------
    sector_hhi     : 板块涨幅 HHI 序列（[0,1]）。
    top_sector_pct : 头部板块（涨幅最高）涨幅序列（%，如 3.5）。

    Returns
    -------
    pd.Series，值 ∈ {0, 35, 65, 80}。
    """
    score = pd.Series(0.0, index=sector_hhi.index)
    hhi = sector_hhi.fillna(0.0)
    top = top_sector_pct.reindex(sector_hhi.index).fillna(0.0)
    score[(hhi > 0.08) & (top > 1)] = 35
    score[(hhi > 0.10) & (top > 2)] = 65
    score[(hhi > 0.15) & (top > 3)] = 80
    return score


def t3_leader_score(max_consec_limit: pd.Series, promotion_rate: pd.Series) -> pd.Series:
    """T3 leader: 龙头效应 → 0-100（最高连板数 + 晋级率）。

    Phase 2c：原 stub=0，现接入 limit_up_down 真实数据。
    龙头 = 市场最高连板高度 + 昨日涨停今日继续涨停（晋级）比例。

    映射（对齐 T3 trigger 门槛 leader>=60）：
      连板≥5 & 晋级>0.5 → 80  （高连板+高晋级，强龙头）
      ≥3 & >0.3         → 65  （中连板+中晋级，过 trigger 门槛）
      ≥2                → 35  （低连板，未达门槛）
      else              → 0   （无连板，无龙头）

    Parameters
    ----------
    max_consec_limit : 全市场最高连板数序列（如 5=5连板）。
    promotion_rate   : 晋级率序列（[0,1]，昨日涨停今日继续涨停比例）。

    Returns
    -------
    pd.Series，值 ∈ {0, 35, 65, 80}。
    """
    score = pd.Series(0.0, index=max_consec_limit.index)
    ml = max_consec_limit.fillna(0.0)
    pr = promotion_rate.reindex(max_consec_limit.index).fillna(0.0)
    score[ml >= 2] = 35
    score[(ml >= 3) & (pr > 0.3)] = 65
    score[(ml >= 5) & (pr > 0.5)] = 80
    return score


def t3_one_day_mainline_flag(prev_top3_max_today_pct: pd.Series) -> pd.Series:
    """T3 one_day_mainline: 一日主线证伪标志（0/1）——T3 fail 条件。

    Phase 2c：原 stub=0，现接入 kline_sector 真实数据。
    昨日涨幅 Top3 板块今日全部下跌>2% = 主线一日游（伪主线），
    昨日的主升今日被证伪 → T3 fail 信号。

    判定：昨日 Top3 今日的最佳表现（max）仍 <-2% → 三者全跌>2% → flag=1。
    （max<门槛 ⟺ 全部<门槛，因 max 是三者中最不跌的。）

    Parameters
    ----------
    prev_top3_max_today_pct : 昨日 Top3 板块今日最佳涨幅序列（%，如 -2.5）。

    Returns
    -------
    pd.Series，值 ∈ {0.0, 1.0}。
    """
    flag = pd.Series(0.0, index=prev_top3_max_today_pct.index)
    flag[prev_top3_max_today_pct.fillna(0.0) < -2.0] = 1.0
    return flag


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


# ---------------------------------------------------------------------------
# S2 NLP: policy / bad_news_flat（P1-E3 MVP：关键词字典情感分析）
# ---------------------------------------------------------------------------


def s2_policy_score(
    policy_count: pd.Series,
    positive_count: pd.Series,
    negative_count: pd.Series,
) -> pd.Series:
    """S2 policy: 政策面信号 → 0-100。

    P1-E3 MVP：基于关键词字典的新闻情感聚合。
    用 3 日滚动平滑的正负面净差 × 政策新闻有无门控。

    映射（对齐 S2 confirm 门槛 policy>=40）：
      有政策新闻 + 净正面≥10 → 80  （强政策利好）
      有政策新闻 + 净正面≥5  → 60  （政策偏正面，过门槛）
      有政策新闻 + 净正面>0  → 40  （政策轻微正面）
      有政策新闻 + 净负面    → 20  （政策偏紧）
      无政策新闻             → 0   （无政策信号）

    Parameters
    ----------
    policy_count   : 每日政策类新闻计数。
    positive_count : 每日正面新闻计数。
    negative_count : 每日负面新闻计数。
    """
    idx = policy_count.index
    net = (positive_count - negative_count).rolling(3, min_periods=1).mean()
    has_policy = (policy_count > 0).rolling(3, min_periods=1).max().astype(float)
    score = pd.Series(0.0, index=idx)
    score[has_policy > 0] = 20  # 有政策新闻但净面未知
    score[(has_policy > 0) & (net > 0)] = 40
    score[(has_policy > 0) & (net >= 5)] = 60
    score[(has_policy > 0) & (net >= 10)] = 80
    return score.fillna(0.0)


def s2_bad_news_flat_score(
    negative_count: pd.Series,
    pct_change: pd.Series,
) -> pd.Series:
    """S2 bad_news_flat: 利空出尽 → 0-100。

    P1-E3 MVP：负面新闻密度高 + 市场企稳 = 利空出尽信号。
    5 日滚动平均负面新闻计数 → 密度评分；5 日累计收益 > -2% → 市场企稳门控。

    映射（对齐 S2 confirm 门槛 bad_news_flat>=40）：
      负面密度≥20 & 市场企稳 → 80  （利空密集+企稳，强出尽信号）
      负面密度≥10 & 市场企稳 → 60  （中度利空+企稳，过门槛）
      负面密度≥5  & 市场企稳 → 40  （轻度利空+企稳）
      市场未企稳              → 0   （利空未出尽）
      无负面新闻              → 0   （无利空可出尽）

    Parameters
    ----------
    negative_count : 每日负面新闻计数。
    pct_change     : 市场代理日收益率序列（用于判断市场是否企稳）。
    """
    idx = negative_count.index
    neg_density = negative_count.rolling(5, min_periods=2).mean().fillna(0.0)
    market_return_5d = pct_change.reindex(idx).fillna(0.0).rolling(5, min_periods=2).sum()
    market_stable = (market_return_5d >= -0.02).astype(float)
    density_score = pd.Series(0.0, index=idx)
    density_score[neg_density >= 5] = 40
    density_score[neg_density >= 10] = 60
    density_score[neg_density >= 20] = 80
    return (density_score * market_stable).fillna(0.0)
