# [BLUEPRINT] MOD-L02-007 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-06
# [MODULE] zephyr.factor.analysis.layered_backtest
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——分层仅使用同期因子值与已实现前向收益
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->空DataFrame; 数据不足->空结果
# [TESTS] tests/factor/test_layered_backtest.py
# [TTL] permanent
"""D-FACTOR-ANA-06 分层回测——按因子值分组计算各层收益与多空收益差。

将每个截面的标的按因子值分为 n_layers 组（默认5分位），计算各层的平均收益，
以及最高层减最低层的多空收益差（layer spread）。

策略参数从 _config.yaml 读取（n_layers 默认5）。
"""
from __future__ import annotations

import pandas as pd

from zephyr.factor.analysis import load_analysis_config


def _get_n_layers(default: int = 5) -> int:
    """从配置读取分层组数。"""
    cfg = load_analysis_config()
    return int(cfg.get("layered_backtest", {}).get("n_layers", default))


def layered_returns(
    factor_values: pd.Series,
    forward_returns: pd.Series,
    n_layers: int | None = None,
) -> pd.DataFrame:
    """按因子值分层计算各层平均前向收益。

    Args:
        factor_values: 因子值，index 为 symbol（单截面）
        forward_returns: 前向收益，index 为 symbol（单截面）
        n_layers: 分层数，None 时从配置读取（默认5）

    Returns:
        DataFrame，index=layer(0..n-1)，columns=[avg_return, count]。
        layer 0 = 因子值最低层，layer n-1 = 最高层。
    """
    if n_layers is None:
        n_layers = _get_n_layers()
    if factor_values.empty or forward_returns.empty:
        return pd.DataFrame()
    common = factor_values.dropna().index.intersection(forward_returns.dropna().index)
    if len(common) < n_layers:
        return pd.DataFrame()
    fv = factor_values.loc[common]
    fr = forward_returns.loc[common]
    # 按 factor value 排序后分组
    sorted_idx = fv.sort_values().index
    layers = pd.qcut(fv.rank(method="first"), n_layers, labels=False)
    grouped = fr.groupby(layers).agg(["mean", "count"])
    grouped.columns = ["avg_return", "count"]
    return grouped


def compute_layer_spread(
    factor_panel: pd.DataFrame,
    return_panel: pd.DataFrame,
    n_layers: int | None = None,
) -> pd.Series:
    """计算多空收益差时间序列（最高层 - 最低层）。

    Args:
        factor_panel: index=date, columns=symbol, values=因子值
        return_panel: index=date, columns=symbol, values=前向收益
        n_layers: 分层数，None 时从配置读取

    Returns:
        pd.Series，index=date, values=多空收益差。数据不足的截面跳过。
    """
    if n_layers is None:
        n_layers = _get_n_layers()
    common_dates = factor_panel.index.intersection(return_panel.index)
    spreads: dict = {}
    for date in common_dates:
        lr = layered_returns(
            factor_panel.loc[date], return_panel.loc[date], n_layers
        )
        if lr.empty or len(lr) < 2:
            continue
        spreads[date] = float(lr["avg_return"].iloc[-1] - lr["avg_return"].iloc[0])
    return pd.Series(spreads, name="layer_spread")
