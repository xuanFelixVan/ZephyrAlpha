# [BLUEPRINT] MOD-RK-05 | docs/03_modules/_domain-risk/var_calculator/blueprint.md
# [MODULE] zephyr.risk.core.var_calculator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy; scipy
# [CONSUMERS] MOD-RK-03(Portfolio Risk Monitor,实时监控) ; MOD-RK-16(Risk Decomposition,残差分析) ; MOD-RK-12(Stress Test) ; MOD-RK-15(Tail Risk)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] VaR≥0(损失额非负);conservative_max=max(parametric,historical);样本不足→抛InsufficientVaRHistoryError;置信度∈(0,1);holding_period≥1
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InsufficientVaRHistoryError;InvalidVaRConfigError
# [TESTS] tests/risk/test_var_calculator.py
# [A_module] module_id=MOD-RK-05 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
VaR Calculator — 风险价值计算器 (MOD-RK-05, Phase 1)

D-RISK §1.2 L2 Real-Time 盘中监控核心模块。Phase 1 实现两种方法并发计算(取max):
    1. 参数法 (Parametric / Variance-Covariance): 假设收益正态分布, VaR = (z·σ - μ)·V
    2. 历史模拟法 (Historical Simulation): 经验分位数, VaR = -quantile(r, 1-c)·V

取 max(parametric, historical) 作为保守估计 (conservative_max), 供 RK-03 实时监控使用。

Phase 2 (未实现): +蒙特卡洛法 (GPU CuPy/PyTorch)
Phase 3 (未实现): Basel III 三角验证 + 乘数因子 + 压力 VaR

关键约束 (设计真源 §6 VaR三阶段演进):
    - 每阶段独立可用——Phase 1 完成即可上线风控
    - 参数法 <1ms, 历史模拟 ~5ms (CPU 即可)
    - 依赖 DuckDB+Parquet (已有, 本模块仅做计算, 数据读取由上层负责)

属 A 类基础设施 (正态分位数 + 经验分位数, 数学逻辑明确), 置信度/持有期为 C 类可调参数。
依据: D:\\临时工作区\\依赖图\\11-D-RISK-风控域.md §1.2 RK-05, §6 VaR三阶段演进
SSoT: depgraph MOD-RK-05
Version: 0.1.0 (Phase 1)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np
from scipy.stats import norm

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "VaRMethod",
    "VaRConfig",
    "VaRResult",
    "VaRCalculator",
    "InsufficientVaRHistoryError",
    "InvalidVaRConfigError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class VaRMethod(str, Enum):
    """VaR 计算方法。"""

    PARAMETRIC = "parametric"            # 参数法 (方差-协方差, 假设正态)
    HISTORICAL = "historical"            # 历史模拟法 (经验分位数)
    CONSERVATIVE_MAX = "conservative_max"  # 取 max(parametric, historical) — Phase 1 默认


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidVaRConfigError(ZephyrBaseError):
    """VaR 配置非法 (如置信度不在 (0,1))。"""

    error_code = "ZA-RK-0005"


class InsufficientVaRHistoryError(ZephyrBaseError):
    """历史收益样本不足, 无法计算 VaR。"""

    error_code = "ZA-RK-0006"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class VaRConfig:
    """VaR 计算配置 (设计真源 §1.2 RK-05 + §6)。

    Attributes:
        confidence_level: 置信水平, 0.95 或 0.99 (常见值), 必须 ∈ (0,1)
        holding_period_days: 持有期(天), 默认 1 (日 VaR)。多日按 sqrt(T) 缩放
        method: 计算方法, 默认 CONSERVATIVE_MAX (取两法 max)
        min_history: 历史模拟法所需最少样本数, 默认 30
        annualization_factor: 年化因子(用于参数法 σ 年化输出), 默认 252 (A股交易日)
    """

    confidence_level: float = 0.95
    holding_period_days: int = 1
    method: VaRMethod = VaRMethod.CONSERVATIVE_MAX
    min_history: int = 30
    annualization_factor: int = 252

    def __post_init__(self) -> None:
        if not 0 < self.confidence_level < 1:
            raise InvalidVaRConfigError(
                f"confidence_level must be in (0,1), got {self.confidence_level}"
            )
        if self.holding_period_days < 1:
            raise InvalidVaRConfigError(
                f"holding_period_days must be >=1, got {self.holding_period_days}"
            )
        if self.min_history < 2:
            raise InvalidVaRConfigError(
                f"min_history must be >=2, got {self.min_history}"
            )
        if self.annualization_factor < 1:
            raise InvalidVaRConfigError(
                f"annualization_factor must be >=1, got {self.annualization_factor}"
            )

    @property
    def z_alpha(self) -> float:
        """标准正态分位点 z_α (α = confidence_level), 即下侧 (1-c) 分位数的绝对值。"""
        # ppf(1-c) 为负, 取绝对值得 z_α (如 0.95 → 1.6449)
        return float(abs(norm.ppf(1.0 - self.confidence_level)))


