# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-03
# [MODULE] zephyr.factor.core.evaluation.metrics
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS] zephyr.factor.core.evaluation.backtest
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——IC计算仅使用同期因子值与已实现前向收益，禁止未来函数
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据不足->返回0.0; 空输入->返回0.0; 不抛异常
# [TESTS] tests/factor/test_evaluation_metrics.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-FACTOR-03 因子评估指标——纯函数模块（无 IO 依赖）。

提供 IC/IR/OOS正率/过拟合检测的计算函数。
全部为纯函数，可独立用合成数据测试。

IC (Information Coefficient): 因子值与前向收益的 Spearman rank correlation
IR (Information Ratio): IC 均值 / IC 标准差
OOS 正率: 样本外 IC > 0 的比例
"""

from __future__ import annotations

import warnings

import pandas as pd

# 零保护阈值
_EPS = 1e-10


def compute_ic(factor_values: pd.Series, forward_returns: pd.Series) -> float:
    """计算单截面信息系数 IC（Spearman rank correlation）。

    Args:
        factor_values: 因子值，index 为 symbol
        forward_returns: 前向收益，index 为 symbol

    Returns:
        IC 值 [-1, 1]。数据不足或常数输入返回 0.0。
    """
    fv_clean = factor_values.dropna()
    fr_clean = forward_returns.dropna()
    common = fv_clean.index.intersection(fr_clean.index)
    if len(common) < 2:
        return 0.0
    # 常数输入时 scipy 抛 ConstantInputWarning 且返回 NaN —— 降级为 0.0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ic = fv_clean.loc[common].corr(fr_clean.loc[common], method="spearman")
    if pd.isna(ic):
        return 0.0
    return float(ic)


def compute_ic_series(
    factor_panel: pd.DataFrame,
    return_panel: pd.DataFrame,
    horizon: int = 5,
) -> pd.Series:
    """逐截面计算 IC 时间序列。

    Args:
        factor_panel: index=date, columns=symbol, values=因子值
        return_panel: index=date, columns=symbol, values=前向收益
        horizon: 前向收益周期（仅用于日志，实际对齐靠 index）

    Returns:
        IC 时间序列，index=date, name="ic"
    """
    common_dates = factor_panel.index.intersection(return_panel.index)
    ic_dict = {date: compute_ic(factor_panel.loc[date], return_panel.loc[date]) for date in common_dates}
    return pd.Series(ic_dict, name="ic")


def compute_ir(ic_series: pd.Series) -> float:
    """信息比率 = mean(IC) / std(IC)。

    Args:
        ic_series: IC 时间序列

    Returns:
        IR 值。数据不足或 std≈0 返回 0.0。
    """
    if ic_series.empty or len(ic_series) < 2:
        return 0.0
    std = ic_series.std(ddof=0)
    if std < _EPS:
        return 0.0
    return float(ic_series.mean() / std)


def compute_oos_positive_rate(ic_series: pd.Series, oos_ratio: float = 0.3) -> float:
    """OOS 正率：后 oos_ratio 比例截面中 IC > 0 的比例。

    Args:
        ic_series: IC 时间序列
        oos_ratio: 样本外比例（默认 0.3）

    Returns:
        OOS 正率 [0, 1]。空序列返回 0.0。
    """
    if ic_series.empty:
        return 0.0
    oos_count = max(1, int(len(ic_series) * oos_ratio))
    oos_ic = ic_series.iloc[-oos_count:]
    positive = int((oos_ic > 0).sum())
    return float(positive) / float(len(oos_ic))


def check_overfitting(is_ic: float, oos_ic: float, threshold: float = 0.5) -> bool:
    """过拟合检测：OOS_IC / IS_IC < threshold 则判定过拟合。

    Args:
        is_ic: 样本内 IC 均值
        oos_ic: 样本外 IC 均值
        threshold: 衰减阈值（默认 0.5——OOS 不到 IS 的 50% 判定过拟合）

    Returns:
        True = 过拟合, False = 正常
    """
    if abs(is_ic) < _EPS:
        return True
    ratio = oos_ic / is_ic if is_ic != 0 else 0.0
    return ratio < threshold
