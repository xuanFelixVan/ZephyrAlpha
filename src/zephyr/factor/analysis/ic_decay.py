# [BLUEPRINT] MOD-L02-004 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-03
# [MODULE] zephyr.factor.analysis.ic_decay
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.evaluation.backtest; zephyr.factor.core.evaluation.metrics
# [CONSUMERS] zephyr.factor.analysis.decay_monitor
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——IC衰减仅使用已实现前向收益
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据不足->返回空Series; 半衰期无法计算->返回0.0
# [TESTS] tests/factor/test_ic_decay.py
# [TTL] permanent
"""D-FACTOR-ANA-03 IC 衰减分析——不同 lag 的 IC 衰减曲线与半衰期。

计算因子值在不同前向收益周期（lag）下的 IC，用于评估因子预测能力的衰减速度。
IC 半衰期 = IC 衰减到初始 IC 一半所需的 lag 数。

职责边界：
- 复用 backtest.load_history 加载数据
- 复用 metrics.compute_ic_series 计算各 lag 的 IC
- 计算半衰期（线性插值）
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from zephyr.factor.core.evaluation.backtest import (
    _compute_factor_panel,
    _compute_forward_returns,
    load_history,
)
from zephyr.factor.core.evaluation.metrics import compute_ic_series
from zephyr.factor.factor_base import FactorRegistry

log = logging.getLogger(__name__)


def compute_ic_decay(
    factor_id: str,
    symbols: list[str],
    start: str,
    end: str,
    max_lag: int = 20,
) -> pd.Series:
    """计算因子在不同前向收益 lag 下的 IC 衰减曲线。

    Args:
        factor_id: 已注册的因子 ID
        symbols: 评估标的池
        start: 回测起始日期
        end: 回测结束日期
        max_lag: 最大前向收益周期，默认 20

    Returns:
        pd.Series，index=lag(1..max_lag)，values=该 lag 下的 IC 均值。
        数据不足返回空 Series。
    """
    factor_cls = FactorRegistry.get(factor_id)
    history = load_history(symbols, start, end)
    if history.empty:
        log.warning("ic_decay: 历史数据为空 factor=%s", factor_id)
        return pd.Series(dtype=float)

    factor_panel = _compute_factor_panel(factor_cls, history)
    close_panel = history["close"].unstack(level="symbol")

    ic_values: dict[int, float] = {}
    for lag in range(1, max_lag + 1):
        return_panel = _compute_forward_returns(close_panel, lag).dropna(how="all")
        if return_panel.empty:
            continue
        ic_series = compute_ic_series(factor_panel, return_panel, lag)
        if not ic_series.empty:
            ic_values[lag] = float(ic_series.mean())
    return pd.Series(ic_values, name="ic_decay")


def compute_half_life(ic_decay_series: pd.Series) -> float:
    """计算 IC 半衰期——IC 衰减到初始值一半所需的 lag 数。

    用线性插值找到 IC 降到 initial_ic/2 的 lag。

    Args:
        ic_decay_series: compute_ic_decay 返回的 Series

    Returns:
        半衰期（lag 数）。无法计算返回 0.0。
    """
    if ic_decay_series.empty:
        return 0.0
    initial_ic = abs(float(ic_decay_series.iloc[0]))
    if initial_ic < 1e-10:
        return 0.0
    half_ic = initial_ic / 2.0
    lags = ic_decay_series.index.to_numpy(dtype=float)
    ics = ic_decay_series.to_numpy(dtype=float)
    abs_ics = np.abs(ics)
    # 找到第一个 abs(ic) <= half_ic 的点
    below = np.where(abs_ics <= half_ic)[0]
    if len(below) == 0:
        # IC 未衰减到一半，返回最大 lag
        return float(lags[-1])
    idx = below[0]
    if idx == 0:
        return float(lags[0])
    # 线性插值
    prev_ic = abs_ics[idx - 1]
    curr_ic = abs_ics[idx]
    prev_lag = lags[idx - 1]
    curr_lag = lags[idx]
    if prev_ic == curr_ic:
        return float(curr_lag)
    ratio = (prev_ic - half_ic) / (prev_ic - curr_ic)
    return float(prev_lag + ratio * (curr_lag - prev_lag))
