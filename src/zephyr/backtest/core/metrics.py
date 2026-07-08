# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.metrics
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] PIT铁律; Sharpe修正(中国10年期国债); 样本量<60不计算Sharpe
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MetricsError
# [TESTS]
# [A_module] module_id=MOD-BT-001-metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
import math

import numpy as np
import pandas as pd

# 标准正态分布CDF(累积分布函数,Cumulative Distribution Function)
# 优先使用scipy.stats.norm.cdf;scipy不可用时用math.erf近似
try:
    from scipy.stats import norm

    def _norm_cdf(x):
        return float(norm.cdf(x))
except ImportError:
    def _norm_cdf(x):
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

# 中国10年期国债无风险利率(年化),来源:D-SIMULATION-23
DEFAULT_RISK_FREE_RATE = 0.025
# 年化交易日数
TRADING_DAYS_PER_YEAR = 252
# Sharpe计算最小样本量(低于此值统计不显著)
MIN_SAMPLES_FOR_SHARPE = 60
# Euler-Mascheroni constant(用于DSR多重测试偏差修正E[max SR]期望)
_EULER_MASCHERONI_GAMMA = 0.5772156649015329


class MetricsError(Exception):
    """绩效指标计算错误"""

    error_code = "ZA-BT-0006"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


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
    n = len(factor_values)
    # ic_std: 相关系数标准误, 由t统计量关系反推
    # t = ic*sqrt(n-2)/sqrt(1-ic^2) -> se(ic) = sqrt((1-ic^2)/(n-2))
    if n > 2 and abs(ic) < 1.0:
        ic_std = float(np.sqrt((1.0 - ic * ic) / (n - 2)))
    else:
        ic_std = 0.0
    if ic_std > 0:
        ic_ir = float(ic / ic_std * np.sqrt(periods_per_year))
    else:
        ic_ir = 0.0

    # t统计量(与ic_std一致: t = ic / ic_std)
    if ic_std > 0:
        t_stat = float(ic / ic_std)
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


# 默认试错次数(用于多重测试偏差修正,multiple testing bias)
# 来源:Bailey & López de Prado (2014)
DEFAULT_N_TRIALS = 10


