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

32 个维度 key（对齐 TRANSITION_CONFIG 的 keys_gte/keys_or_gte）：
  可算 30 个：vix_panic/correlation/liquidity/flash_recover（S1）
              capitulation/vix/wyckoff/valuation/fund/spring/three_yang/breadth_thrust/
              break_sc_low/vix_new_high/fund_outflow（S2）
              bqs/rcs/frs（T1）, continue_decline（T2）
              volume_price/ma_trend/sentiment/money_effect/mainline/leader/one_day_mainline（T3）
              shrink_flat（T4）, leader_break/rebound_wrap（T5）, sudden_volume（T6）
  stub 2 个（=0）：bad_news_flat/policy（S2, NLP，待 NLP 管道）
  Phase 2c：money_effect/mainline/leader/one_day_mainline 从 stub 升级为可算（接 money_flow/kline_sector/limit_up_down）
  P1-E9（14_regime_s2_diagnosis §4）：capitulation 衰减加权多过滤器 / valuation 路B校准
    +路A基本面函数 / spring 深度分级 / breadth_thrust V 反转通路 / three_yang 6 维分级

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
    "s2_valuation_score_fundamental",
    "s2_fund_score",
    "s2_spring_flag",
    "s2_three_yang_flag",
    "s2_breadth_thrust_score",
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


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """ATR(14)——项目无现成实现，P1-E9a 自带（14_regime_s2_diagnosis §4.1）。

    True Range = max(high-low, |high-prev_close|, |low-prev_close|)，
    ATR = TR 的 Wilder 平滑（等价 EMA with alpha=1/window）。

    模块级私有（前缀 _）：仅 overlay_features 内 S2 维度用（capitulation 实体过滤器 +
    spring 0.5×ATR 失效边距，§4.3）；未来 T1/T5 需 ATR 再提升到 features/_indicators.py。
    """
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1.0 / window, adjust=False).mean()


