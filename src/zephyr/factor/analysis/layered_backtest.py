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
# [A_module] module_id=MOD-L02-007 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-ANA-06 分层回测——按因子值分组计算各层收益与多空收益差。

将每个截面的标的按因子值分为 n_layers 组（默认5分位），计算各层的平均收益，
以及最高层减最低层的多空收益差（layer spread）。

策略参数从 _config.yaml 读取（n_layers 默认5）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 因子值截面 pd.Series
#   fields: index=symbol，values=单截面因子值（layered_returns 参数 factor_values）
#   code: layered_backtest.py L37
# - id: I2
#   name: 前向收益截面 pd.Series
#   fields: index=symbol，values=已实现前向收益（参数 forward_returns）
#   code: layered_backtest.py L38
# - id: I3
#   name: 因子/收益面板 pd.DataFrame
#   fields: index=date，columns=symbol（compute_layer_spread 参数 factor_panel/return_panel）
#   code: layered_backtest.py L70-71
# - id: I4
#   name: 分层数配置 int
#   fields: layered_backtest.n_layers=5（五分层）
#   code: analysis/_config.yaml L5-6
# 层: 算法
# - id: A1
#   name_zh: ① 单截面分层收益
#   name_en: layered_returns
#   intro: 按因子值大小把股票分成n组，算每组的平均前向收益
#   desc: 取因子与收益共有symbol → qcut(rank, n_layers) 分层 → groupby 求 mean/count（L56-66）
#   inputs: I1 I2 I4
#   outputs: DataFrame index=layer，columns=[avg_return, count]
#   invariant: INV-004 PIT铁律——仅用同期因子值与已实现前向收益；layer 0=因子值最低层
# - id: A2
#   name_zh: ② 多空收益差时间序列
#   name_en: compute_layer_spread
#   intro: 每个交易日截面做一次分层，最高层收益减最低层收益得到多空价差序列
#   desc: 逐 date 调 layered_returns → spread=avg_return.iloc[-1]-avg_return.iloc[0]（L86-95）
#   inputs: I3 I4 A1
#   outputs: pd.Series name=layer_spread，index=date
# 层: 输出
# - id: O1
#   name_zh: 分层收益表 DataFrame
#   name_en: layered returns table
#   intro: 各层平均收益与样本数，看因子值高的组是否真的赚得多
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 多空收益差 layer_spread pd.Series
#   name_en: layer spread series
#   intro: 最高层减最低层的收益差时间序列，衡量因子区分度
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I4 --> A1
# I3 --> A2
# I4 --> A2
# A1 --> A2
# A1 --> O1
# A2 --> O2
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
    # 按 factor value 排名分位分组
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
