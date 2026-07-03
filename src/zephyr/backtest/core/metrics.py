# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.metrics
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT铁律; Sharpe修正(中国10年期国债); 样本量<60不计算Sharpe
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MetricsError
# [TESTS]
# [A_module] module_id=MOD-BT-001-metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""回测绩效指标计算模块

职责:
  - 计算回测绩效指标:总收益率/年化收益率/Sharpe/Sortino/最大回撤/胜率
  - Sharpe修正:使用中国10年期国债无风险利率(默认2.5%)
  - 样本量<60不计算Sharpe(统计不显著)
  - 支持IC/IR因子评估指标

约束:
  - PIT铁律:仅使用历史数据,禁止未来函数
  - 年化基准:252交易日

SSoT: docs/03_modules/_domain_backtest/blueprint.md §4.2
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

# 中国10年期国债无风险利率(年化),来源:D-SIMULATION-23
DEFAULT_RISK_FREE_RATE = 0.025
# 年化交易日数
TRADING_DAYS_PER_YEAR = 252
# Sharpe计算最小样本量(低于此值统计不显著)
MIN_SAMPLES_FOR_SHARPE = 60


class MetricsError(Exception):
    """绩效指标计算错误"""


def calculate_metrics(
    nav_series: pd.Series,
    trades_count: int = 0,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> dict:
    """计算回测绩效指标

    Args:
        nav_series: 净值序列(按日期排序,首值为初始资金)
        trades_count: 总交易笔数
        risk_free_rate: 年化无风险利率(默认2.5%,中国10年期国债)
        periods_per_year: 年化周期数(默认252交易日)

    Returns:
        dict: total_return, annual_return, sharpe_ratio, sortino_ratio,
              max_drawdown, win_rate, trades_count

    Raises:
        MetricsError: nav_series为空或无效
    """
    if nav_series is None or len(nav_series) == 0:
        raise MetricsError("nav_series不能为空")

    nav = nav_series.dropna()
    if len(nav) < 2:
        raise MetricsError("nav_series有效数据不足(需>=2)")

    # 总收益率
    initial_nav = float(nav.iloc[0])
    final_nav = float(nav.iloc[-1])
    if initial_nav <= 0:
        raise MetricsError(f"初始净值必须>0, got {initial_nav}")
    total_return = (final_nav - initial_nav) / initial_nav

    # 日收益率
    returns = nav.pct_change().dropna()
    n_samples = len(returns)

    # 年化收益率
    n_periods = len(nav)
    if n_periods > 1:
        annual_return = (1 + total_return) ** (periods_per_year / n_periods) - 1
    else:
        annual_return = 0.0

    # Sharpe比率(修正版:减去无风险利率)
    # 样本量<60不计算(统计不显著)
    if n_samples < MIN_SAMPLES_FOR_SHARPE:
        sharpe_ratio = 0.0
        sortino_ratio = 0.0
    else:
        rf_per_period = risk_free_rate / periods_per_year
        excess_returns = returns - rf_per_period
        std_returns = float(returns.std())
        if std_returns > 0:
            sharpe_ratio = float(excess_returns.mean() / std_returns * np.sqrt(periods_per_year))
        else:
            sharpe_ratio = 0.0

        # Sortino比率(仅用下行波动率)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            downside_std = float(downside_returns.std())
            if downside_std > 0:
                sortino_ratio = float(excess_returns.mean() / downside_std * np.sqrt(periods_per_year))
            else:
                sortino_ratio = 0.0
        else:
            sortino_ratio = 0.0

    # 最大回撤
    max_drawdown = _calculate_max_drawdown(nav)

    # 胜率(正收益天数占比)
    if n_samples > 0:
        win_rate = float((returns > 0).sum() / n_samples)
    else:
        win_rate = 0.0

    return {
        "total_return": float(total_return),
        "annual_return": float(annual_return),
        "sharpe_ratio": float(sharpe_ratio),
        "sortino_ratio": float(sortino_ratio),
        "max_drawdown": float(max_drawdown),
        "win_rate": float(win_rate),
        "trades_count": int(trades_count),
    }


def _calculate_max_drawdown(nav: pd.Series) -> float:
    """计算最大回撤

    MaxDD = max((peak - nav) / peak)
    返回正值(如0.15表示最大回撤15%)
    """
    peak = nav.expanding().max()
    drawdown = (nav - peak) / peak
    max_dd = float(drawdown.min())
    return abs(max_dd) if max_dd < 0 else 0.0


def calculate_ic_ir(
    factor_values: pd.Series,
    forward_returns: pd.Series,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> dict:
    """计算因子IC/IR(信息系数/信息比率)

    用于因子快速筛选(向量化回测场景)。

    Args:
        factor_values: 因子值序列(截面排序)
        forward_returns: 远期收益率序列(与factor_values对齐)
        periods_per_year: 年化周期数

    Returns:
        dict: ic_mean, ic_std, ic_ir, t_stat, ic_positive_ratio
    """
    if len(factor_values) != len(forward_returns):
        raise MetricsError(
            f"factor_values长度({len(factor_values)})与forward_returns长度({len(forward_returns)})不一致"
        )

    if len(factor_values) < 2:
        return {"ic_mean": 0.0, "ic_std": 0.0, "ic_ir": 0.0, "t_stat": 0.0, "ic_positive_ratio": 0.0}

    # Spearman秩相关(更稳健)
    ic = float(factor_values.corr(forward_returns, method="spearman"))
    ic_std = float(forward_returns.std())
    if ic_std > 0:
        ic_ir = float(ic / ic_std * np.sqrt(periods_per_year))
    else:
        ic_ir = 0.0

    # t统计量
    n = len(factor_values)
    if n > 2 and ic_std > 0:
        t_stat = float(ic * np.sqrt(n - 2) / np.sqrt(1 - ic**2 + 1e-10))
    else:
        t_stat = 0.0

    ic_positive_ratio = float((forward_returns > 0).sum() / n) if n > 0 else 0.0

    return {
        "ic_mean": ic,
        "ic_std": ic_std,
        "ic_ir": ic_ir,
        "t_stat": t_stat,
        "ic_positive_ratio": ic_positive_ratio,
    }


__all__ = [
    "calculate_metrics",
    "calculate_ic_ir",
    "MetricsError",
    "DEFAULT_RISK_FREE_RATE",
    "TRADING_DAYS_PER_YEAR",
    "MIN_SAMPLES_FOR_SHARPE",
]
