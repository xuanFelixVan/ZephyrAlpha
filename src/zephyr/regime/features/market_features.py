# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §3 F1/F3/F4/F5
# [MODULE] zephyr.regime.features.market_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder消费F1 realized_vol_pct + F3 cross_asset_corr + F4 ad_ratio + F5 volume_anomaly)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] realized_vol_pct∈[0,1]; cross_asset_corr∈[-1,1]; ad_ratio∈[-1,1]; volume_anomaly为z-score; PIT严格(t及以前)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_market_features.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §3 #MOD-REGIME-002
"""市场级 regime 特征：实现波动率分位 / 跨资产相关性 / 涨跌家数比 / 量能异动（MOD-REGIME-002 §3 F1/F3/F4/F5）。

与 trend_features（F2a Hurst / F2b Kalman，单标的趋势）互补，本模块为**市场级**特征，
由 RegimeFeatureBuilder 在组合层面聚合计算，喂 HMM 9态观测矩阵 X 的 4 列。

  F1 realized_vol_pct  — 20日实现波动率的250日滚动分位（市场风险强度）
  F3 cross_asset_corr  — 沪深300/中证500/创业板指 两两相关系数均值（60日，恐慌时相关性飙升）
  F4 ad_ratio          — 全市场涨跌家数比的对数 tanh 归一化（市场广度， breadth）
  F5 volume_anomaly    — 成交量 z-score（20日，量能异动）

PIT 铁律（blueprint §6.1）：F1/F3/F5 用 t-1 及以前窗口；F4 用 t 日盘后快照。
所有函数返回 pandas.Series（index=日期），由 RegimeFeatureBuilder 对齐拼装。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["realized_vol_pct", "cross_asset_corr", "ad_ratio", "volume_anomaly"]


# ---------------------------------------------------------------------------
# F1: 实现波动率历史分位（realized volatility percentile）
# ---------------------------------------------------------------------------


def realized_vol_pct(
    close: pd.Series,
    hv_window: int = 20,
    pct_window: int = 250,
) -> pd.Series:
    """20日实现波动率（年化）在过去250日的滚动分位 ∈ [0, 1]。

    算法：
      1. 对数收益率 r = log(close / close.shift(1))
      2. 20日滚动标准差 × √252 → 年化实现波动率 HV
      3. HV 在过去 250 日的 rolling rank（pct=True）→ 分位

    高分位（>0.8）= 波动率处于历史高位 = 风险态；低分位 = 平静态。
    对应 RiskSignal #1（realized_vol 分位）的 raw 特征。

    Parameters
    ----------
    close : 收盘价序列（index=日期）。应为市场代理（如沪深300指数）。
    hv_window : 实现波动率窗口（默认20日）。
    pct_window : 分位回看窗口（默认250日≈1年）。

    Returns
    -------
    pd.Series，index 同 close，值 ∈ [0, 1]；前 (hv_window+pct_window) 日为 NaN。
    """
    returns = np.log(close / close.shift(1))
    hv = returns.rolling(hv_window).std() * np.sqrt(252)
    return hv.rolling(pct_window).rank(pct=True)


# ---------------------------------------------------------------------------
# F3: 跨资产相关性（cross-asset correlation）
# ---------------------------------------------------------------------------


def cross_asset_corr(
    returns_df: pd.DataFrame,
    window: int = 60,
) -> pd.Series:
    """多资产收益率两两相关系数均值（60日滚动）∈ [-1, 1]。

    算法：对 returns_df 每两列计算 rolling 相关系数，再对全部 pair 取均值。
    恐慌期跨资产相关性飙升（"在崩盘中一切相关系数趋于1"），是 CRISIS 信号。

    Parameters
    ----------
    returns_df : 收益率 DataFrame（index=日期，columns=资产，如 000300/000905/399006）。
    window : 滚动窗口（默认60日）。

    Returns
    -------
    pd.Series，index 同 returns_df，值 ∈ [-1, 1]；前 window 日为 NaN。
    """
    assets = list(returns_df.columns)
    if len(assets) < 2:
        # 单资产无法算相关性，返回 0（中性）
        return pd.Series(0.0, index=returns_df.index)

    pair_corrs: list[pd.Series] = []
    for i in range(len(assets)):
        for j in range(i + 1, len(assets)):
            c = returns_df[assets[i]].rolling(window).corr(returns_df[assets[j]])
            pair_corrs.append(c)
    return pd.concat(pair_corrs, axis=1).mean(axis=1)


# ---------------------------------------------------------------------------
# F4: 涨跌家数比（advance/decline ratio）
# ---------------------------------------------------------------------------


def ad_ratio(advance: pd.Series, decline: pd.Series) -> pd.Series:
    """全市场涨跌家数比的对数 tanh 归一化 ∈ [-1, 1]。

    算法：
      ratio = log((advance + 1) / (decline + 1))
      ad_ratio = tanh(ratio)   # 归一化到 [-1, 1]，压缩极端值

    +1 = 普涨（广度强），-1 = 普跌（广度崩塌），0 = 涨跌平衡。
    对应 RiskSignal #7（涨跌家数极端）与 S2 广度维度。

    Parameters
    ----------
    advance : 上涨家数序列（index=日期）。
    decline : 下跌家数序列（index=日期）。

    Returns
    -------
    pd.Series，index 同 advance，值 ∈ [-1, 1]；缺数据处为 0（中性）。
    """
    adv = advance.astype(float).fillna(0.0)
    dec = decline.astype(float).fillna(0.0)
    # log((adv+1)/(dec+1))，+1 防 log(0)/除零
    log_ratio = np.log((adv + 1.0) / (dec + 1.0))
    return np.tanh(log_ratio)


# ---------------------------------------------------------------------------
# F5: 量能异动（volume anomaly / z-score）
# ---------------------------------------------------------------------------


def volume_anomaly(volume: pd.Series, window: int = 20) -> pd.Series:
    """成交量 z-score（20日滚动标准化）。

    算法：z = (volume - rolling_mean) / rolling_std

    高 z（>2）= 放量异动（突破/恐慌抛售），低 z（<-2）= 缩量（流动性枯竭）。
    对应 RiskSignal #2（量能异动）与 S2 capitulation 量能极端维度。

    Parameters
    ----------
    volume : 成交量序列（index=日期）。应为市场代理（如沪深300指数成交量）。
    window : 滚动窗口（默认20日）。

    Returns
    -------
    pd.Series，index 同 volume；前 window 日为 NaN。std=0 时返回 0（避免除零）。
    """
    mean = volume.rolling(window).mean()
    std = volume.rolling(window).std()
    # std=0（成交量恒定）时返回 0，避免 inf/NaN
    z = (volume - mean) / std.replace(0.0, np.nan)
    return z.fillna(0.0)
