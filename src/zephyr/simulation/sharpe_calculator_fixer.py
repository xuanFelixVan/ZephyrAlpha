# [BLUEPRINT] MOD-SIM-023 | docs/03_modules/_domain_simulation/sharpe_calculator_fixer/blueprint.md
# [MODULE] zephyr.simulation.sharpe_calculator_fixer
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.simulation.deflated_sharpe_calculator; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.simulation.strategy_simulator; zephyr.simulation.result_analyzer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SharpeResult/SharpeConfig frozen不可变; 样本<60时sharpe=None; float计算; 无第三方依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SimulationError(ZA-SIM-0023)
# [TESTS] tests/simulation/test_sharpe_calculator_fixer.py
# [TTL] permanent
"""D_SIMULATION — Sharpe Calculator Fixer (Sharpe 计算修正器)

A股场景的 Sharpe 比率修正: 中国10Y国债无风险利率 + 样本量门禁 +
非正态检测(Jarque-Bera)→Sortino + DSR修正 + 滚动Sharpe + 自动年化。

属 A 类基础设施(确定性数学计算), 纯基础层不涉及策略。

设计真源: depgraph MOD-SIM-023
蓝图: docs/03_modules/_domain_simulation/sharpe_calculator_fixer/blueprint.md
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.simulation.deflated_sharpe_calculator import (
    DeflatedSharpeCalculator,
    DSRConfig,
    _kurtosis,
    _mean,
    _skewness,
    _std,
)

_logger = logging.getLogger(__name__)


class SimulationError(ZephyrBaseError):
    """仿真计算异常——输入非法。"""

    error_code = "ZA-SIM-0023"


class SharpeMethod(str, Enum):
    """Sharpe 计算方法选择。"""

    SHARPE = "sharpe"  # 正态分布, 用标准 Sharpe
    SORTINO = "sortino"  # 非正态分布, 用 Sortino
    INSUFFICIENT = "insufficient"  # 样本不足, 不计算


@dataclass(frozen=True)
class SharpeConfig:
    """Sharpe 修正配置——不可变。

    Attributes:
        min_samples: 最小样本量(低于此不计算, 默认 60)
        periods_per_year: 年化频率(A股日度=252)
        risk_free_rate: 每期无风险利率(默认中国10Y国债~2.5%年化/252)
        jb_critical: Jarque-Bera 临界值(χ²(2) α=0.05 ≈ 5.99)
        dsr_threshold: DSR 显著性阈值
    """

    min_samples: int = 60
    periods_per_year: int = 252
    risk_free_rate: float = 0.025 / 252  # 中国10年期国债~2.5%年化
    jb_critical: float = 5.99
    dsr_threshold: float = 0.95


@dataclass(frozen=True)
class SharpeResult:
    """Sharpe 修正计算结果——不可变。

    Attributes:
        sharpe: 非年化 Sharpe(样本不足为 None)
        sharpe_annualized: 年化 Sharpe
        sortino: 非年化 Sortino(非正态时计算, 否则 None)
        sortino_annualized: 年化 Sortino
        dsr: Deflated Sharpe Ratio(样本不足为 None)
        method: 使用的方法(SHARPE/SORTINO/INSUFFICIENT)
        is_non_normal: 是否非正态
        skewness: 偏度
        kurtosis: 超额峰度
        jb_statistic: Jarque-Bera 统计量
        num_obs: 样本数
        risk_free_rate: 使用的无风险利率
    """

    sharpe: float | None
    sharpe_annualized: float | None
    sortino: float | None
    sortino_annualized: float | None
    dsr: float | None
    method: SharpeMethod
    is_non_normal: bool
    skewness: float
    kurtosis: float
    jb_statistic: float
    num_obs: int
    risk_free_rate: float


def _downside_std(returns: list[float], rf: float) -> float:
    """下行标准差(用于 Sortino)。

    downside_dev = min(0, returns - rf)
    downside_std = sqrt(mean(downside_dev²))
    """
    n = len(returns)
    if n == 0:
        return 0.0
    sq_sum = sum(min(0.0, r - rf) ** 2 for r in returns) / n
    return math.sqrt(sq_sum)


def _jarque_bera(skewness: float, kurtosis: float, n: int) -> float:
    """Jarque-Bera 正态性检验统计量。

    JB = n/6 * (γ² + κ²/4)
    JB > 5.99 → 拒绝正态(α=0.05, χ²(2))
    """
    if n == 0:
        return 0.0
    return n / 6.0 * (skewness ** 2 + kurtosis ** 2 / 4.0)


class SharpeCalculatorFixer:
    """Sharpe 计算修正器——A股场景的 Sharpe 修正。

    修正项:
      1. 无风险利率用中国10年期国债(非美国T-bill)
      2. 样本量 < 60 不计算(统计不显著)
      3. 非正态分布用 Sortino 替代(Jarque-Bera 检测)
      4. 多重测试偏差用 DSR(MOD-SIM-024)修正
      5. 年化按频率自动选择

    Usage:
        fixer = SharpeCalculatorFixer()

        result = fixer.calculate(returns, num_trials=50)
        if result.method == SharpeMethod.INSUFFICIENT:
            print("样本不足")
        elif result.is_non_normal:
            print(f"Sortino={result.sortino_annualized}")
        else:
            print(f"Sharpe={result.sharpe_annualized}, DSR={result.dsr}")

        # 滚动 Sharpe
        rolling = fixer.rolling_sharpe(returns, window=60)
    """

    def __init__(self, config: SharpeConfig | None = None) -> None:
        self._config = config if config is not None else SharpeConfig()
        self._dsr_calc = DeflatedSharpeCalculator(
            DSRConfig(
                periods_per_year=self._config.periods_per_year,
                significance_threshold=self._config.dsr_threshold,
                risk_free_rate=self._config.risk_free_rate,
            )
        )

    @property
    def config(self) -> SharpeConfig:
        """配置(只读)。"""
        return self._config

    def calculate(
        self,
        returns: list[float],
        num_trials: int = 1,
        risk_free_rate: float | None = None,
    ) -> SharpeResult:
        """计算修正后的 Sharpe/Sortino + DSR。

        Args:
            returns: 收益率序列(每期)
            num_trials: 试次数(传给 DSR)
            risk_free_rate: 每期无风险利率, None=用 config 默认

        Returns:
            SharpeResult(样本不足时 sharpe/sortino/dsr 为 None)

        Raises:
            SimulationError: 空序列
        """
        if not returns:
            raise SimulationError("returns 不能为空")

        rf = (
            risk_free_rate
            if risk_free_rate is not None
            else self._config.risk_free_rate
        )
        n = len(returns)

        # 1. 样本量门禁
        if n < self._config.min_samples:
            return SharpeResult(
                sharpe=None,
                sharpe_annualized=None,
                sortino=None,
                sortino_annualized=None,
                dsr=None,
                method=SharpeMethod.INSUFFICIENT,
                is_non_normal=False,
                skewness=0.0,
                kurtosis=0.0,
                jb_statistic=0.0,
                num_obs=n,
                risk_free_rate=rf,
            )

        # 2. 统计量
        gamma = _skewness(returns)
        kappa = _kurtosis(returns)
        jb = _jarque_bera(gamma, kappa, n)
        is_non_normal = jb > self._config.jb_critical

        # 3. Sharpe
        mean_ret = _mean(returns)
        std_ret = _std(returns, ddof=1)
        annual_factor = math.sqrt(self._config.periods_per_year)

        if std_ret == 0:
            sharpe = 0.0
        else:
            sharpe = (mean_ret - rf) / std_ret
        sharpe_annual = sharpe * annual_factor

        # 4. 非正态 -> Sortino
        sortino: float | None = None
        sortino_annual: float | None = None
        if is_non_normal:
            d_std = _downside_std(returns, rf)
            if d_std == 0:
                sortino = 0.0
            else:
                sortino = (mean_ret - rf) / d_std
            sortino_annual = sortino * annual_factor

        # 5. DSR
        dsr: float | None = None
        try:
            dsr_result = self._dsr_calc.calculate(
                returns, num_trials=num_trials, risk_free_rate=rf
            )
            dsr = dsr_result.dsr
        except Exception:
            _logger.warning("DSR 计算失败, 跳过", exc_info=True)

        method = (
            SharpeMethod.SORTINO if is_non_normal else SharpeMethod.SHARPE
        )

        result = SharpeResult(
            sharpe=sharpe,
            sharpe_annualized=sharpe_annual,
            sortino=sortino,
            sortino_annualized=sortino_annual,
            dsr=dsr,
            method=method,
            is_non_normal=is_non_normal,
            skewness=gamma,
            kurtosis=kappa,
            jb_statistic=jb,
            num_obs=n,
            risk_free_rate=rf,
        )
        _logger.debug(
            "Sharpe修正: method=%s SR=%.4f Sortino=%s DSR=%s JB=%.2f non_normal=%s",
            method.value,
            sharpe,
            f"{sortino:.4f}" if sortino is not None else "N/A",
            f"{dsr:.4f}" if dsr is not None else "N/A",
            jb,
            is_non_normal,
        )
        return result

    def rolling_sharpe(
        self,
        returns: list[float],
        window: int = 60,
        num_trials: int = 1,
    ) -> list[SharpeResult]:
        """滚动窗口 Sharpe 修正计算。

        Args:
            returns: 完整收益率序列
            window: 滚动窗口大小(默认 60, 不小于 min_samples)
            num_trials: 试次数

        Returns:
            list[SharpeResult], 长度 = len(returns) - window + 1

        Raises:
            SimulationError: 窗口 < min_samples / 序列短于窗口
        """
        effective_window = max(window, self._config.min_samples)
        if effective_window != window:
            _logger.info(
                "滚动窗口 %d < min_samples %d, 调整为 %d",
                window,
                self._config.min_samples,
                effective_window,
            )
        if len(returns) < effective_window:
            raise SimulationError(
                f"序列长度 {len(returns)} < 窗口 {effective_window}",
                details={"len": len(returns), "window": effective_window},
            )

        results: list[SharpeResult] = []
        for i in range(effective_window, len(returns) + 1):
            window_returns = returns[i - effective_window:i]
            results.append(
                self.calculate(window_returns, num_trials=num_trials)
            )
        return results


__all__ = [
    "SharpeCalculatorFixer",
    "SharpeConfig",
    "SharpeMethod",
    "SharpeResult",
    "SimulationError",
]