def s2_capitulation_score(
    vol_z: pd.Series,
    pct_change: pd.Series,
    volume: pd.Series | None = None,
    high: pd.Series | None = None,
    low: pd.Series | None = None,
    open: pd.Series | None = None,
    close: pd.Series | None = None,
    put_call_ratio: pd.Series | None = None,
    new_low_ratio: pd.Series | None = None,
    lookback: int = 20,
    halflife: int = 10,
    atr_window: int = 14,
    vol_mult: float = 2.0,
    enable_options_filter: bool = False,
    base_mode: str = "zscore",
    wick_mode: str = "wick",
    vol_filter_mode: str = "mult",
    agg_mode: str = "wavg",
) -> pd.Series:
    """S2 capitulation: 近 N 日 capitulation 的衰减加权和（过程信号，防粘滞）。

    P1-E9a（14_regime_s2_diagnosis §4.1）：原瞬时两维信号（z>1∧pct<-1.5% 分档 50/70/90）
    升级为"单日多维度共振 + 衰减加权过程化"。Capitulation 是危机见底的【过程】信号，
    复苏事件日是企稳时点（当日不暴跌），故衡量"近期曾出现投降抛售"。

    三层升级：
      1. _capitulation_daily 多维度共振（量价基础分 + 量能>2.0×均量 + 实体>40%ATR
         + 下影线>50% 三过滤器；可选 put/call>1.4 + 新低占比>90% 第 5/6 维）。
      2. 衰减加权和替代 rolling max：rolling max 致单日高分持续 lookback 日→状态粘滞
         （S2 是一次性转换不应持续）。权重 e^(-i/τ)，τ=halflife/0.693。
         数值边界：halflife=10/lookback=20 时 w₀≈0.09，单日 90 分仅贡献 ~8 分，
         trigger≥60 需多日 capitulation 簇集（设计意图，禁止降阈值凑分）。
      3. ATR 自实现（_atr，项目无现成）。

    lookback/halflife 按 stage 分参数化（§4.1 注）：trigger（近 1 月）halflife=10/
    lookback=20（默认）；confirm（政策底→市场底滞后 1.5-3 月）halflife=30/lookback=40
    （占位，待 §4.5 walk-forward 校准）。

    参数化候选族（2026-08-28 S2 校准调查报告 §四预注册草案，Owner 裁定聚合=C1 主 +
    C3 对照；全部默认值 = legacy，现行为不变）：
      - base_mode: "zscore"(legacy) | "pct250"(A1 长期分位基准) | "precrisis_z"(A2 危机前基准 z)
      - wick_mode: "wick"(legacy) | "none"(B1 删 wick，语义归位 spring/flush 域)
        | "close_pos"(B2 光脚大阴线：收盘位置贴底 <0.15)
      - vol_filter_mode: "mult"(legacy 20 日均量×vol_mult) | "pct250"(>0.8)
        | "calm_window"(>平静窗均量×1.5)
      - agg_mode: "wavg"(legacy 归一化衰减加权) | "decayed_max"(C1 衰减峰值)
        | "cluster_count"(C3 近 20 日 daily≥70 簇计数映射 0/40/60/80)
    三层候选自由组合（A×B×C≤12 组，§4.4 walk-forward 选型，严禁降阈值凑分）。

    降级：volume/high/low/open/close 任一缺失 → 回退原瞬时两维版（治标 z>1，
    与 commit 93a25890 一致），保证无 OHLCV 的调用方不抛错（降级路径忽略模式参数）。
    """
    if any(s is None for s in (volume, high, low, open, close)):
        # 降级：原瞬时两维版（无 rolling/无过滤器）
        score = pd.Series(0.0, index=vol_z.index)
        z = vol_z.fillna(0.0)
        pct = pct_change.fillna(0.0)
        score[(z > 1) & (pct < -0.015)] = 50
        score[(z > 1) & (pct < -0.03)] = 70
        score[(z > 3) & (pct < -0.04)] = 90
        return score
    daily = _capitulation_daily(
        vol_z,
        pct_change,
        volume,
        high,
        low,
        open,
        close,
        atr_window,
        vol_mult,
        put_call_ratio,
        new_low_ratio,
        enable_options_filter,
        base_mode=base_mode,
        wick_mode=wick_mode,
        vol_filter_mode=vol_filter_mode,
    )
    # 衰减因子：rolling 窗口按时间正序传入（旧→新），权重须反序对齐——近期权重高、
    # 远期 e^(-i/τ) 衰减（τ=halflife/0.693）。14 memo 伪码 weights 未反序系笔误，
    # 此处按 §4.1 文字设计意图（防粘滞、信号自然消退）实现。
    decay = np.exp(-np.arange(lookback)[::-1] / (halflife / 0.693))
    if agg_mode == "wavg":
        # legacy：归一化衰减加权平均（w₀≈0.089，单日 90 仅贡献 ~8 分）
        weights = decay / decay.sum()
        return daily.rolling(lookback).apply(lambda w: (w * weights).sum(), raw=True)
    if agg_mode == "decayed_max":
        # C1 衰减峰值：score_t = max_{i∈窗口} daily_i×e^(-(t-i)/τ)（非归一化）。
        # 单日 90 → 当日 90 直接过 trigger 60；3 周后 90×e^(-15/14.4)≈31.9。
        return daily.rolling(lookback).apply(lambda w: (w * decay).max(), raw=True)
    if agg_mode == "cluster_count":
        # C3 簇计数映射：近 lookback 日 daily≥70 天数 n → 0/1/2/≥3 映射 0/40/60/80。
        # 对"簇早于事件日 3 周"天然稳健（计数只随窗口滑动衰减，无权重逐日衰减）；
        # min_periods=1：计数语义无需满窗（warmup 期按已观测日计数，无信号=0）。
        counts = (daily >= 70).astype(float).rolling(lookback, min_periods=1).sum()
        return pd.Series(
            np.select([counts >= 3, counts == 2, counts == 1], [80.0, 60.0, 40.0], default=0.0),
            index=daily.index,
        )
    raise ValueError(f"未知 agg_mode: {agg_mode!r}（可选 wavg/decayed_max/cluster_count）")


