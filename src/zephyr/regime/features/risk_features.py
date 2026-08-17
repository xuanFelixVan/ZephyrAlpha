# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §5.3 RiskSignal 13参数
# [MODULE] zephyr.regime.features.risk_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] MOD-REGIME-002(RiskSignalConstructor消费13参数系数映射→risk_signal_inputs)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 所有coef∈[0.30,1.00]; 无异常=1.0(平时不干预); 系数只降不升(风险只减不增); PIT由调用方shift(1)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_risk_signal_builder.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_modifiable=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §5.3 #MOD-REGIME-002 #Phase2a
"""RiskSignal 13 参数纯函数（MOD-REGIME-002 Phase 2a）。

把原始特征（HMM 6 特征 + 新算 MA/KDJ/HHI）映射成 [0.30, 1.00] 系数，供
RiskSignalConstructor 组装 risk_signal_inputs 喂 RegimeDetector._compute_risk_signal。

设计原则（10_regime_detector_spec §5.3 + Phase 2 计划 §C1不退化保护）：
  - **无异常 = 1.0**：平时所有参数系数 1.0 → RiskBase=1.0 → Shrinkage 不变（C1 不退化前提）
  - **#1 保留 Phase 1 危机地板**：realized_vol_coef 复刻 _build_feature_risk 的 vol_pct+slope
    交集映射，保证 risk_base_phase2a ≤ risk_base_phase1（危机区只更严不更松）
  - **系数只降不升**：风险参数只把系数从 1.0 往下调，永远不会上调（风险只减不增不变量）
  - **保守阈值**：新参数仅在明确异常时触发，避免慢熊误杀致 Sharpe 退化
  - **PIT 由调用方负责**：本模块函数纯计算，shift(1) 在 RiskSignalConstructor._precompute 统一做

13 参数对照（10_regime_detector_spec §5.3.3）：
  #1  realized_vol       — vol_pct+slope 交集（危机地板，复刻 Phase 1）
  #2  volume_anomaly     — 放量暴跌/杀跌/滞涨（复用 F5）
  #3  price_pattern      — 空头排列/破前低（新算 MA5/20/60）
  #4  time_incubation    — stub=1.0（主观无数据）
  #5  space_position     — close vs 250日高点（新算）
  #6  cross_asset_corr   — 恐慌相关性飙升（复用 F3）
  #7  ad_ratio_extreme   — 普跌广度（复用 F4）
  #8  siphon             — 板块HHI+资金集中度（新算，数据缺失降级1.0）
  #9  tech_divergence    — KDJ顶背离（新算）
  #10 trend_slope_decay  — 斜率衰竭+Hurst衰退（复用 F2b/F2a）
  #11 news_ghost         — stub opportunity=0.0（无 NLP）
  #12 chip_structure     — stub=1.0（Phase 2c 接 chip engine）
  #13 bad_news_flat      — stub opportunity=0.0（无 NLP）
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "realized_vol_coef",
    "volume_anomaly_coef",
    "price_pattern_coef",
    "space_position_coef",
    "cross_asset_corr_coef",
    "ad_ratio_extreme_coef",
    "siphon_coef",
    "tech_divergence_coef",
    "trend_slope_decay_coef",
    "kdj",
    "detect_top_divergence",
]


# ---------------------------------------------------------------------------
# #1: 实现波动率分位 + 趋势斜率交集（危机地板，复刻 Phase 1 _build_feature_risk）
# ---------------------------------------------------------------------------


def realized_vol_coef(vol_pct: pd.Series, slope: pd.Series) -> pd.Series:
    """#1: vol_pct 分位 × slope 方向交集 → 系数（复刻 Phase 1 危机地板）。

    映射（与 RegimeFeatureBuilder._build_feature_risk 逐档对齐，保证 Phase 2a
    的 #1 ≡ Phase 1 的单参数 risk，使 risk_base_phase2a ≤ risk_base_phase1）：
      vol_pct>0.90 + 下跌(slope<0) → 0.30  （危机：极端高波+暴跌）
      vol_pct>0.90 + 未跌           → 0.60  （极端高波，赶顶/赶底）
      vol_pct>0.75 + 下跌           → 0.50  （高波+下跌，偏危机）
      vol_pct>0.75 + 未跌           → 0.80  （高波但未跌）
      else                          → 1.00  （正常，HMM 主导）

    slope<0 视为下跌趋势确认（kalman_slope 负=下行）。NaN 视为未跌（保守不误杀）。

    Parameters
    ----------
    vol_pct : realized_vol_pct 序列（[0,1]，复用 F1）。
    slope   : kalman_slope 序列（复用 F2b，负=下跌）。

    Returns
    -------
    pd.Series，index 同 vol_pct，值 ∈ {1.0, 0.80, 0.60, 0.50, 0.30}。
    """
    coef = pd.Series(1.0, index=vol_pct.index)
    down = slope.fillna(0.0) < 0.0  # NaN→0.0 视为未跌（保守）
    # 按 mild→severe 顺序赋值，severe 覆盖 mild（pandas 布尔赋值后写覆盖先写）
    coef[vol_pct > 0.75] = 0.80
    coef[(vol_pct > 0.75) & down] = 0.50
    coef[vol_pct > 0.90] = 0.60
    coef[(vol_pct > 0.90) & down] = 0.30
    return coef


# ---------------------------------------------------------------------------
# #2: 量能异动（放量暴跌/杀跌/滞涨）
# ---------------------------------------------------------------------------


def volume_anomaly_coef(vol_z: pd.Series, pct_change: pd.Series) -> pd.Series:
    """#2: 量能异动 × 涨跌幅 → 系数（复用 F5 volume_anomaly z-score）。

    映射（10_regime_detector_spec §5.3.3 维度2）：
      放量暴跌（z>2 & 跌>3%）   → 0.30  （恐慌抛售）
      放量杀跌（z>1.5 & 跌>1.5%）→ 0.60  （主动抛压）
      else                      → 1.00

    ⚠️ C1 验证 2026-08-06 修正：原"放量滞涨(z>1.5 & 涨<0.5%)→0.85"在 A 股约
    4.3% 日子触发（放量小涨是常态换手非危机），且多在 #1 未触发的非危机日，
    纯增 Sharpe 拖累不增 MaxDD 保护。移除滞涨维度，仅保留明确的放量下跌信号
    （暴跌/杀跌，罕见且与 #1 危机互补）。

    Parameters
    ----------
    vol_z      : volume_anomaly z-score 序列（复用 F5）。
    pct_change : 日涨跌幅序列（close.pct_change()）。

    Returns
    -------
    pd.Series，值 ∈ {1.0, 0.60, 0.30}。
    """
    coef = pd.Series(1.0, index=vol_z.index)
    pct = pct_change.fillna(0.0)
    z = vol_z.fillna(0.0)
    # 放量杀跌
    coef[(z > 1.5) & (pct < -0.015)] = 0.60
    # 放量暴跌
    coef[(z > 2.0) & (pct < -0.03)] = 0.30
    return coef


# ---------------------------------------------------------------------------
# #3: 价格形态（空头排列 / 破前低）
# ---------------------------------------------------------------------------


def price_pattern_coef(close: pd.Series) -> pd.Series:
    """#3: 破前低 → 系数（新算 rolling min）。

    ⚠️ C1 验证 2026-08-06 修正：原"空头排列(MA5<MA20<MA60)→0.85"在 A 股熊市
    约 28% 日子触发（空头排列是熊市常态非危机信号），致过度收缩。移除空头排列
    维度，仅保留"破前低"破位信号（罕见，与 #1 危机互补）。

    映射（收紧后）：
      破 250 日前低（close<rolling_250min.shift(1)）→ 0.60  （长期破位，危机）
      破 60 日前低（close<rolling_60min.shift(1)） → 0.90  （中期破位，轻度预警）
      else                                          → 1.00

    C1 验证 2026-08-06 二次调优：mild 0.85→0.90（min() 聚合下减少单次收缩幅度），
    severe 0.60 保留（破 250 日前低罕见且与 #1 危机互补，保留强保护）。

    Parameters
    ----------
    close : 收盘价序列（市场代理）。

    Returns
    -------
    pd.Series，值 ∈ {1.0, 0.90, 0.60}；前 250 日为 1.0（warmup）。
    """
    coef = pd.Series(1.0, index=close.index)
    prior_low_60 = close.rolling(60).min().shift(1)
    prior_low_250 = close.rolling(250).min().shift(1)
    breakdown_60 = close < prior_low_60
    breakdown_250 = close < prior_low_250
    coef[breakdown_60] = 0.90
    coef[breakdown_250] = 0.60
    return coef


# ---------------------------------------------------------------------------
# #5: 空间位置（close vs 250 日高点）
# ---------------------------------------------------------------------------


def space_position_coef(close: pd.Series, window: int = 250) -> pd.Series:
    """#5: 当前价相对 250 日高点位置 → 系数（新算）。

    pos = close / rolling_max(close, 250)，衡量距高点的回撤深度。

    ⚠️ C1 验证 2026-08-06 修正：原阈值 pos<0.5 在沪深300 从不触发（沪深300
    历史最大回撤约 40%，pos 最低 ~0.58）。放宽到 pos<0.4 才能在 2015 股灾深跌
    区触发，作为深跌套牢的补充信号。

    映射（放宽后）：
      pos<0.30（距高点-70%） → 0.60  （深跌套牢区，罕见极端）
      pos<0.40（距高点-60%） → 0.85  （深度回撤，2015 股灾级）
      else                   → 1.00

    Parameters
    ----------
    close  : 收盘价序列。
    window : 高点回看窗口（默认 250 日≈1年）。

    Returns
    -------
    pd.Series，值 ∈ {1.0, 0.85, 0.60}；前 window 日为 1.0。
    """
    coef = pd.Series(1.0, index=close.index)
    rolling_max = close.rolling(window).max()
    pos = close / rolling_max
    coef[pos < 0.40] = 0.85
    coef[pos < 0.30] = 0.60
    return coef


# ---------------------------------------------------------------------------
# #6: 跨资产相关性（恐慌时相关性飙升）
# ---------------------------------------------------------------------------


def cross_asset_corr_coef(corr: pd.Series) -> pd.Series:
    """#6: 跨资产相关性均值 → 系数（复用 F3 cross_asset_corr）。

    恐慌期"一切相关系数趋于1"，corr 飙升是 CRISIS 信号。

    ⚠️ A 股结构性高相关：沪深300/中证500/创业板指常态相关 0.70-0.90（同涨同跌
    是 A 股常态，非危机）。C1 验证 2026-08-06 修正：原阈值 >0.70→0.85 致 87%
    日子误触发，永久压仓致 Sharpe 崩塌（0.35→0.12）。只有相关性逼近 1（>0.93，
    真正恐慌收敛）才触发，与 #1 波动率危机信号互补。

    映射（收紧后）：
      corr>0.97 → 0.60  （极端收敛，系统性恐慌）
      corr>0.95 → 0.92  （相关性逼近 1，轻度预警）
      else      → 1.00

    C1 验证 2026-08-06 二次调优：mild 0.85→0.92（min() 聚合下减少单次收缩幅度），
    severe 0.60 保留（>0.97 真正恐慌收敛罕见，保留强保护）。

    Parameters
    ----------
    corr : cross_asset_corr 序列（[-1,1]，复用 F3）。

    Returns
    -------
    pd.Series，值 ∈ {1.0, 0.92, 0.60}。
    """
    coef = pd.Series(1.0, index=corr.index)
    c = corr.fillna(0.0)
    coef[c > 0.95] = 0.92
    coef[c > 0.97] = 0.60
    return coef


# ---------------------------------------------------------------------------
# #7: 涨跌家数极端（普跌广度）
# ---------------------------------------------------------------------------


def ad_ratio_extreme_coef(ad_ratio: pd.Series) -> pd.Series:
    """#7: 涨跌家数比 → 系数（复用 F4 ad_ratio ∈ [-1,1]）。

    普跌（ad_ratio 接近 -1）= 广度崩塌，CRISIS 信号。

    ⚠️ A 股普跌常见：ad_ratio<-0.6 在 A 股约 30% 交易日触发（常态偏弱非危机）。
    C1 验证 2026-08-06 收紧：只有极端普跌（<-0.88，近乎全市场下跌）才触发，
    与 #1 波动率危机互补，避免常态弱市误杀。

    C1 验证 2026-08-06 二次调优：#7 在 Phase 2a 触发率 12.7%（6.8% 在 0.60 严重
    档），是除 #1 外最大额外收缩源。min() 聚合下 #7 独自拉低 RiskBase 致 Sharpe
    从 Phase 1 的 0.2678 退化至 0.2464。采取两步软化：
      ① 阈值收紧：mild -0.88→-0.90，severe -0.95→-0.97（减少触发天数）
      ② 系数软化：mild 0.85→0.90，severe 0.60→0.75（减少单次收缩幅度）
    #1 的 0.30 危机地板仍主导真危机日，#7 只做"广度预警"而非"广度屠杀"。

    映射（二次调优后）：
      ad_ratio<-0.97 → 0.75  （全市场崩塌式普跌，罕见极端）
      ad_ratio<-0.90 → 0.90  （极端普跌，轻度预警）
      else           → 1.00

    Parameters
    ----------
    ad_ratio : ad_ratio 序列（[-1,1]，复用 F4）。

    Returns
    -------
    pd.Series，值 ∈ {1.0, 0.90, 0.75}。
    """
    coef = pd.Series(1.0, index=ad_ratio.index)
    a = ad_ratio.fillna(0.0)
    coef[a < -0.90] = 0.90
    coef[a < -0.97] = 0.75
    return coef


# ---------------------------------------------------------------------------
# #8: 虹吸态（板块 HHI + 资金集中度）
# ---------------------------------------------------------------------------


def siphon_coef(sector_hhi: pd.Series | None, fund_concentration: pd.Series | None) -> pd.Series:
    """#8: 虹吸态 → 系数（板块集中度 HHI + 资金集中度）。

    虹吸 = 资金极度集中少数板块/个股，其余失血阴跌（10_regime_detector_spec §5.3.3 维度8）。
    任一数据缺失 → 该维度不参与（系数 1.0），两者都极端取更严。

    映射（HHI 为板块涨幅平方和归一化，越高越集中；fund_concentration 为头部净流入占比）：
      HHI>0.15 或 fund>0.5 → 0.60  （强虹吸）
      HHI>0.10 或 fund>0.4 → 0.85  （中度虹吸）
      else                 → 1.00

    Parameters
    ----------
    sector_hhi          : 板块涨幅 HHI 序列（[0,1]，None=数据缺失降级）。
    fund_concentration  : 头部资金净流入占比序列（[0,1]，None=数据缺失降级）。

    Returns
    -------
    pd.Series，值 ∈ {1.0, 0.85, 0.60}；数据全缺时恒 1.0（index 取 sector_hhi 或 fund）。
    """
    # 取可用 index（优先 sector_hhi）
    ref = sector_hhi if sector_hhi is not None else fund_concentration
    if ref is None:
        return pd.Series(dtype=float)  # 调用方按 1.0 降级
    coef = pd.Series(1.0, index=ref.index)
    hhi = sector_hhi.fillna(0.0) if sector_hhi is not None else pd.Series(0.0, index=ref.index)
    fund = fund_concentration.fillna(0.0) if fund_concentration is not None else pd.Series(0.0, index=ref.index)
    strong = (hhi > 0.15) | (fund > 0.5)
    moderate = (hhi > 0.10) | (fund > 0.4)
    coef[moderate] = 0.85
    coef[strong] = 0.60
    return coef


# ---------------------------------------------------------------------------
# #9: 技术指标背离（KDJ 顶背离）
# ---------------------------------------------------------------------------


def kdj(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """计算 KDJ 指标（#9 顶背离检测用）。

    K = SMA(RSV, 3, 1)；D = SMA(K, 3, 1)；J = 3K - 2D。
    RSV = (close - rolling_min(low,n)) / (rolling_max(high,n) - rolling_min(low,n)) × 100。

    Parameters
    ----------
    high, low, close : OHLC 序列。
    n                : RSV 窗口（默认 9）。

    Returns
    -------
    (K, D, J) 三个 pd.Series。
    """
    low_min = low.rolling(n).min()
    high_max = high.rolling(n).max()
    rsv = (close - low_min) / (high_max - low_min + 1e-8) * 100
    k = rsv.ewm(alpha=1 / 3, adjust=False).mean()
    d = k.ewm(alpha=1 / 3, adjust=False).mean()
    j = 3 * k - 2 * d
    return k, d, j


def detect_top_divergence(close: pd.Series, indicator: pd.Series, window: int = 60) -> pd.Series:
    """检测顶背离：价格创 window 日新高但指标未新高。

    顶背离 = 赶顶衰竭信号（10_regime_detector_spec §5.3.3 维度9）。

    Parameters
    ----------
    close     : 收盘价序列。
    indicator : 指标序列（如 KDJ 的 J 值）。
    window    : 新高回看窗口（默认 60 日）。

    Returns
    -------
    pd.Series（bool/float），1.0=顶背离，0.0=无。前 window 日为 0。
    """
    close_high = close.rolling(window).max()
    ind_high = indicator.rolling(window).max()
    price_new_high = close >= close_high
    ind_new_high = indicator >= ind_high
    divergence = price_new_high & ~ind_new_high
    return divergence.astype(float).fillna(0.0)


def tech_divergence_coef(
    divergence: pd.Series,
    divergence_60min: pd.Series | None = None,
    divergence_30min: pd.Series | None = None,
) -> pd.Series:
    """#9: KDJ 顶背离 → 系数（多分时共振极端档）。

    映射（10_regime_detector_spec §4.11.4 多分时共振是 #9 极端档）：
      日线背离 + 60min&30min 同背离 → 0.60  （多分时共振，确定性翻倍）
      日线背离 + 任一分时共振       → 0.75  （双周期共振）
      日线背离（单分时）            → 0.92  （轻度预警，原值）
      else                          → 1.00

    C1 验证 2026-08-06 二次调优：单分时 0.85→0.92（min() 聚合下减少单次收缩幅度）。
    Phase 2c 新增多分时共振档（0.75/0.60），数据缺失时降级单分时 0.92（C1 不退化）。

    Parameters
    ----------
    divergence : 日线顶背离 0/1 序列（detect_top_divergence 返回）。
    divergence_60min : 60min 顶背离 0/1 序列（None=降级单分时）。
    divergence_30min : 30min 顶背离 0/1 序列（None=降级单分时）。

    Returns
    -------
    pd.Series，值 ∈ {1.0, 0.92, 0.75, 0.60}。
    """
    coef = pd.Series(1.0, index=divergence.index)
    coef[divergence > 0.5] = 0.92
    if divergence_60min is not None and divergence_30min is not None:
        # 对齐到日线 index（取当日最后值，ffill 填充非交易日）
        d60 = divergence_60min.reindex(divergence.index, method="ffill").fillna(0)
        d30 = divergence_30min.reindex(divergence.index, method="ffill").fillna(0)
        daily_div = divergence > 0.5
        both = daily_div & (d60 > 0.5) & (d30 > 0.5)
        any2 = daily_div & ((d60 > 0.5) | (d30 > 0.5))
        coef[any2] = 0.75
        coef[both] = 0.60
    return coef


# ---------------------------------------------------------------------------
# #10: 趋势斜率衰竭（Kalman 斜率 z-score + Hurst 衰退）
# ---------------------------------------------------------------------------


def trend_slope_decay_coef(slope: pd.Series, hurst: pd.Series | None = None, window: int = 250) -> pd.Series:
    """#10: 趋势斜率衰竭 → 系数（复用 F2b kalman_slope + F2a hurst）。

    斜率显著走弱 + Hurst<0.5（均值回复，趋势失效）= 趋势衰竭风险。
    映射：
      slope_z<-2 & hurst<0.5 → 0.60  （趋势衰竭+反转特征）
      slope_z<-2             → 0.92  （斜率显著走弱，轻度预警）
      else                   → 1.00

    C1 验证 2026-08-06 二次调优：mild 0.85→0.92（min() 聚合下减少单次收缩幅度），
    severe 0.60 保留（趋势衰竭+反转罕见且与 #1 危机互补，保留强保护）。

    slope_z = (slope - rolling_mean) / rolling_std（滚动标准化，跨 regime 可比）。

    Parameters
    ----------
    slope  : kalman_slope 序列（复用 F2b）。
    hurst  : hurst_dfa 序列（复用 F2a，None=不参与 Hurst 维度）。
    window : 斜率标准化回看窗口（默认 250 日）。

    Returns
    -------
    pd.Series，值 ∈ {1.0, 0.92, 0.60}；前 window 日为 1.0。
    """
    coef = pd.Series(1.0, index=slope.index)
    s = slope.fillna(0.0)
    mean = s.rolling(window).mean()
    std = s.rolling(window).std().replace(0.0, np.nan)
    slope_z = (s - mean) / std
    weak = slope_z < -2.0
    coef[weak] = 0.92
    if hurst is not None:
        h = hurst.fillna(0.5)
        coef[weak & (h < 0.5)] = 0.60
    return coef
