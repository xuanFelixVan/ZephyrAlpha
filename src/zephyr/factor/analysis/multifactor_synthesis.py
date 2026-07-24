# [BLUEPRINT] MOD-L02-011 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-10
# [MODULE] zephyr.factor.analysis.multifactor_synthesis
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.ic_ir_calc
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——合成仅使用同期因子值; IC加权权重来自历史IC(不引入未来函数)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->空Series; 权重不匹配->等权兜底; 回归失败->等权兜底
# [TESTS] tests/factor/test_multifactor_synthesis.py
# [TTL] permanent
"""D-FACTOR-ANA-10 多因子合成——将多个因子值合成为综合信号。

提供三种合成方法：
1. 等权合成（synthesize_equal_weight）：所有因子等权平均，最简单的基线
2. IC加权合成（synthesize_ic_weighted）：按历史 IC 均值分配权重
3. 回归优化合成（synthesize_regression）：用历史前向收益回归求权重

统一入口 synthesize() 通过 method 参数选择。
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


def synthesize_equal_weight(
    factor_values: dict[str, pd.Series],
) -> pd.Series:
    """等权合成——所有因子值等权平均。

    Args:
        factor_values: factor_id → pd.Series（index 对齐）

    Returns:
        合成信号 pd.Series。空输入返回空 Series。
    """
    if not factor_values:
        return pd.Series(dtype=float)
    panel = pd.DataFrame(factor_values)
    return panel.mean(axis=1)


def synthesize_ic_weighted(
    factor_values: dict[str, pd.Series],
    ic_weights: dict[str, float],
) -> pd.Series:
    """IC 加权合成——按历史 IC 均值分配权重。

    Args:
        factor_values: factor_id → pd.Series
        ic_weights: factor_id → 权重（历史 IC 均值，会归一化）

    Returns:
        合成信号 pd.Series。权重不匹配时退化为等权。
    """
    if not factor_values:
        return pd.Series(dtype=float)
    # 过滤出有权重的因子
    weights = {k: float(v) for k, v in ic_weights.items() if k in factor_values and v != 0}
    if not weights:
        log.warning("ic_weighted: 无有效权重，退化为等权")
        return synthesize_equal_weight(factor_values)
    # 归一化权重（保证和为1）
    total = sum(abs(w) for w in weights.values())
    if total < 1e-10:
        return synthesize_equal_weight(factor_values)
    norm_weights = {k: w / total for k, w in weights.items()}
    panel = pd.DataFrame({k: factor_values[k] * norm_weights[k] for k in norm_weights})
    return panel.sum(axis=1)


def synthesize_regression(
    factor_values: dict[str, pd.Series],
    forward_returns: pd.Series,
) -> pd.Series:
    """回归优化合成——用历史前向收益对因子值做回归求权重。

    将多因子面板作为自变量，前向收益作为因变量，做 OLS 回归，
    用回归系数作为权重合成信号。

    Args:
        factor_values: factor_id → pd.Series
        forward_returns: 前向收益，index 与因子值对齐

    Returns:
        合成信号 pd.Series。回归失败时退化为等权。
    """
    if not factor_values:
        return pd.Series(dtype=float)
    panel = pd.DataFrame(factor_values)
    common = panel.index.intersection(forward_returns.dropna().index)
    if len(common) < len(panel.columns) + 1:
        log.warning("regression: 数据不足，退化为等权")
        return synthesize_equal_weight(factor_values)
    X = panel.loc[common].fillna(0).to_numpy()
    y = forward_returns.loc[common].to_numpy()
    try:
        # OLS: w = (X^T X)^-1 X^T y
        coeffs, *_ = np.linalg.lstsq(X, y, rcond=None)
    except np.linalg.LinAlgError:
        log.warning("regression: 矩阵求解失败，退化为等权")
        return synthesize_equal_weight(factor_values)
    return panel.fillna(0) @ coeffs


def synthesize(
    factor_values: dict[str, pd.Series],
    method: str = "ic_weighted",
    **kwargs,
) -> pd.Series:
    """多因子合成统一入口。

    Args:
        factor_values: factor_id → pd.Series
        method: 合成方法 "equal_weight" / "ic_weighted" / "regression"
        **kwargs: 方法特定参数（如 ic_weights, forward_returns）

    Returns:
        合成信号 pd.Series
    """
    if method == "equal_weight":
        return synthesize_equal_weight(factor_values)
    if method == "ic_weighted":
        ic_weights = kwargs.get("ic_weights", {})
        return synthesize_ic_weighted(factor_values, ic_weights)
    if method == "regression":
        forward_returns = kwargs.get("forward_returns")
        if forward_returns is None:
            log.warning("synthesize: regression 需要 forward_returns 参数，退化为等权")
            return synthesize_equal_weight(factor_values)
        return synthesize_regression(factor_values, forward_returns)
    log.warning("synthesize: 未知方法 '%s'，退化为等权", method)
    return synthesize_equal_weight(factor_values)