def _capitulation_daily(
    vol_z: pd.Series,
    pct_change: pd.Series,
    volume: pd.Series,
    high: pd.Series,
    low: pd.Series,
    open: pd.Series,
    close: pd.Series,
    atr_window: int = 14,
    vol_mult: float = 2.0,
    put_call_ratio: pd.Series | None = None,
    new_low_ratio: pd.Series | None = None,
    enable_options_filter: bool = False,
    base_mode: str = "zscore",
    wick_mode: str = "wick",
    vol_filter_mode: str = "mult",
) -> pd.Series:
    """单日 capitulation 评分（多维度共振，P1-E9a 原两维升级版）。

    量价基础分（base_mode 三候选，2026-08-28 调查报告 §4.1 预注册；刻度 50/70/90 不变）：
      - "zscore"（legacy）：z>3 & 跌>4% → 90 / z>1 & 跌>3% → 70 / z>1 & 跌>1.5% → 50
        （z 为调用方传入的 20 日滚窗 vol_z，危机簇内滚窗均量被抬高 → 结构性失真）
      - "pct250"（A1 长期分位基准）：量能证据改用 250 日滚动分位
        vol_pct250 = volume.rolling(250).rank(pct=True)（与 synthetic_vix_pct 同族口径，
        抗簇内失真），分档锚定跌幅主导（极端跌幅本身即投降证据，量能降级为佐证）：
        跌≥3% ∧ vol_pct250>0.6 → 50 / 跌≥5% ∧ vol_pct250>0.5 → 70 / 跌≥7% → 90
        （90 档无量能条件；warmup 期分位 NaN → 视为不满足）
      - "precrisis_z"（A2 危机前基准 z）：z 的均值/方差改用危机前平静窗
        volume.shift(20).rolling(40)（衡量"相对危机前的放量"，簇内高量不再抬基准），
        分档阈值同 legacy；内部从 volume 重算，忽略传入 vol_z
    三道过滤器（仅共振时保留基础分，否则归零；wick/vol 两维可切换候选口径）：
      - 量能放大（vol_filter_mode）："mult"（legacy）当日量 > vol_mult×20 日均量
        （v0.4.0 校准 1.3→2.0，研究下限）| "pct250"（B3，vol_pct250>0.8，与 A1 联动）
        | "calm_window"（B3，> 平静窗 shift(20).rolling(40) 均量×1.5，与 A2 联动）
      - 实体力度（不变，实证唯一健康维度）：|close-open| > 40% ATR(14)（真实体）
      - 下影线/收盘位置（wick_mode）："wick"（legacy）下影线占比>0.5（卖盘被吸收信号，
        实证与 A 股暴跌"光脚大阴线"形态根本冲突）| "none"（B1 删 wick，见底确认语义
        移交 spring/flush 域）| "close_pos"（B2 本土形态：(close-low)/(high-low)<0.15
        收盘贴底 = 恐慌尾盘无人承接的实体宣泄）
    可选第 5/6 维（enable_options_filter=True 且数据就绪时，默认关——三过滤器已
    selective 足够，六维交集过严致永不触发）：
      - put/call ratio > 1.4（期权市场恐慌对冲需求）
      - 创新低占比 > 0.90（indiscriminate selling）
    """
    pct = pct_change.fillna(0.0)
    base = pd.Series(0.0, index=vol_z.index)
    # 250 日滚动分位在 base/vol_filter 两处可能用到，惰性按需计算
    vol_pct250: pd.Series | None = None

    def _vol_pct250() -> pd.Series:
        nonlocal vol_pct250
        if vol_pct250 is None:
            vol_pct250 = volume.rolling(250).rank(pct=True)
        return vol_pct250

    # ── L1 基础分档 ──
    if base_mode == "zscore":
        z = vol_z.fillna(0.0)
        base[(z > 1) & (pct < -0.015)] = 50
        base[(z > 1) & (pct < -0.03)] = 70
        base[(z > 3) & (pct < -0.04)] = 90
    elif base_mode == "pct250":
        vp = _vol_pct250()
        base[(pct <= -0.03) & (vp > 0.6)] = 50
        base[(pct <= -0.05) & (vp > 0.5)] = 70
        base[pct <= -0.07] = 90
    elif base_mode == "precrisis_z":
        calm_mean = volume.shift(20).rolling(40).mean()
        calm_std = volume.shift(20).rolling(40).std()
        z = ((volume - calm_mean) / (calm_std + 1e-8)).fillna(0.0)
        base[(z > 1) & (pct < -0.015)] = 50
        base[(z > 1) & (pct < -0.03)] = 70
        base[(z > 3) & (pct < -0.04)] = 90
    else:
        raise ValueError(f"未知 base_mode: {base_mode!r}（可选 zscore/pct250/precrisis_z）")

    # ── L2 过滤器：量能（口径候选）+ 实体（不变）+ 下影/收盘位置（形态候选）──
    if vol_filter_mode == "mult":
        vol_surge = volume > volume.rolling(20).mean() * vol_mult
    elif vol_filter_mode == "pct250":
        vol_surge = _vol_pct250() > 0.8
    elif vol_filter_mode == "calm_window":
        vol_surge = volume > volume.shift(20).rolling(40).mean() * 1.5
    else:
        raise ValueError(f"未知 vol_filter_mode: {vol_filter_mode!r}（可选 mult/pct250/calm_window）")
    atr = _atr(high, low, close, atr_window)
    body = (close - open).abs()  # 真实体
    big_body = body > atr * 0.4
    if wick_mode == "wick":
        lower_wick = np.minimum(open, close) - low  # 下影线
        wick_ratio = lower_wick / (high - low + 1e-8)
        shape_ok = wick_ratio > 0.5
    elif wick_mode == "none":
        shape_ok = pd.Series(True, index=vol_z.index)
    elif wick_mode == "close_pos":
        close_pos = (close - low) / (high - low + 1e-8)  # 收盘在当日区间中的位置
        shape_ok = close_pos < 0.15
    else:
        raise ValueError(f"未知 wick_mode: {wick_mode!r}（可选 wick/none/close_pos）")
    mask = vol_surge & big_body & shape_ok
    # 可选第 5/6 维（JournalPlus 2026 四信号 confluence）
    if enable_options_filter:
        if put_call_ratio is not None:
            mask = mask & (put_call_ratio.fillna(0.0) > 1.4)
        if new_low_ratio is not None:
            mask = mask & (new_low_ratio.fillna(0.0) > 0.90)
    return base.where(mask, 0.0)


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
    """S2 valuation 路 B: 价格回撤代理估值 → 0-100（MVP 改良版）。

    P1-E9b（14_regime_s2_diagnosis §4.2 路 B）：pos = close / rolling_max(close, 250)。
    pos 越低 = 距高点越远 = 估值越有吸引力。

    阈值校准（P1-E9b 放宽，适配非腰斩级复苏）：原 <0.50 才给 40 过严
    （2020/2024 复苏 pos≈0.90 得 0），整体右移+提分：
      pos<0.50 → 80  （腰斩级仍高分）
      pos<0.60 → 60  （距高点-40%，深度折价）
      pos<0.70 → 40  （距高点-30% 即有估值吸引力，过 confirm 门槛）
      else     → 0   （接近高点，无估值吸引力）

    注：路 B 救不了"价格没跌但估值分位已低"（须路 A s2_valuation_score_fundamental
    接 CAPE/PB 分位；Step 0 ① 勘探 daily_valuation 无 CAPE 分位字段，管道待建）。
    """
    score = pd.Series(0.0, index=close.index)
    # min_periods=20：避免 warmup 期（数据起点 < window）rolling_max=NaN → pos=NaN → 误零。
    # 实测 000300 kline 数据起点晚于 data_load_start，2015 年 rolling(250) 不足 250 非 NaN → 全零。
    rolling_max = close.rolling(window, min_periods=20).max()
    pos = close / rolling_max
    score[pos < 0.70] = 40
    score[pos < 0.60] = 60
    score[pos < 0.50] = 80
    return score


