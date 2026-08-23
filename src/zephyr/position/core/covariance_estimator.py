# [BLUEPRINT] MOD-POS-011 | docs/03_modules/MOD-POS-011/
# [MODULE] zephyr.position.core.covariance_estimator
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-POS-013(风险预算分配器) ; MOD-POS-012(相关性regime监控) ; D_RISK
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Ledoit-Wolf收缩标准做法(目标=等方差对角阵μI); 收缩强度κ∈[0,1]; 输出矩阵对称; 输入须N≥2标的且T≥2等长有限序列; 常数序列(零方差)拒绝; 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-POS-011/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCovarianceInputError(ZA-POS-0019)
# [TESTS] tests/position/test_covariance_estimator.py
# [A_module] module_id=MOD-POS-011 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Covariance Estimator — Ledoit-Wolf 收缩协方差估计器 (MOD-POS-011)

风险预算/相关性监控的公共估计底座。小样本（T 有限、N 标的）下样本协方差
病态，Ledoit-Wolf 收缩是标准做法：以等方差对角阵 μI 为收缩目标，按数据
自适应强度 κ∈[0,1] 收缩：

    Σ_shrunk = κ·μI + (1−κ)·S_sample

κ 由 Ledoit-Wolf (2004) 公式闭式估计（d²/b² 框架），无需调参。

纪律：
  - 纯函数、无 IO、无真源依赖——收益率序列由调用方注入（禁自造数据管道）；
  - 输入校验 Fail-Closed：非等长/样本不足/非有限值/零方差序列一律拒绝；
  - 与选股信号零耦合（三维解耦 how much 层基础设施）。

依据: Ledoit & Wolf (2004) "A well-conditioned estimator for
large-dimensional covariance matrices"
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

import numpy as np

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "CovarianceEstimate",
    "InvalidCovarianceInputError",
    "estimate_covariance",
]

_MIN_OBSERVATIONS: Final = 2
# 零方差判定地板（浮点容差）：日收益率量级 ~1e-2，方差 ~1e-4；
# 1e-12 对应 std<1e-6，视为常数序列（无可估风险结构）
_ZERO_VARIANCE_FLOOR: Final = 1e-12


class InvalidCovarianceInputError(ZephyrBaseError):
    """协方差估计输入非法（长度不齐/样本不足/非有限值/零方差）。"""

    error_code = "ZA-POS-0019"


@dataclass(frozen=True)
class CovarianceEstimate:
    """协方差估计结果（frozen 不可变）。

    Attributes:
        symbols: 标的代码（字典序排序，与 matrix 行列对齐）
        matrix: N×N 收缩后协方差矩阵（行主序嵌套 tuple）
        shrinkage: Ledoit-Wolf 收缩强度 κ∈[0,1]（0=纯样本协方差，1=纯对角目标）
        n_observations: 样本量 T（各序列等长）
    """

    symbols: tuple[str, ...]
    matrix: tuple[tuple[float, ...], ...]
    shrinkage: float
    n_observations: int

    def to_nested_dict(self) -> dict[str, dict[str, float]]:
        """转为 {symbol: {symbol: cov}} 嵌套字典口径（供 JSON 序列化/审计留痕）。"""
        return {
            s1: {s2: self.matrix[i][j] for j, s2 in enumerate(self.symbols)}
            for i, s1 in enumerate(self.symbols)
        }


def estimate_covariance(
    returns: Mapping[str, Sequence[float]],
) -> CovarianceEstimate:
    """Ledoit-Wolf 收缩协方差估计（纯函数）。

    Args:
        returns: {symbol: 收益率序列}，要求 N≥2 个标的、各序列等长 T≥2、
            全部为有限值、无零方差（常数）序列

    Returns:
        CovarianceEstimate（symbols 字典序，matrix 为收缩后协方差）

    Raises:
        InvalidCovarianceInputError: 输入违反任一前置条件
    """
    if not returns:
        raise InvalidCovarianceInputError("收益率输入为空（须 N≥2 个标的）")
    if len(returns) < 2:
        raise InvalidCovarianceInputError(
            f"标的数不足（须 N≥2 才有协方差结构），got {len(returns)}"
        )

    symbols = tuple(sorted(returns))
    lengths = {len(returns[s]) for s in symbols}
    if len(lengths) != 1:
        raise InvalidCovarianceInputError(
            f"收益率序列长度不齐（须等长），lengths={sorted(lengths)}"
        )
    n_obs = lengths.pop()
    if n_obs < _MIN_OBSERVATIONS:
        raise InvalidCovarianceInputError(
            f"样本量不足（须 T≥{_MIN_OBSERVATIONS}），got {n_obs}"
        )

    x = np.array([[float(v) for v in returns[s]] for s in symbols], dtype=float).T  # T×N
    if not np.isfinite(x).all():
        raise InvalidCovarianceInputError("收益率含非有限值（NaN/Inf）")

    # 去均值（按列）
    x_dm = x - x.mean(axis=0)
    variances = (x_dm**2).sum(axis=0) / n_obs
    if (variances <= _ZERO_VARIANCE_FLOOR).any():
        bad = symbols[int(np.argmin(variances))]
        raise InvalidCovarianceInputError(f"标的 {bad} 收益率零方差（常数序列无可估风险结构）")

    n_assets = len(symbols)
    # 样本协方差 S = X'X / T（Ledoit-Wolf 2004 原文口径，ddof=0）
    sample = (x_dm.T @ x_dm) / n_obs

    # 收缩目标 F = μI，μ = tr(S)/N
    mu = float(np.trace(sample) / n_assets)
    target = np.eye(n_assets) * mu

    # d² = ||S − F||²_F / N
    delta = sample - target
    d2 = float((delta**2).sum() / n_assets)

    if d2 <= 0.0:
        # S 已等于目标（各标的等方差且零协方差）→ 无需收缩
        kappa = 0.0
        shrunk = sample
    else:
        # b² = (1/T²)·Σ_t ||x_t x_t' − S||²_F / N， capped at d²
        b2_sum = 0.0
        for t in range(n_obs):
            outer = np.outer(x_dm[t], x_dm[t])
            diff = outer - sample
            b2_sum += float((diff**2).sum())
        b2 = min(b2_sum / (n_obs**2) / n_assets, d2)
        kappa = b2 / d2
        shrunk = kappa * target + (1.0 - kappa) * sample

    kappa = min(max(kappa, 0.0), 1.0)
    # 数值对称化（消除浮点非对称）
    shrunk = (shrunk + shrunk.T) / 2.0

    matrix = tuple(tuple(float(shrunk[i, j]) for j in range(n_assets)) for i in range(n_assets))
    if not all(math.isfinite(v) for row in matrix for v in row):
        raise InvalidCovarianceInputError("估计结果含非有限值（输入数据病态）")

    return CovarianceEstimate(
        symbols=symbols,
        matrix=matrix,
        shrinkage=float(kappa),
        n_observations=n_obs,
    )
