# [BLUEPRINT] MOD-SIM-024 | docs/03_modules/_domain_simulation/deflated_sharpe_calculator/blueprint.md
# [MODULE] zephyr.simulation.deflated_sharpe_calculator
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.simulation.sharpe_calculator_fixer; zephyr.simulation.result_analyzer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DSRResult/DSRConfig/DSRTrendPoint frozen不可变; DSR∈(0,1); 样本<3拒绝; num_trials<1拒绝; float计算非Decimal; 无第三方依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SimulationError(ZA-SIM-0024)
# [TESTS] tests/simulation/test_deflated_sharpe_calculator.py
# [A_module] module_id=MOD-SIM-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_SIMULATION — Deflated Sharpe Ratio Calculator (DSR 计算器)

多重测试偏差修正的 Sharpe 比率。基于 Bailey & López de Prado (2014) 论文,
修正回测中"试了 N 次取最好"导致的 Sharpe 虚高。

属 A 类基础设施(确定性数学计算), 纯基础层不涉及策略。

设计真源: depgraph MOD-SIM-024
蓝图: docs/03_modules/_domain_simulation/deflated_sharpe_calculator/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 收益率序列 returns
#   fields: 每期收益率 list[float]（非年化；空序列/样本<3拒绝）
#   code: calculate(returns) L241
# - id: I2
#   name: 试次数 num_trials
#   fields: 回测尝试的策略/参数组合数 N（≥1，默认1=无多重测试修正）
#   code: calculate(num_trials) L244
# - id: I3
#   name: DSR配置 DSRConfig
#   fields: 显著性阈值0.95 + 年化频率252 + 无风险利率rf
#   code: DSRConfig L46
# 层: 特征
# - id: F1
#   name_zh: 收益率偏度
#   name_en: gamma
#   intro: 收益率分布的不对称程度（Fisher-Pearson有偏估计）
#   formula: γ=m3/m2^1.5，mk=(1/n)Σ(xi-mean)^k；n<3返回0
#   code: deflated_sharpe_calculator.py L131
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 收益率超额峰度
#   name_en: kappa
#   intro: 收益率分布的厚尾程度（超额峰度）
#   formula: κ=m4/m2²-3；n<4返回0
#   code: deflated_sharpe_calculator.py L148
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: Sharpe估计量方差
#   name_en: var_sr
#   intro: 非正态修正下Sharpe比率估计量的方差
#   formula: V[SR]=(1-γ·SR+(κ-1)/4·SR²)/(T-1)；T≤1返回0
#   code: deflated_sharpe_calculator.py L188
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F4
#   name_zh: 多重测试期望最大值
#   name_en: expected_max
#   intro: 试N次取最好时Sharpe的期望虚高幅度（Euler-Maclaurin近似）
#   formula: E[max(Z_N)]≈√(2lnN)-(lnπ+lnlnN)/(2√(2lnN))；N≤1返回0
#   code: deflated_sharpe_calculator.py L164
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① DSR主计算
#   name_en: DeflatedSharpeCalculator.calculate
#   intro: 修正"试N次取最好"偏差后的Deflated Sharpe Ratio
#   desc: SR=(mean-rf)/std → SR年=SR×√252 → SR*=SR/√V[SR]-E[max(Z_N)] → DSR=Φ(SR*)（Φ用math.erf实现）；var_sr≤0时DSR退化为1.0或0.5
#   inputs: I1 I2 I3 F1 F2 F3 F4
#   outputs: DSRResult（sharpe/年化sharpe/dsr/偏度/峰度/var_sr/expected_max/is_significant）
#   invariant: DSR∈(0,1)；样本<3或N<1抛SimulationError(ZA-SIM-0024)
# - id: A2
#   name_zh: ② 滚动窗口DSR趋势追踪
#   name_en: DeflatedSharpeCalculator.track_trend
#   intro: 每个滚动窗口算一次DSR，形成DSR趋势序列
#   desc: 从window-1位置起逐位取前window期收益率调calculate，收集DSRTrendPoint(index,dsr,年化sharpe)
#   inputs: I1 I2 A1
#   outputs: DSRTrendPoint列表（长度=len-window+1）
# 层: 输出
# - id: O1
#   name_zh: DSR计算结果 DSRResult
#   name_en: DSRResult
#   intro: 含DSR值/显著性判断/全套中间统计量的不可变结果
#   invariant: frozen不可变；DSR∈(0,1)
#   downstream: zephyr.simulation.sharpe_calculator_fixer; zephyr.simulation.result_analyzer（[CONSUMERS]）
# - id: O2
#   name_zh: DSR趋势点序列
#   name_en: list[DSRTrendPoint]
#   intro: 滚动窗口DSR+年化Sharpe的时间序列，用于趋势追踪
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# I1 -.->|断点| F3
# I2 -.->|断点| F4
# I1 --> A1
# I2 --> A1
# I3 --> A1
# F1 --> A1
# F2 --> A1
# F3 --> A1
# F4 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> A2
# A1 --> O1
# A2 --> O2
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class SimulationError(ZephyrBaseError):
    """仿真计算异常——输入非法(空序列/样本不足/试次数非法)。"""

    error_code = "ZA-SIM-0024"


