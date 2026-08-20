# [BLUEPRINT] MOD-L02-010 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-09
# [MODULE] zephyr.factor.analysis.factor_attribution
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数——无IO依赖; 归因基于已计算IC序列或因子值
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->空结果; 缺失行业映射->只返回时间归因
# [TESTS] tests/factor/test_factor_attribution.py
# [A_module] module_id=MOD-L02-010 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-ANA-09 因子归因——按时间和行业维度分解因子表现。

时间归因：将 IC 时间序列按月（或其他频率）聚合，看各月 IC 表现。
行业归因：将因子值按行业分组，计算各行业的因子收益贡献。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: IC时间序列 pd.Series
#   fields: index=datetime，values=各期IC值
#   code: ic_series 函数参数
# - id: I2
#   name: 单截面因子值与前向收益 pd.Series
#   fields: factor_values / forward_returns，index=symbol
#   code: factor_values, forward_returns 函数参数
# - id: I3
#   name: 行业映射 dict[str, str]
#   fields: symbol → 行业名称，缺省归入「未知」
#   code: sector_map 函数参数
# - id: I4
#   name: 时间归因频率配置 str
#   fields: factor_attribution.time_freq，默认 ME（月末）
#   code: _config.yaml L15-16
# 层: 算法
# - id: A1
#   name_zh: ① 时间维度归因
#   name_en: attribute_by_time
#   intro: 把IC序列按配置频率重采样取均值，看每个周期表现
#   desc: index 转 datetime 后 s.resample(freq).mean()（L54-58）；空输入返回空Series
#   inputs: I1 I4
#   outputs: 周期IC均值 pd.Series
# - id: A2
#   name_zh: ② 行业维度归因
#   name_en: attribute_by_sector
#   intro: 因子值和收益按行业分组，算各行业平均因子/平均收益/样本数
#   desc: 取因子与收益交集 → sector_map 贴行业标签 → groupby(sector).agg(mean/mean/count)（L78-89）
#   inputs: I2 I3
#   outputs: 行业归因表 DataFrame
# 层: 输出
# - id: O1
#   name_zh: 时间归因结果 pd.Series
#   name_en: time attribution Series
#   intro: index=周期，values=该周期IC均值
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 行业归因表 DataFrame
#   name_en: sector attribution DataFrame
#   intro: index=行业，columns=[avg_factor, avg_return, count]
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I4 --> A1
# A1 --> O1
# I2 --> A2
# I3 --> A2
# A2 --> O2
"""

from __future__ import annotations

import pandas as pd

from zephyr.factor.analysis import load_analysis_config


def _get_time_freq(default: str = "ME") -> str:
    """从配置读取时间归因频率。

    pandas 2.x 弃用了 'M'/'Q'/'Y'，改用 'ME'/'QE'/'YE'（Month/Quarter/Year End）。
    """
    cfg = load_analysis_config()
    return str(cfg.get("factor_attribution", {}).get("time_freq", default))


def attribute_by_time(
    ic_series: pd.Series,
    freq: str | None = None,
) -> pd.Series:
    """按时间频率聚合 IC 序列（默认按月）。

    Args:
        ic_series: IC 时间序列，index 为 datetime
        freq: 聚合频率（如 "ME" 月, "QE" 季, "W" 周），None 时从配置读取

    Returns:
        pd.Series，index=周期, values=该周期 IC 均值
    """
    if freq is None:
        freq = _get_time_freq()
    if ic_series.empty:
        return pd.Series(dtype=float)
    # 确保 index 是 datetime
    idx = pd.to_datetime(ic_series.index)
    s = ic_series.copy()
    s.index = idx
    return s.resample(freq).mean()


def attribute_by_sector(
    factor_values: pd.Series,
    forward_returns: pd.Series,
    sector_map: dict[str, str],
) -> pd.DataFrame:
    """按行业分组归因因子收益。

    Args:
        factor_values: 因子值，index 为 symbol（单截面）
        forward_returns: 前向收益，index 为 symbol
        sector_map: symbol → 行业名称映射

    Returns:
        DataFrame，index=行业, columns=[avg_factor, avg_return, count]
    """
    if factor_values.empty or forward_returns.empty:
        return pd.DataFrame()
    common = factor_values.dropna().index.intersection(forward_returns.dropna().index)
    if len(common) == 0:
        return pd.DataFrame()
    fv = factor_values.loc[common]
    fr = forward_returns.loc[common]
    sectors = pd.Series([sector_map.get(s, "未知") for s in common], index=common)
    df = pd.DataFrame({"factor": fv, "return": fr, "sector": sectors})
    grouped = df.groupby("sector").agg(
        avg_factor=("factor", "mean"),
        avg_return=("return", "mean"),
        count=("factor", "count"),
    )
    return grouped