def s2_valuation_score_fundamental(
    cape_percentile: pd.Series,
    pb_percentile: pd.Series | None = None,
    broken_net_ratio: pd.Series | None = None,
    erp_percentile: pd.Series | None = None,
    erp_absolute: pd.Series | None = None,
    buffett_ratio: pd.Series | None = None,
) -> pd.Series:
    """S2 valuation 路 A: 基本面估值评分 → 0-100（P1-E9b，对齐 §4.12.5）。

    关键（雪球 2026 席勒 PE 报告）：危机期 PE_TTM 因盈利 E 崩塌而"越跌越贵"失真
    （2008/2013 大底是盈利低谷）。S2 正是危机场景，故优先用 CAPE（5 年通胀调整
    平均盈利平滑周期，A 股专用——10 年 CAPE 混入股权分置改革前失真数据）或
    PB 分位，PE_TTM 分位仅辅助。

    评分映射（CAPE 分位为主，对齐 confirm 门槛 40）：
      CAPE 分位 <10% → 80（极度低估）/ <25% → 60（低估）/ <40% → 40（偏低）
    叠加加分（封顶 100）：
      PB 分位 <10% 或破净率 >10% → +10（pb_percentile 优先，缺省时用 broken_net_ratio）
      ERP：分位 >95% → +5；绝对值 >5% → +5、>6%（熊末）→ +10（ERP 项封顶 10，
        分位与绝对值双确认避免分位在长牛后失真）
      巴菲特指标（总市值/GDP，A 股本土化阈值下调）<70% → +5

    数据字段映射（待 daily_valuation CAPE 管道建成后由调用方注入）：
      cape_percentile ← cape_5y_percentile / pb_percentile ← pb_percentile /
      broken_net_ratio ← 全市场破净率 / erp_percentile|erp_absolute ← 风险溢价 /
      buffett_ratio ← 总市值/GDP。ERP/巴菲特字段缺失时降级运行（仅 CAPE+PB，少 15 分加分）。
    """
    score = pd.Series(0.0, index=cape_percentile.index)
    cp = cape_percentile.fillna(1.0)
    score[cp < 0.40] = 40
    score[cp < 0.25] = 60
    score[cp < 0.10] = 80
    if pb_percentile is not None:
        score = score + (pb_percentile < 0.10).astype(float) * 10
    elif broken_net_ratio is not None:
        score = score + (broken_net_ratio > 0.10).astype(float) * 10
    # ERP 分位 + 绝对值双确认
    if erp_percentile is not None:
        erp_bonus = (erp_percentile > 0.95).astype(float) * 5
    else:
        erp_bonus = pd.Series(0.0, index=cape_percentile.index)
    if erp_absolute is not None:
        ea = erp_absolute.fillna(0.0)
        erp_bonus = erp_bonus + (ea > 0.05).astype(float) * 5
        erp_bonus = erp_bonus.mask(ea > 0.06, 10.0)  # >6% 熊末直接满额
    score = score + erp_bonus.clip(upper=10.0)
    # 巴菲特指标 A 股本土化（<70% 深度低估）
    if buffett_ratio is not None:
        score = score + (buffett_ratio.fillna(1.0) < 0.70).astype(float) * 5
    return score.clip(upper=100.0)