def calculate_dsr(
    sharpe_ratio: float,
    n_trials: int = DEFAULT_N_TRIALS,
    n_samples: int = 0,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> dict:
    """计算Deflated Sharpe Ratio(修正夏普比率,多重测试偏差修正)

    基于Bailey & López de Prado (2014)公式,对原始Sharpe进行两层修正:
      1. 非正态分布修正(考虑偏度skewness与峰度kurtosis)
      2. 多重测试偏差修正(扣除N次试错中最高Sharpe的期望)

    Args:
        sharpe_ratio: 原始Sharpe比率(已年化)
        n_trials: 试错次数(用于多重测试偏差修正)
        n_samples: 样本量(收益率观测数)
        skewness: 收益率偏度(skewness,正态=0)
        kurtosis: 收益率峰度(kurtosis,Pearson定义,正态=3)
        risk_free_rate: 年化无风险利率(保留参数,与基础指标API一致;
            Sharpe已为超额收益,此参数当前不参与DSR计算)

    Returns:
        dict: dsr, adjusted_sharpe, expected_max_sharpe, is_overfitting

    Note:
        - DSR < 0.5 -> is_overfitting=True(来源:D-SIMULATION-24)
        - n_samples < 60 -> 样本不足,返回dsr=0.0, is_overfitting=True
    """
    # 样本量不足,统计不显著(与MIN_SAMPLES_FOR_SHARPE一致)
    if n_samples < MIN_SAMPLES_FOR_SHARPE:
        return {
            "dsr": 0.0,
            "adjusted_sharpe": float(sharpe_ratio),
            "expected_max_sharpe": 0.0,
            "is_overfitting": True,
        }

    sr = float(sharpe_ratio)
    skew = float(skewness)
    kurt = float(kurtosis)

    # 1) 非正态修正Sharpe(adjusted Sharpe Ratio, Bailey-LdP 2014)
    #    SR_adj = SR * (1 - skew*SR/6 + (kurt-3)*SR^2/24)
    adjustment = 1.0 - skew * sr / 6.0 + (kurt - 3.0) * sr * sr / 24.0
    adjusted_sharpe = sr * adjustment

    # 2) DSR方差项(考虑非正态与样本量, Mertens/Bailey-LdP)
    #    var_term = 1 - skew*SR_adj + (kurt-1)/4 * SR_adj^2
    #    sigma_sr = sqrt(var_term / (n_samples - 1))
    var_term = (
        1.0
        - skew * adjusted_sharpe
        + (kurt - 1.0) * adjusted_sharpe * adjusted_sharpe / 4.0
    )
    if n_samples > 1 and var_term > 0:
        sigma_sr = float(np.sqrt(var_term / (n_samples - 1)))
    else:
        sigma_sr = 0.0

    # 3) 多重测试偏差(multiple testing bias):N次独立试错中最高Sharpe的期望
    #    E[max SR] = sigma_sr * [(1-γ)*sqrt(2*ln(N)) + γ/sqrt(2*ln(N))]
    #    γ = Euler-Mascheroni constant ≈ 0.5772156649
    if n_trials > 1 and sigma_sr > 0:
        sqrt_2lnN = float(np.sqrt(2.0 * np.log(n_trials)))
        if sqrt_2lnN > 0:
            expected_max_sharpe = sigma_sr * (
                (1.0 - _EULER_MASCHERONI_GAMMA) * sqrt_2lnN
                + _EULER_MASCHERONI_GAMMA / sqrt_2lnN
            )
        else:
            expected_max_sharpe = 0.0
    else:
        expected_max_sharpe = 0.0

    # 4) DSR = Φ((SR_adj - E[max SR]) / sigma_sr),Φ为标准正态CDF
    if sigma_sr > 0:
        z = (adjusted_sharpe - expected_max_sharpe) / sigma_sr
        dsr = _norm_cdf(z)
    else:
        dsr = 0.0

    # DSR < 0.5 -> 存在过拟合(overfitting)(来源:D-SIMULATION-24)
    is_overfitting = bool(dsr < 0.5)

    return {
        "dsr": float(dsr),
        "adjusted_sharpe": float(adjusted_sharpe),
        "expected_max_sharpe": float(expected_max_sharpe),
        "is_overfitting": is_overfitting,
    }


def calculate_full_metrics(
    nav_series: pd.Series,
    trades_count: int = 0,
    n_trials: int = DEFAULT_N_TRIALS,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> dict:
    """计算完整绩效指标(基础指标 + Deflated Sharpe Ratio)

    在calculate_metrics基础上,额外计算:
      - 收益率偏度(skewness)与峰度(kurtosis)
      - Deflated Sharpe Ratio(DSR,多重测试偏差修正后的Sharpe)

    Args:
        nav_series: 净值序列(按日期排序,首值为初始资金)
        trades_count: 总交易笔数
        n_trials: 试错次数(用于DSR多重测试修正)
        risk_free_rate: 年化无风险利率
        periods_per_year: 年化周期数(默认252交易日)

    Returns:
        dict: 基础指标(total_return/annual_return/sharpe_ratio/sortino_ratio/
              max_drawdown/win_rate/trades_count) +
              dsr/adjusted_sharpe/expected_max_sharpe/is_overfitting
    """
    # 基础指标(复用现有calculate_metrics)
    base_metrics = calculate_metrics(
        nav_series,
        trades_count=trades_count,
        risk_free_rate=risk_free_rate,
        periods_per_year=periods_per_year,
    )

    # 收益率序列(用于高阶矩估计,higher-order moments)
    nav = nav_series.dropna()
    returns = nav.pct_change().dropna()
    n_samples = len(returns)

    # 偏度(skewness)与峰度(kurtosis)
    # 注意:pandas.Series.kurtosis()返回超额峰度(excess kurtosis,正态=0);
    # DSR公式中(kurtosis-3)使用Pearson峰度(正态=3),故需+3还原
    if n_samples > 0:
        skewness = float(returns.skew())
        raw_kurtosis = float(returns.kurtosis()) + 3.0
    else:
        skewness = 0.0
        raw_kurtosis = 3.0

    # 计算DSR(Deflated Sharpe Ratio)
    dsr_result = calculate_dsr(
        sharpe_ratio=base_metrics["sharpe_ratio"],
        n_trials=n_trials,
        n_samples=n_samples,
        skewness=skewness,
        kurtosis=raw_kurtosis,
        risk_free_rate=risk_free_rate,
    )

    # 合并返回:基础指标 + DSR相关字段
    result = dict(base_metrics)
    result["dsr"] = dsr_result["dsr"]
    result["adjusted_sharpe"] = dsr_result["adjusted_sharpe"]
    result["expected_max_sharpe"] = dsr_result["expected_max_sharpe"]
    result["is_overfitting"] = dsr_result["is_overfitting"]
    return result


__all__ = [
    "calculate_metrics",
    "calculate_ic_ir",
    "MetricsError",
    "DEFAULT_RISK_FREE_RATE",
    "TRADING_DAYS_PER_YEAR",
    "MIN_SAMPLES_FOR_SHARPE",
    "calculate_dsr",
    "calculate_full_metrics",
    "DEFAULT_N_TRIALS",
]