# #14 裁定（2026-08-20）：DSR 阈值常量唯一真源（SSoT）——分级语义对齐社区惯例：
# 显著性放行线 0.95（类比 p<0.05）；运气中值否决线 0.5（低于此=无超出运气的证据）。
# 消费方：本模块 DSRConfig 默认值 / backtest.core.metrics.calculate_dsr is_overfitting。
DSR_SIGNIFICANCE_THRESHOLD = 0.95
DSR_OVERFITTING_FLOOR = 0.5


@dataclass(frozen=True)
class DSRConfig:
    """DSR 配置——不可变。

    Attributes:
        significance_threshold: DSR 显著性阈值(默认 DSR_SIGNIFICANCE_THRESHOLD=0.95)
        periods_per_year: 年化频率(A股日度=252)
        risk_free_rate: 默认无风险利率(默认 0.0)
    """

    significance_threshold: float = DSR_SIGNIFICANCE_THRESHOLD
    periods_per_year: int = 252
    risk_free_rate: float = 0.0


@dataclass(frozen=True)
class DSRResult:
    """DSR 计算结果——不可变。

    Attributes:
        sharpe: 非年化 Sharpe 比率
        sharpe_annualized: 年化 Sharpe 比率
        dsr: Deflated Sharpe Ratio ∈ (0, 1)
        num_trials: 试次数 N
        num_obs: 样本数 T
        skewness: 收益率偏度 γ
        kurtosis: 收益率峰度 κ
        var_sr: Sharpe 估计量方差 V[SR]
        expected_max: 多重测试期望最大值 E[max(Z_N)]
        is_significant: DSR 是否达到显著性阈值
    """

    sharpe: float
    sharpe_annualized: float
    dsr: float
    num_trials: int
    num_obs: int
    skewness: float
    kurtosis: float
    var_sr: float
    expected_max: float
    is_significant: bool


@dataclass(frozen=True)
class DSRTrendPoint:
    """DSR 趋势追踪点——不可变。

    Attributes:
        index: 滚动窗口结束位置
        dsr: 该窗口的 DSR 值
        sharpe: 该窗口的年化 Sharpe
    """

    index: int
    dsr: float
    sharpe: float


