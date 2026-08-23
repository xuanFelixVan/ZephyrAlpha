# [BLUEPRINT] MOD-POS-012 | docs/03_modules/MOD-POS-012/
# [MODULE] zephyr.position.core.correlation_regime_monitor
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.covariance_estimator ; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-POS-013(风险预算分配器) ; D_RISK(自适应风控⑤相关性监控)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 相关矩阵由MOD-POS-011收缩协方差标准化(对角=1,值域[-1,1]); 平均成对相关不含对角; regime三档(LOW/NORMAL/HIGH)按阈值单调划分; HIGH→diversification_effective=False+分散失效预警; 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-POS-012/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCorrelationRegimeInputError(ZA-POS-0020) ; 数据校验委托MOD-POS-011 InvalidCovarianceInputError透传
# [TESTS] tests/position/test_correlation_regime_monitor.py
# [A_module] module_id=MOD-POS-012 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Correlation Regime Monitor — 相关性 regime 监控 (MOD-POS-012)

宪章 §1.3 能力⑤自适应风控的"相关性监控"落点：监控组合持仓标的间的平均
成对相关，划分三档 regime：

  - LOW（avg < low_threshold）：相关性低，分散化有效；
  - NORMAL（low ≤ avg < high）：常态区间；
  - HIGH（avg ≥ high_threshold）：相关性抬升，分散化失效风险——
    危机中资产相关性趋向 1，账面"分散"的组合可能实则同向暴露。

估计链路：收益率序列 → MOD-POS-011 Ledoit-Wolf 收缩协方差 → 标准化为
相关矩阵（对策略/选股信号零耦合，三维解耦 how much 层）。

纪律：纯函数、无 IO；数据校验委托 MOD-POS-011（Fail-Closed 透传）。
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.position.core.covariance_estimator import estimate_covariance
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "CorrelationRegime",
    "CorrelationRegimeReport",
    "InvalidCorrelationRegimeInputError",
    "assess_correlation_regime",
]

# 默认阈值（经验基线，可经参数覆盖——不硬编码为全局常量真源）
_DEFAULT_LOW_THRESHOLD: Final = 0.3
_DEFAULT_HIGH_THRESHOLD: Final = 0.6


class CorrelationRegime(str, Enum):
    """相关性 regime 三档。"""

    LOW = "LOW"  # 低相关，分散化有效
    NORMAL = "NORMAL"  # 常态
    HIGH = "HIGH"  # 高相关，分散化失效风险


class InvalidCorrelationRegimeInputError(ZephyrBaseError):
    """相关性 regime 监控参数非法（阈值越界/乱序/非有限）。"""

    error_code = "ZA-POS-0020"


@dataclass(frozen=True)
class CorrelationRegimeReport:
    """相关性 regime 评估报告（frozen 不可变）。

    Attributes:
        symbols: 标的代码（字典序，与 correlation_matrix 行列对齐）
        correlation_matrix: N×N 相关矩阵（对角=1，对称）
        avg_pairwise_correlation: 平均成对相关（i<j 上三角均值，不含对角）
        regime: 三档 regime 判定
        diversification_effective: 分散化是否有效（HIGH→False）
        max_pair: 最高相关标的对（symbol_a, symbol_b）
        max_pair_correlation: 最高成对相关值
        warnings: 预警信息（高相关 regime 的分散失效预警等）
    """

    symbols: tuple[str, ...]
    correlation_matrix: tuple[tuple[float, ...], ...]
    avg_pairwise_correlation: float
    regime: CorrelationRegime
    diversification_effective: bool
    max_pair: tuple[str, str]
    max_pair_correlation: float
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _validate_thresholds(low_threshold: float, high_threshold: float) -> None:
    for name, v in (("low_threshold", low_threshold), ("high_threshold", high_threshold)):
        if not math.isfinite(v) or v < 0.0 or v > 1.0:
            raise InvalidCorrelationRegimeInputError(
                f"{name} 非法（须为 [0,1] 有限值），got {v}"
            )
    if low_threshold >= high_threshold:
        raise InvalidCorrelationRegimeInputError(
            f"low_threshold 须严格小于 high_threshold，got {low_threshold} >= {high_threshold}"
        )


def assess_correlation_regime(
    returns: Mapping[str, Sequence[float]],
    *,
    low_threshold: float = _DEFAULT_LOW_THRESHOLD,
    high_threshold: float = _DEFAULT_HIGH_THRESHOLD,
) -> CorrelationRegimeReport:
    """评估组合相关性 regime（纯函数）。

    Args:
        returns: {symbol: 收益率序列}（前置条件同 MOD-POS-011）
        low_threshold: LOW/NORMAL 分界（默认 0.3）
        high_threshold: NORMAL/HIGH 分界（默认 0.6）

    Returns:
        CorrelationRegimeReport

    Raises:
        InvalidCorrelationRegimeInputError: 阈值非法
        InvalidCovarianceInputError: 收益率数据非法（MOD-POS-011 透传）
    """
    _validate_thresholds(low_threshold, high_threshold)

    est = estimate_covariance(returns)
    n = len(est.symbols)

    # 协方差→相关矩阵：corr_ij = cov_ij / sqrt(var_i * var_j)
    corr: list[list[float]] = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                corr[i][j] = 1.0
            else:
                denom = math.sqrt(est.matrix[i][i] * est.matrix[j][j])
                corr[i][j] = max(-1.0, min(1.0, est.matrix[i][j] / denom))

    # 平均成对相关（上三角 i<j，不含对角）+ 最高对
    pair_sum = 0.0
    pair_count = 0
    max_pair = (est.symbols[0], est.symbols[1])
    max_corr = -2.0
    for i in range(n):
        for j in range(i + 1, n):
            c = corr[i][j]
            pair_sum += c
            pair_count += 1
            if c > max_corr:
                max_corr = c
                max_pair = (est.symbols[i], est.symbols[j])
    avg_corr = pair_sum / pair_count

    if avg_corr >= high_threshold:
        regime = CorrelationRegime.HIGH
    elif avg_corr >= low_threshold:
        regime = CorrelationRegime.NORMAL
    else:
        regime = CorrelationRegime.LOW

    warnings: list[str] = []
    if regime is CorrelationRegime.HIGH:
        warnings.append(
            f"组合平均成对相关 {avg_corr:.3f} ≥ {high_threshold}，"
            "分散化失效风险（高相关 regime，账面分散可能实则同向暴露）"
        )

    return CorrelationRegimeReport(
        symbols=est.symbols,
        correlation_matrix=tuple(tuple(row) for row in corr),
        avg_pairwise_correlation=avg_corr,
        regime=regime,
        diversification_effective=regime is not CorrelationRegime.HIGH,
        max_pair=max_pair,
        max_pair_correlation=max_corr,
        warnings=tuple(warnings),
    )