def s2_fund_score(
    volume: pd.Series,
    window: int = 20,
    margin_balance: pd.Series | None = None,
    xl_order_inflow: pd.Series | None = None,
    pct_window: int = 250,
    w_margin: float = 0.4,
    w_xl: float = 0.35,
    w_volume: float = 0.25,
) -> pd.Series:
    """S2 fund: 资金承接 → 0-100。

    升级路径（14_regime_s2_diagnosis §4.0 fund 警告/§6 开放问题 10，跨 P1-E4）：
    注入 margin_balance（融资余额日频）或 xl_order_inflow（超大单净流入日频）时，
    评分 = "融资余额变化分位 + 超大单净流入分位 + 成交量分位"加权（缺源按可用源
    归一化）。依据（2026 研究）：成交量不区分方向（散户接盘式上涨持续性差）、无
    "出清"语义（融资余额低点=出清）；924 是"主力净流入+融资余额攀升+成交量跃升"
    三者共振，单看成交量无法复现。

      - 融资余额分量：margin_balance.diff(window)（近 window 日变化）的 pct_window
        日滚动分位——攀升=杠杆资金回流（分位高）；持续下降=出清中（分位低）
      - 超大单分量：xl_order_inflow.rolling(window).sum() 的滚动分位
      - 成交量分量：volume 的滚动分位（量级跃升语义，不再用方向不明的均量比）
      - composite 映射（对齐 confirm 门槛 fund>=50）：
        >0.80 → 70（三源共振强承接）/ >0.60 → 50（达门槛）/ >0.40 → 25 / else → 0

    两新源均 None 时回退原 MVP 代理（近 window 日均量 vs 前 window 日均量，
    分档 70/50/25/0），向后兼容（C1 不退化）。预热期分位全 NaN → 0（无信号）。
    """
    if margin_balance is None and xl_order_inflow is None:
        # 原 MVP 路径：成交量代理（不变）
        score = pd.Series(0.0, index=volume.index)
        recent_avg = volume.rolling(window).mean()
        prev_avg = volume.shift(window).rolling(window).mean()
        ratio = recent_avg / (prev_avg + 1e-8)
        score[ratio > 1.0] = 25
        score[ratio > 1.2] = 50
        score[ratio > 1.5] = 70
        return score

    min_p = min(pct_window, 60)
    comps: list[pd.Series] = []
    weights: list[float] = []
    # 成交量分位（量级跃升语义）
    comps.append(volume.rolling(pct_window, min_periods=min_p).rank(pct=True))
    weights.append(w_volume)
    if margin_balance is not None:
        # 融资余额近 window 日变化的分位（攀升=回流，下降=出清中）
        margin_chg = margin_balance.diff(window)
        comps.append(margin_chg.rolling(pct_window, min_periods=min_p).rank(pct=True))
        weights.append(w_margin)
    if xl_order_inflow is not None:
        # 超大单近 window 日累计净流入的分位
        xl_sum = xl_order_inflow.rolling(window).sum()
        comps.append(xl_sum.rolling(pct_window, min_periods=min_p).rank(pct=True))
        weights.append(w_xl)

    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    mat = pd.concat(comps, axis=1)
    # 按行加权（NaN 源剔除并归一化；全 NaN 预热期 → NaN → 落 0 档）
    with np.errstate(divide="ignore", invalid="ignore"):
        denom = mat.notna().to_numpy(dtype=float) @ w
        numer = mat.fillna(0.0).to_numpy(dtype=float) @ w
    composite = pd.Series(
        np.where(denom > 0, numer / np.where(denom > 0, denom, 1.0), np.nan),
        index=volume.index,
    )
    score = pd.Series(0.0, index=volume.index)
    c = composite.fillna(0.0)
    score[c > 0.40] = 25
    score[c > 0.60] = 50
    score[c > 0.80] = 70
    return score


