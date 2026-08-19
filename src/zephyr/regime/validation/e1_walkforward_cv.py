# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §0.5.7 E1 / §4.5 E1 / §5
# [MODULE] zephyr.regime.validation.e1_walkforward_cv
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan Phase 4 E1
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯统计函数: 只消费既有 walk-forward 各窗口 MaxDD 改善产物, 不重跑回测; CV=std(ddof=1)/|mean|; 均值≈0 时 CV 退化定义(见代码); 至少 2 窗口; frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] E1WalkForwardCVError(ZA-REGIME-0037)
# [TESTS] tests/regime/validation/test_e1_walkforward_cv.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: improvements(walk-forward 各季度窗口 MaxDD 改善序列, 既有回测产物, 如 46 季度)
# I2: cv_threshold=0.50(§5 E1 判定门槛)
# F1: improvements_from_pairs((dd_base, dd_exp) 窗口对 → |dd_base|−|dd_exp| 改善序列, 统一正/负值约定)
# A1: compute_improvement_cv(mean/std/CV 正式统计 → CV<0.5 判定)
# O1: E1CVReport(n_windows/mean/std/cv/passed)
# [/ALGO_FLOW]
"""D_REGIME — E1 Walk-Forward 稳定性正式统计（11 号 memo §0.5.7 E1）。

纯统计函数：消费既有 walk-forward 回测产物（各季度窗口的 MaxDD 改善序列，
production 参数 train_years=5 / refit QE / 46 季度边界，见 memo §4.5 E1），
按 §5 E1 门槛「各窗口 MaxDD 改善的变异系数 CV < 0.5」判定稳定性。

依据: 11_regime_backtest_validation_plan §4.5 E1 / §5
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Sequence

import numpy as np

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

_EPS = 1e-12


class E1WalkForwardCVError(ZephyrBaseError):
    """ZA-REGIME-0037: E1 walk-forward CV 统计错误（输入非法）。"""

    error_code = "ZA-REGIME-0037"


@dataclass(frozen=True)
class E1CVReport:
    """E1 walk-forward CV 统计报告——不可变。"""

    n_windows: int
    mean_improvement: float  # 各窗口 MaxDD 改善均值
    std_improvement: float  # 样本标准差（ddof=1）
    cv: float  # 变异系数 std/|mean|；均值≈0 时：std≈0→0.0，否则→inf
    passed: bool  # cv < cv_threshold（§5 E1=0.5）
    summary: str


def improvements_from_pairs(pairs: Sequence[tuple[float, float]]) -> list[float]:
    """(dd_baseline, dd_experiment) 窗口对 → MaxDD 改善序列 |dd_base|−|dd_exp|。

    统一正/负值两种 MaxDD 存储约定（c1_comparator 同款绝对值处理）。
    """
    return [abs(float(b)) - abs(float(e)) for b, e in pairs]


def compute_improvement_cv(
    improvements: Sequence[float],
    cv_threshold: float = 0.50,
) -> E1CVReport:
    """E1 主入口：各窗口 MaxDD 改善的变异系数正式统计。

    Args:
        improvements: 各 walk-forward 窗口的 MaxDD 改善（≥2 窗口）。
        cv_threshold: 判定门槛（§5 E1=0.50，CV<threshold 为稳定）。

    Returns:
        E1CVReport；passed = cv < cv_threshold。

    Raises:
        E1WalkForwardCVError: 窗口数<2 / 含非有限值 / 门槛非正。
    """
    if cv_threshold <= 0:
        raise E1WalkForwardCVError(f"cv_threshold 需 >0: {cv_threshold}")
    vals = np.asarray(improvements, dtype=float)
    if vals.size < 2:
        raise E1WalkForwardCVError(f"窗口数需 ≥2: {vals.size}")
    if not np.isfinite(vals).all():
        raise E1WalkForwardCVError("improvements 含 NaN/Inf")

    mean = float(vals.mean())
    std = float(vals.std(ddof=1))
    if abs(mean) < _EPS:
        cv = 0.0 if std < _EPS else float("inf")
    else:
        cv = std / abs(mean)
    passed = cv < cv_threshold
    summary = (
        f"E1 walk-forward 稳定性: {vals.size} 窗口, MaxDD改善 mean={mean:+.4f} "
        f"std={std:.4f} CV={cv:.3f} 门槛<{cv_threshold:.2f} → "
        f"{'稳定' if passed else '不稳定（参数过拟合警告）'}"
    )
    _logger.info("E1 完成: %s", summary)
    return E1CVReport(
        n_windows=int(vals.size),
        mean_improvement=mean,
        std_improvement=std,
        cv=cv,
        passed=passed,
        summary=summary,
    )


__all__ = [
    "E1CVReport",
    "E1WalkForwardCVError",
    "compute_improvement_cv",
    "improvements_from_pairs",
]