# ──────────────────────────────────────────────────────────────────────────────
# 计算结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class VaRResult:
    """VaR 计算结果。

    所有金额字段单位与传入的 portfolio_value 一致 (如 NAV 元)。
    VaR 以正数表示潜在损失额 (≥0)。

    Attributes:
        value: 最终 VaR 值 (按 method 选取, conservative_max=两法 max)
        value_pct: VaR 占 portfolio_value 的比例 (≥0)
        method: 实际使用的方法
        confidence_level: 置信水平
        holding_period_days: 持有期
        parametric_var: 参数法结果 (None 表示未计算)
        historical_var: 历史模拟法结果 (None 表示未计算)
        portfolio_value: 输入的组合价值
        mean_return: 样本平均收益 (日频)
        std_return: 样本标准差 (日频)
        sample_size: 历史样本数
        timestamp: 计算时间
    """

    value: float
    value_pct: float
    method: VaRMethod
    confidence_level: float
    holding_period_days: int
    portfolio_value: float
    mean_return: float
    std_return: float
    sample_size: int
    timestamp: datetime
    parametric_var: float | None = None
    historical_var: float | None = None

    @property
    def annualized_vol(self) -> float:
        """年化波动率 = std_return * sqrt(annualization_factor)。"""
        return float(self.std_return * np.sqrt(252.0))

    def to_dict(self) -> dict[str, Any]:
        """转为字典 (供事件/日志)。"""
        return {
            "value": self.value,
            "value_pct": self.value_pct,
            "method": self.method.value,
            "confidence_level": self.confidence_level,
            "holding_period_days": self.holding_period_days,
            "parametric_var": self.parametric_var,
            "historical_var": self.historical_var,
            "portfolio_value": self.portfolio_value,
            "mean_return": self.mean_return,
            "std_return": self.std_return,
            "sample_size": self.sample_size,
            "annualized_vol": self.annualized_vol,
        }


# ──────────────────────────────────────────────────────────────────────────────
# VaR 计算器
# ──────────────────────────────────────────────────────────────────────────────