def s2_spring_flag(
    close: pd.Series,
    high: pd.Series | None = None,
    low: pd.Series | None = None,
    volume: pd.Series | None = None,
    window: int = 60,
    atr_window: int = 14,
    atr_mult: float = 0.5,
) -> pd.Series:
    """S2 spring: Wyckoff Spring 震仓分级标志 → 0/1/2/3（P1-E9c 升级）。

    P1-E9c（14_regime_s2_diagnosis §4.3）：wyckoff_engine 的 Spring 事件是二值
    （broke_sc∧recovered∧缩量），缺 velocity/穿透深度分级/0.5×ATR 失效边距/主尾巴
    四要素（Step 0 ② 勘探结论），按 §4.3 步骤 4 用 high/low 自算兜底版（跨日 close
    实现合法，FibAlgo 2026）。flag 标在【收回确认日】（信号可知时点，PIT 安全）。

    判定（investing.com 2026-02 4-step 见底公式量化）：
      1. 刺破：当日 low < rolling_min(low, window).shift(1)（前 window 日支撑）
      2. velocity：当日收回 close>支撑（v1 最强）/ 次日收回（v2）/ 第 3 日收回（v3
         边界）；>3 日未收回 → 不成立
      3. 失效边距：收回前任一收盘 < 刺破日 low − atr_mult×ATR(14) → Spring 失效
         （FibAlgo 2026 TR 支撑边距；atr_mult 敏感性见 §4.3 v0.4.3 警告）
    深度分级（TradingWyckoff 2026，穿透深度=(支撑−low)/支撑）：
      <1% → 1（minor，弱）/ 1-3% → 2（moderate，标准）/ >3% → 3（major，强制清算级）

    降级：high/low 缺失 → 回退原 close 跨日简化版（0/1，无分级），保证旧调用方不抛错。
    volume 参数预留（量能特征参与类型鉴别，当前兜底版不作硬条件，防交集过严）。
    """
    if high is None or low is None:
        # 降级：原 close 跨日简化版（前一日 close 跌破前低，当日 close 收回）
        legacy_window = 20
        flag = pd.Series(0.0, index=close.index)
        prior_low = close.rolling(legacy_window).min().shift(1)
        broke_prev = close.shift(1) < prior_low.shift(1)
        recovered = close > prior_low
        flag[broke_prev & recovered] = 1.0
        return flag
    support = low.rolling(window).min().shift(1)  # 前 window 日最低（不含当日）
    penetrate = (low < support).fillna(False)
    depth = ((support - low) / (support.abs() + 1e-12)).where(penetrate)
    atr = _atr(high, low, close, atr_window)
    # 失效线：刺破日 low − atr_mult×ATR（收回前收盘跌破此线 → Spring 失效）
    fail_level = (low - atr_mult * atr).where(penetrate)
    pen_support = support.where(penetrate)

    # velocity 分级收回判定（flag 标在收回确认日；中间日收盘须持续低于支撑，否则
    # 已按更快 velocity 确认过，避免同一刺破重复触发）
    rec1 = penetrate & (close > support)  # v1：当日收回
    pen1 = penetrate.shift(1, fill_value=False)
    ok1 = close.shift(1) >= fail_level.shift(1)  # 刺破日收盘未失效（NaN→False）
    still_below1 = close.shift(1) <= pen_support.shift(1)  # 刺破日未收回
    rec2 = pen1 & ok1 & still_below1 & (close > pen_support.shift(1))  # v2：次日收回
    pen2 = penetrate.shift(2, fill_value=False)
    ok2 = (close.shift(2) >= fail_level.shift(2)) & (close.shift(1) >= fail_level.shift(2))
    still_below2 = (close.shift(2) <= pen_support.shift(2)) & (close.shift(1) <= pen_support.shift(2))
    rec3 = pen2 & ok2 & still_below2 & (close > pen_support.shift(2))  # v3：第 3 日收回（边界）

    # 收回日的穿透深度（取对应刺破日 depth）
    event_depth = depth.where(rec1).combine_first(depth.shift(1).where(rec2))
    event_depth = event_depth.combine_first(depth.shift(2).where(rec3))

    flag = pd.Series(0.0, index=close.index)
    has_event = event_depth.notna()
    flag[has_event & (event_depth < 0.01)] = 1.0  # minor
    flag[has_event & (event_depth >= 0.01) & (event_depth <= 0.03)] = 2.0  # moderate
    flag[has_event & (event_depth > 0.03)] = 3.0  # major
    return flag


