# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.metrics
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]zephyr.simulation.deflated_sharpe_calculator
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT铁律; Sharpe修正(中国10年期国债); 样本量<60不计算Sharpe; DSR退化态fail-closed(dsr_degenerate=True⇒dsr=0.0地板,不可读作"测得不显著")
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MetricsError
# [TESTS] tests/backtest/test_metrics.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
回测绩效指标计算模块

职责:
  - 计算回测绩效指标:总收益率/年化收益率/Sharpe/Sortino/最大回撤/胜率
  - Sharpe修正:使用中国10年期国债无风险利率(默认2.5%)
  - 样本量<60不计算Sharpe(统计不显著)
  - 支持IC/IR因子评估指标

约束:
  - PIT铁律:仅使用历史数据,禁止未来函数
  - 年化基准:252交易日

SSoT: docs/03_modules/_domain_backtest/blueprint.md §4.2
# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/metrics.yaml
# A4 --> O1
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.simulation.deflated_sharpe_calculator import (
    DSR_OVERFITTING_FLOOR,
    DSRConfig,
    DeflatedSharpeCalculator,
)

# 中国10年期国债无风险利率(年化),来源:D-SIMULATION-23
DEFAULT_RISK_FREE_RATE = 0.025
# 年化交易日数
TRADING_DAYS_PER_YEAR = 252
# Sharpe计算最小样本量(低于此值统计不显著)
MIN_SAMPLES_FOR_SHARPE = 60


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
              max_drawdown, win_rate(=日度正收益占比，非交易胜率——P1-3 口径澄清),
              trades_count

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

    # 胜率(正收益天数占比)——口径澄清（P1-3，2026-09-14 外部审查整改）：
    # 本字段 = 日度正收益率占比（day-level positive-return ratio），**非逐笔
    # 交易胜率**。BacktestResult.win_rate / 产物 metrics.win_rate 均沿此口径，
    # 与外部机构"胜率=盈利交易数/总交易数"惯例不同，消费侧勿直接对比。
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
# 注意: 此默认值(10)仅为fallback, 调用方MUST传入实际试错次数(策略数/参数组合数).
# 若实际试错次数>10而未显式传入, DSR会偏乐观(undercorrected).
# 对于参数搜索/网格优化的场景, n_trials应=参数组合总数.
# 车道 L 接线(2026-09-16): 未显式传入时不再直接吃这个默认 10，而是自动向可审计
# 真源 TrialLedger(MOD-BT-200) 取全局累计机器回测数；仅当账本不可读时才退回此默认并留
# n_trials_source="fallback_default:..."（禁硬编码拍脑袋基数）。
DEFAULT_N_TRIALS = 10


def _resolve_n_trials(n_trials: int | None) -> tuple[int, str]:
    """解析 DSR 多重检验基数 n_trials（真值优先，来源可溯，fail-closed 不猜）。

    优先级：
      1. 调用方显式传入整数 -> (n, "explicit")
      2. 缺省(None) -> 读可审计真源 TrialLedger.cumulative_trials() -> (n, "trial_ledger:<n>")
      3. 账本不可读 -> 退回 DEFAULT_N_TRIALS + 留痕 (DEFAULT_N_TRIALS, "fallback_default:<err>")

    懒导入 TrialLedger 避免 import 环（账本仅依赖 file_utils/paths）。
    """
    if n_trials is not None:
        return int(n_trials), "explicit"
    try:
        from zephyr.backtest.core.n_trial_ledger import TrialLedger

        n = int(TrialLedger().cumulative_trials())
        if n < 1:
            raise ValueError(f"账本读数非法(<1): {n}")
        return n, f"trial_ledger:{n}"
    except Exception as exc:  # noqa: BLE001——账本缺失/非法=退回默认并留痕，绝不让纯数学路径崩
        return DEFAULT_N_TRIALS, f"fallback_default:{type(exc).__name__}"