def _normal_cdf(x: float) -> float:
    """标准正态分布 CDF Φ(x), 使用 math.erf 实现。

    Φ(x) = 0.5 * (1 + erf(x / sqrt(2)))
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _mean(values: list[float]) -> float:
    """算术均值。"""
    return sum(values) / len(values)


def _variance(values: list[float], ddof: int = 1) -> float:
    """样本方差(ddof=1 为无偏估计)。"""
    n = len(values)
    if n <= ddof:
        return 0.0
    m = _mean(values)
    return sum((v - m) ** 2 for v in values) / (n - ddof)


def _std(values: list[float], ddof: int = 1) -> float:
    """样本标准差。"""
    return math.sqrt(_variance(values, ddof))


def _skewness(values: list[float]) -> float:
    """样本偏度(Fisher-Pearson, 有偏估计)。

    γ = m3 / m2^(3/2)
    其中 mk = (1/n) * Σ(xi - mean)^k
    """
    n = len(values)
    if n < 3:
        return 0.0
    m = _mean(values)
    m2 = sum((v - m) ** 2 for v in values) / n
    m3 = sum((v - m) ** 3 for v in values) / n
    if m2 == 0:
        return 0.0
    return m3 / (m2 ** 1.5)


def _kurtosis(values: list[float]) -> float:
    """样本峰度(超额峰度, excess kurtosis)。

    κ = m4 / m2² - 3
    """
    n = len(values)
    if n < 4:
        return 0.0
    m = _mean(values)
    m2 = sum((v - m) ** 2 for v in values) / n
    m4 = sum((v - m) ** 4 for v in values) / n
    if m2 == 0:
        return 0.0
    return m4 / (m2 ** 2) - 3.0


def _expected_max_sharpe(num_trials: int) -> float:
    """多重测试期望最大值 E[max(Z_N)]。

    N=1: 0 (无需修正)
    N>1: Euler-Maclaurin 近似
        ≈ sqrt(2·ln(N)) - (ln(π) + ln(ln(N))) / (2·sqrt(2·ln(N)))

    Args:
        num_trials: 试次数 N

    Returns:
        E[max(Z_N)]
    """
    if num_trials <= 1:
        return 0.0
    ln_n = math.log(num_trials)
    if ln_n <= 0:
        return 0.0
    sqrt_2ln = math.sqrt(2.0 * ln_n)
    # Euler-Maclaurin 近似
    numerator = math.log(math.pi) + math.log(ln_n)
    return sqrt_2ln - numerator / (2.0 * sqrt_2ln)


def _variance_of_sharpe(
    sharpe: float, skewness: float, kurtosis: float, num_obs: int
) -> float:
    """Sharpe 估计量方差 V[SR] (非正态修正)。

    V[SR] = (1 - γ·SR + (κ-1)/4·SR²) / (T - 1)

    Args:
        sharpe: 非年化 Sharpe
        skewness: 偏度 γ
        kurtosis: 超额峰度 κ
        num_obs: 样本数 T

    Returns:
        V[SR]
    """
    if num_obs <= 1:
        return 0.0
    sr = sharpe
    return (1.0 - skewness * sr + (kurtosis - 1.0) / 4.0 * sr * sr) / (
        num_obs - 1
    )


class DeflatedSharpeCalculator:
    """Deflated Sharpe Ratio 计算器。

    基于 Bailey & López de Prado (2014) 修正多重测试偏差。
    无第三方依赖, 纯 math 实现。

    Usage:
        calc = DeflatedSharpeCalculator(DSRConfig(periods_per_year=252))

        # 单次回测(无多重测试修正)
        result = calc.calculate(returns, num_trials=1)

        # 试了50次取最好的 Sharpe
        result = calc.calculate(returns, num_trials=50)
        print(result.dsr)           # DSR 值
        print(result.is_significant)  # 是否显著(>= 0.95)

        # 趋势追踪(滚动窗口)
        trend = calc.track_trend(returns, num_trials=50, window=60)
    """

    def __init__(self, config: DSRConfig | None = None) -> None:
        self._config = config if config is not None else DSRConfig()

    @property
    def config(self) -> DSRConfig:
        """配置(只读)。"""
        return self._config

    def calculate(
        self,
        returns: list[float],
        num_trials: int = 1,
        risk_free_rate: float | None = None,
    ) -> DSRResult:
        """计算 Deflated Sharpe Ratio。

        Args:
            returns: 收益率序列(每期收益率, 非年化)
            num_trials: 试次数 N(回测尝试了多少策略/参数组合), 默认 1
            risk_free_rate: 每期无风险利率, None=用 config 默认值

        Returns:
            DSRResult

        Raises:
            SimulationError: 空序列 / 样本不足(<3) / num_trials<1
        """
        if not returns:
            raise SimulationError("returns 不能为空")
        if len(returns) < 3:
            raise SimulationError(
                f"样本数不足: {len(returns)} < 3(无法计算偏度/峰度)",
                details={"num_obs": len(returns)},
            )
        if num_trials < 1:
            raise SimulationError(
                f"num_trials 不能 < 1: {num_trials}",
                details={"num_trials": num_trials},
            )

        rf = risk_free_rate if risk_free_rate is not None else self._config.risk_free_rate
        n = len(returns)

        # 1. 基本 Sharpe (非年化)
        mean_ret = _mean(returns)
        std_ret = _std(returns, ddof=1)
        if std_ret == 0:
            # 零方差: 无波动, Sharpe 无定义
            sr = 0.0
        else:
            sr = (mean_ret - rf) / std_ret

        sr_annual = sr * math.sqrt(self._config.periods_per_year)

        # 2. 偏度/峰度
        gamma = _skewness(returns)
        kappa = _kurtosis(returns)

        # 3. Sharpe 估计量方差
        var_sr = _variance_of_sharpe(sr, gamma, kappa, n)

        # 4. 多重测试期望最大值
        expected_max = _expected_max_sharpe(num_trials)

        # 5. DSR
        if var_sr <= 0:
            # 方差为零(极少情况), DSR 退化为 0.5 或 1.0
            dsr = 1.0 if sr > 0 else 0.5
        else:
            # SR* = (SR - 0) / sqrt(V[SR]) - E[max(Z_N)]
            # DSR = Φ(SR*)
            sr_star = sr / math.sqrt(var_sr) - expected_max
            dsr = _normal_cdf(sr_star)

        is_significant = dsr >= self._config.significance_threshold

        result = DSRResult(
            sharpe=sr,
            sharpe_annualized=sr_annual,
            dsr=dsr,
            num_trials=num_trials,
            num_obs=n,
            skewness=gamma,
            kurtosis=kappa,
            var_sr=var_sr,
            expected_max=expected_max,
            is_significant=is_significant,
        )
        _logger.debug(
            "DSR计算: SR=%.4f SR_ann=%.4f DSR=%.4f N=%d T=%d significant=%s",
            sr, sr_annual, dsr, num_trials, n, is_significant,
        )
        return result

    def track_trend(
        self,
        returns: list[float],
        num_trials: int = 1,
        window: int = 60,
    ) -> list[DSRTrendPoint]:
        """滚动窗口 DSR 趋势追踪。

        从 window-1 位置开始, 每个位置取前 window 期收益率计算 DSR,
        形成 DSR 趋势序列。

        Args:
            returns: 完整收益率序列
            num_trials: 试次数
            window: 滚动窗口大小(默认 60)

        Returns:
            list[DSRTrendPoint], 长度 = len(returns) - window + 1

        Raises:
            SimulationError: 窗口 < 3 / 序列短于窗口
        """
        if window < 3:
            raise SimulationError(
                f"window 不能 < 3: {window}",
                details={"window": window},
            )
        if len(returns) < window:
            raise SimulationError(
                f"序列长度 {len(returns)} < 窗口 {window}",
                details={"len": len(returns), "window": window},
            )

        trend: list[DSRTrendPoint] = []
        for i in range(window, len(returns) + 1):
            window_returns = returns[i - window:i]
            result = self.calculate(window_returns, num_trials=num_trials)
            trend.append(DSRTrendPoint(
                index=i - 1,
                dsr=result.dsr,
                sharpe=result.sharpe_annualized,
            ))
        return trend


__all__ = [
    "DSRConfig",
    "DSRResult",
    "DSRTrendPoint",
    "DeflatedSharpeCalculator",
    "SimulationError",
]