def s2_three_yang_flag(
    open: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    window: int = 60,
    grading: str = "legacy",
    drawdown_threshold: float = -0.15,
) -> pd.Series:
    """S2 three_yang: 红三兵 6 维量化判定 → 0/1/2/3（P1-E9e 升级）。

    P1-E9e（14_regime_s2_diagnosis §4.4b）：原"连续 3 日上涨"过宽松（任何三根小红
    K 线即触发），无法区分"主力抢筹型红三兵"与"下跌中继三小阳假信号"。升级为
    2026 八源汇总的 6 维标准：
      1. 实体递增：3 阳线 + 第三根实体≥第二根 1.5× + 第二根>第一根
      2. 开盘位置：后根开盘在前根实体内 + 收盘逐日新高
      3. 上影线：上影 ≤ 实体 5%（光头最佳）
      4. 量能配合：温和递增（1.1×/1.1×）+ 第三根≥前两根均量 2×，禁止巨量
         （单根量 > 前 5 日均量 2× = 一日游风险）
      5. 位置：60 日跌幅 >30%（底部反转；高位三连阳=诱多，排除）
      6. 失效：三根总涨幅 >15% = 动能透支 → 排除

    返回分级：3=三个白武士（第三根实体≥第二根 2× + 近乎光头，加强版），
    2=标准红三兵，1=弱红三兵（缺量能确认），0=不满足。
    strong_confirm 门槛 three_yang≥2（标准红三兵及以上）。

    grading="v2_index"（2026-08-28 S2 校准调查报告 §六修复建议 3，指数适配版，
    legacy 默认保持现行为不变）：
      - weak(=1)     = 三连阳 ∧ 实体递增 ∧ 收盘逐日新高 ∧ drawdown<drawdown_threshold
                       ∧ not_overbought
      - standard(=2) = weak ∧ 量温和递增 1.1× ∧ ¬巨量
      - warrior(=3)  = standard ∧ 上影≤实体 5% ∧ 第三根实体≥第二根 2×
      差异点：
      ① d5 位置维度：drawdown<-30% → drawdown_threshold=-0.15（Owner 裁定单一口径；
         000300 危机级回撤实证仅 ~15%：2020 新冠底 -15%、2024 924 前 -15%；
         legacy 路径仍硬编码 -30%，drawdown_threshold 仅 v2_index 生效）；
      ② d4 删除"第三根量≥前两根均量 2×"维度——回源核对 14 号 §4.4b 原文：同文并存
         "温和递增 1.1×"与"第三根≥前两根均量 2×"+"禁止巨量>2×"，三者数学互斥
         （全历史满足率 0.4%），判定该条系"巨量排除"语义的误抄（逻辑上"禁巨量>2×"
         才是排除条件），v2 仅保留 温和递增 1.1× ∧ ¬巨量；
      ③ open_in_body 移出定级（2024-09-24 跳空高开 +4.3% 属合法底部反转，不应卡死）；
      ④ 上影≤5% 从 weak 前置条件降级为 warrior 分级条件（实证通过率 12.2% 偏严）。
    """
    if grading not in ("legacy", "v2_index"):
        raise ValueError(f"未知 grading: {grading!r}（可选 legacy/v2_index）")
    body = (close - open).abs()
    upper_wick = high - close
    wick_ratio = upper_wick / (body + 1e-8)

    # 维度 1: 连续 3 阳线 + 实体递增
    is_yang = close > open
    three_yang = is_yang & is_yang.shift(1) & is_yang.shift(2)
    body_inc = (body > body.shift(1) * 1.5) & (body.shift(1) > body.shift(2))
    # 维度 2: 后根开盘在前根实体内
    open_in_body = (open > open.shift(1)) & (open < close.shift(1))
    close_new_high = (close > close.shift(1)) & (close.shift(1) > close.shift(2))
    # 维度 3: 上影 ≤ 实体 5%
    small_wick = wick_ratio < 0.05
    # 维度 4: 量能温和递增 + 第三根 ≥ 前两根均量 2× + 禁止巨量
    vol_inc = (volume > volume.shift(1) * 1.1) & (volume.shift(1) > volume.shift(2) * 1.1)
    vol_surge = volume > (volume.shift(1) + volume.shift(2)) / 2 * 2.0
    not_giant = volume < volume.rolling(5).mean() * 2.0
    # 维度 5: 位置（底部反转：60 日跌幅 >30%；v2_index 指数适配 -15%）
    rolling_max = close.rolling(window).max()
    drawdown = close / rolling_max - 1.0
    at_bottom = drawdown < (-0.30 if grading == "legacy" else drawdown_threshold)
    # 维度 6: 失效（三根总涨幅 >15% = 动能透支）
    total_gain = close / close.shift(2) - 1.0
    not_overbought = total_gain < 0.15

    # 分级
    score = pd.Series(0.0, index=close.index)
    if grading == "legacy":
        base_mask = three_yang & body_inc & open_in_body & close_new_high & at_bottom
        weak = base_mask & small_wick & not_overbought  # 缺量能确认
        standard = weak & vol_inc & vol_surge & not_giant
        # 三个白武士：第三根实体显著放大（≥第二根 2×）+ 近乎光头（上影≈0）
        warrior = standard & (body > body.shift(1) * 2.0) & (wick_ratio < 0.01)
    else:
        # v2_index：核心维合取定级 + 辅助维分级（开盘位置/上影不再卡 weak）
        weak = three_yang & body_inc & close_new_high & at_bottom & not_overbought
        standard = weak & vol_inc & not_giant  # vol_surge 维度已删（误抄，见 docstring ②）
        warrior = standard & (wick_ratio < 0.05) & (body > body.shift(1) * 2.0)

    score[weak.fillna(False)] = 1.0
    score[standard.fillna(False)] = 2.0
    score[warrior.fillna(False)] = 3.0
    return score