def calculate_full_metrics(
    nav_series: pd.Series,
    trades_count: int = 0,
    n_trials: int | None = None,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> dict:
    """计算完整绩效指标(基础指标 + Deflated Sharpe Ratio)

    在calculate_metrics基础上,额外计算:
      - Deflated Sharpe Ratio(DSR,多重测试偏差修正后的Sharpe概率)

    DSR 实现（2026-09-15 A4 裁定）:全量委托官方件 MOD-SIM-024
    ``zephyr.simulation.deflated_sharpe_calculator.DeflatedSharpeCalculator``
    （日频收益序列直入,量纲自洽）。原 ``calculate_dsr`` 坏路径已退役——
    该实现把年化 Sharpe 配日频样本数,σ_SR 系统性偏小、DSR 系统性偏向 1。

    Args:
        nav_series: 净值序列(按日期排序,首值为初始资金)
        trades_count: 总交易笔数
        n_trials: 试错次数(用于DSR多重测试修正)。None=自动向可审计真源 TrialLedger
            (MOD-BT-200,全局累计机器回测数)取真值；显式传整数=调用方指定基数。
            DEFAULT_N_TRIALS(=10) 仅在账本不可读时作 fallback 并留痕，禁裸吃默认。
        risk_free_rate: 年化无风险利率
        periods_per_year: 年化周期数(默认252交易日)

    Returns:
        dict: 基础指标(total_return/annual_return/sharpe_ratio/sortino_ratio/
              max_drawdown/win_rate/trades_count) +
              dsr/adjusted_sharpe/expected_max_sharpe/is_overfitting/dsr_degenerate
              (dsr∈[0,1]概率, dsr_degenerate=True 时为不可判定的 Fail-Closed 地板 0.0,
               须先读 dsr_degenerate 再信 dsr;
               adjusted_sharpe=年化Sharpe;
               expected_max_sharpe=E[max(Z_N)] 多重测试期望;
               is_overfitting=dsr<0.5 运气中值否决线,放行线0.95归 is_significant) +
              n_trials(实际用于修正的基数) + n_trials_source(来源可溯标记)
    """
    # 基础指标(复用现有calculate_metrics)
    base_metrics = calculate_metrics(
        nav_series,
        trades_count=trades_count,
        risk_free_rate=risk_free_rate,
        periods_per_year=periods_per_year,
    )

    # n_trials 真值解析（None→账本，来源留痕）——DSR 多重检验基数，来源可溯
    n_trials_resolved, n_trials_source = _resolve_n_trials(n_trials)

    # 收益率序列(日频,直接喂官方件——量纲自洽)
    nav = nav_series.dropna()
    returns = nav.pct_change().dropna()
    n_samples = len(returns)

    # 样本量不足,统计不显著(与MIN_SAMPLES_FOR_SHARPE口径一致;官方件<3会抛错,此处先行拦截)
    if n_samples < MIN_SAMPLES_FOR_SHARPE:
        result = dict(base_metrics)
        result["dsr"] = 0.0
        result["adjusted_sharpe"] = float(base_metrics["sharpe_ratio"])
        result["expected_max_sharpe"] = 0.0
        result["is_overfitting"] = True
        result["dsr_degenerate"] = True  # 样本不足=不可判定(SDC-4 fail-closed)
        result["n_trials"] = int(n_trials_resolved)
        result["n_trials_source"] = n_trials_source
        return result

    dsr_result = DeflatedSharpeCalculator(
        DSRConfig(periods_per_year=periods_per_year)
    ).calculate(
        [float(r) for r in returns],
        num_trials=int(n_trials_resolved),
        risk_free_rate=risk_free_rate / periods_per_year,
    )

    # 合并返回:基础指标 + DSR相关字段(键名向后兼容)
    result = dict(base_metrics)
    result["dsr"] = float(dsr_result.dsr)
    result["adjusted_sharpe"] = float(base_metrics["sharpe_ratio"])
    result["expected_max_sharpe"] = float(dsr_result.expected_max)
    # is_overfitting 语义=运气中值否决线(dsr < DSR_OVERFITTING_FLOOR=0.5);
    # 显著性放行线 0.95 归 MOD-SIM-024 is_significant。
    # 退化态(dsr_result.degenerate, dsr=DSR_UNDECIDABLE=0.0)在此同样落 True：
    # "判不了"必须阻断晋级，不得被读成"测得不显著"（SDC-4 Fail-Closed）。
    result["is_overfitting"] = bool(dsr_result.dsr < DSR_OVERFITTING_FLOOR)
    result["dsr_degenerate"] = bool(dsr_result.degenerate)
    result["n_trials"] = int(n_trials_resolved)
    result["n_trials_source"] = n_trials_source
    return result


__all__ = [
    "calculate_metrics",
    "calculate_ic_ir",
    "MetricsError",
    "DEFAULT_RISK_FREE_RATE",
    "TRADING_DAYS_PER_YEAR",
    "MIN_SAMPLES_FOR_SHARPE",
    "calculate_full_metrics",
    "DEFAULT_N_TRIALS",
]