class VaRCalculator:
    """VaR 风险价值计算器 (Phase 1: 参数法 + 历史模拟, 取 max)。

    用法 (单序列收益):
        calc = VaRCalculator()
        returns = np.array([...])  # 日收益序列
        result = calc.calculate(returns, portfolio_value=1_000_000.0)
        print(result.value)        # 95% 日 VaR (元)

    用法 (多资产 + 权重):
        asset_returns = np.array([[...], [...]]).T  # (T, N)
        weights = np.array([0.6, 0.4])
        result = calc.calculate_portfolio(asset_returns, weights, portfolio_value=1e6)

    Args:
        config: 计算配置, 默认 95% 日 VaR, conservative_max
    """

    def __init__(self, config: VaRConfig | None = None) -> None:
        self._config = config or VaRConfig()

    @property
    def config(self) -> VaRConfig:
        return self._config

    # ── 公开 API ──

    def calculate(
        self,
        returns: np.ndarray,
        portfolio_value: float,
        now: datetime | None = None,
    ) -> VaRResult:
        """对单序列收益计算 VaR。

        Args:
            returns: 日收益序列 (1D array), 如组合净值日收益率
            portfolio_value: 当前组合价值 (如 NAV 元)
            now: 时间戳

        Returns:
            VaRResult

        Raises:
            InsufficientVaRHistoryError: 样本数 < min_history
            InvalidVaRConfigError: portfolio_value 非正
        """
        returns = self._validate_returns(returns)
        if portfolio_value <= 0:
            raise InvalidVaRConfigError(
                f"portfolio_value must be positive, got {portfolio_value}"
            )
        now = now or datetime.now(timezone.utc)

        mean_r = float(np.mean(returns))
        std_r = float(np.std(returns, ddof=1)) if len(returns) > 1 else 0.0
        n = len(returns)

        if self._config.method is VaRMethod.PARAMETRIC:
            p_var = self._parametric(mean_r, std_r, portfolio_value)
            h_var: float | None = None
            value = p_var
        elif self._config.method is VaRMethod.HISTORICAL:
            h_var = self._historical(returns, portfolio_value)
            p_var = None
            value = h_var
        else:  # CONSERVATIVE_MAX
            p_var = self._parametric(mean_r, std_r, portfolio_value)
            h_var = self._historical(returns, portfolio_value)
            value = max(p_var, h_var)

        value_pct = value / portfolio_value if portfolio_value > 0 else 0.0

        logger.info(
            "VaR computed: method=%s value=%.2f (%.4f%%) parametric=%s historical=%s n=%d",
            self._config.method.value,
            value,
            value_pct * 100,
            f"{p_var:.2f}" if p_var is not None else None,
            f"{h_var:.2f}" if h_var is not None else None,
            n,
        )

        return VaRResult(
            value=value,
            value_pct=value_pct,
            method=self._config.method,
            confidence_level=self._config.confidence_level,
            holding_period_days=self._config.holding_period_days,
            portfolio_value=portfolio_value,
            mean_return=mean_r,
            std_return=std_r,
            sample_size=n,
            timestamp=now,
            parametric_var=p_var,
            historical_var=h_var,
        )

    def calculate_portfolio(
        self,
        asset_returns: np.ndarray,
        weights: np.ndarray,
        portfolio_value: float,
        now: datetime | None = None,
    ) -> VaRResult:
        """对多资产组合计算 VaR (先合成组合收益序列, 再套用 calculate)。

        Args:
            asset_returns: 资产收益矩阵, shape (T, N), T=历史天数, N=资产数
            weights: 权重向量, shape (N,), 须与 asset_returns 列对齐
            portfolio_value: 组合价值
            now: 时间戳

        Returns:
            VaRResult (基于合成组合收益序列)
        """
        asset_returns = np.asarray(asset_returns, dtype=float)
        weights = np.asarray(weights, dtype=float)
        if asset_returns.ndim != 2:
            raise InvalidVaRConfigError(
                f"asset_returns must be 2D (T,N), got shape {asset_returns.shape}"
            )
        if weights.ndim != 1 or weights.shape[0] != asset_returns.shape[1]:
            raise InvalidVaRConfigError(
                f"weights shape {weights.shape} mismatched with asset_returns "
                f"columns {asset_returns.shape[1]}"
            )
        # 合成组合日收益 = weights @ asset_returns.T
        portfolio_returns = asset_returns @ weights
        return self.calculate(portfolio_returns, portfolio_value, now=now)

    # ── 内部: 计算方法 ──

    def _parametric(
        self, mean_r: float, std_r: float, portfolio_value: float
    ) -> float:
        """参数法: VaR = (z_α·σ - μ)·V·sqrt(T), 下限 0。

        - z_α = |ppf(1-c)| (如 0.95 → 1.6449)
        - σ 用样本标准差 (ddof=1)
        - 多日按 sqrt(holding_period) 缩放
        - (z·σ - μ) 可能为负 (高均值低波动) → VaR 取 0 下限
        """
        z = self._config.z_alpha
        T = self._config.holding_period_days
        # 日 VaR (损失额, 正数)
        daily_var = (z * std_r - mean_r) * portfolio_value
        # 多日缩放
        var = daily_var * np.sqrt(T)
        return float(max(0.0, var))

    def _historical(
        self, returns: np.ndarray, portfolio_value: float
    ) -> float:
        """历史模拟法: VaR = -quantile(r, 1-c)·V·sqrt(T)。

        - 取收益序列的下侧 (1-c) 经验分位数 (负数=损失)
        - VaR = -该分位数 · portfolio_value (正数)
        - 多日按 sqrt(T) 缩放 (历史模拟的平方根缩放为近似)
        """
        c = self._config.confidence_level
        T = self._config.holding_period_days
        # 下侧 (1-c) 分位数 (如 0.05 分位)
        q = float(np.quantile(returns, 1.0 - c))
        var = -q * portfolio_value * np.sqrt(T)
        return float(max(0.0, var))

    # ── 内部: 校验 ──

    def _validate_returns(self, returns: np.ndarray) -> np.ndarray:
        """校验并规范化收益序列。"""
        arr = np.asarray(returns, dtype=float)
        if arr.ndim != 1:
            raise InvalidVaRConfigError(
                f"returns must be 1D, got shape {arr.shape}"
            )
        # 过滤 NaN
        arr = arr[~np.isnan(arr)]
        if len(arr) < self._config.min_history:
            raise InsufficientVaRHistoryError(
                f"need >= {self._config.min_history} valid returns, got {len(arr)}"
            )
        return arr