def s2_breadth_thrust_score(
    adv_issues: pd.Series,
    dec_issues: pd.Series,
    ema_window: int = 10,
) -> pd.Series:
    """S2 breadth_thrust: Zweig Breadth Thrust → 0-100（V 反转/政策型复苏确认）。

    P1-E9d（14_regime_s2_diagnosis §4.4）：confirm 析取通路——V 反转/政策型复苏不走
    Wyckoff 吸筹（wyckoff 合法偏低卡死 confirm），breadth thrust 在急速普涨中触发，
    正好补 wyckoff 盲区。

    定义（Zweig）：10 日 EMA(adv/(adv+dec)) 从 <0.40 升至 >0.615 在 10 交易日内。
    映射（对齐 confirm 析取门槛 breadth_thrust>=60）：
      完整 thrust（10 日窗口内曾 <0.40 且当前 >0.615） → 80
      10 日 EMA >0.615（已进入普涨区，不论起点）        → 60
      10 日 EMA >0.55（广度改善但未达 thrust）          → 30
      else                                              → 0

    完整 thrust 判定用 rolling(ema_window).min().shift(1) 取过去 ema_window 日内最低
    EMA（匹配"10 日内曾 washout"语义；ema.shift(ema_window) 只看恰好 −10 日会漏判
    washout 低点落在窗口中段的情形）。

    注：0.615/0.40 是美股 NYSE 标准，A 股本土化校准（0.58-0.65 区间扫描）属
    §4.5 验证闭环（Step 0 ③ 勘探得 399106 涨跌家数可用），预注册参数禁止施工调参。
    """
    total = adv_issues + dec_issues + 1e-8
    breadth_ratio = adv_issues / total
    ema = breadth_ratio.ewm(span=ema_window, adjust=False).mean()
    was_washout = ema.rolling(ema_window).min().shift(1) < 0.40
    now_thrust = ema > 0.615
    full_thrust = (was_washout & now_thrust).fillna(False)
    score = pd.Series(0.0, index=adv_issues.index)
    score[ema > 0.55] = 30
    score[ema > 0.615] = 60
    score[full_thrust] = 80
    return score


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
