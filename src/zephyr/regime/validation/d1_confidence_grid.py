# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §0.5.7 D1 / §4.4
# [MODULE] zephyr.regime.validation.d1_confidence_grid
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan Phase 3 D1
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯分析函数: 不重跑回测, 只重放四档映射; 默认档镜像 regime_detector._CONFIDENCE_BANDS(0.50/0.30/0.15 下界); 扰动后档界须严格降序且在(0,1)内否则该网格点跳过; 效果代理指标=置信序列均值
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] D1ConfidenceGridError(ZA-REGIME-0035)
# [TESTS] tests/regime/validation/test_d1_confidence_grid.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: max_p_values(walk-forward 全区间逐日 max(P) 序列, 既有 detector 产物)
# I2: bands(四档映射 (下界,base) 降序, 默认镜像 detector 生产值) + pct=0.20 扰动幅度
# F1: apply_confidence_bands(单点 max(P)→base_confidence, 从高到低取首个命中档)
# A1: run_d1_threshold_grid(三档下界各 ×{0.8,1.0,1.2} 全网格 27 组合→合法组合重放序列→均值/档位占比)
# A2: 相对变化 |均值−基线均值|/|基线均值| <30% 判定(§4.4 D 类稳健门槛)
# O1: D1GridReport(基线均值 + 逐网格点统计 + max_rel_change + passed)
# [/ALGO_FLOW]
"""D_REGIME — D1 ConfidenceSignal 四档阈值 ±20% 敏感性网格（11 号 memo §0.5.7 D1）。

纯分析函数：不重跑回测，只把既有 walk-forward 产物（逐日 max(P) 序列）在
扰动后的四档映射下重放，统计置信序列均值与各档占比的变化，按 §4.4 D 类门槛
（±20% 扰动效果变化 <30%）判定阈值稳健性。

默认四档镜像 regime_detector._CONFIDENCE_BANDS 生产值
（(0.50,1.0)/(0.30,0.9)/(0.15,0.8)/(0.0,0.7)，C1 验证 2026-08-06 校准版）；
仅扰动三个非零下界，映射系数不动。

依据: 11_regime_backtest_validation_plan §0.5.7 D1 / §4.4
Version: 0.1.0
"""

from __future__ import annotations

import itertools
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

# 默认四档映射（镜像 regime_detector._CONFIDENCE_BANDS，2026-08-06 C1 校准版）
DEFAULT_CONFIDENCE_BANDS: tuple[tuple[float, float], ...] = (
    (0.50, 1.0),  # top1 ≥50% → 满部署
    (0.30, 0.9),  # 30-50% → 轻度收缩
    (0.15, 0.8),  # 15-30% → 中度收缩
    (0.0, 0.7),   # <15% → 强收缩（防御保留档）
)


class D1ConfidenceGridError(ZephyrBaseError):
    """ZA-REGIME-0035: D1 四档网格分析错误（输入非法/档界非法）。"""

    error_code = "ZA-REGIME-0035"


@dataclass(frozen=True)
class D1GridPoint:
    """单网格点结果——不可变。"""

    thresholds: tuple[float, ...]  # 扰动后的非零下界（降序）
    mean_confidence: float  # 重放序列均值
    band_shares: tuple[float, ...]  # 各档天数占比（与 bands 同序）
    rel_change: float  # 均值相对基线变化


@dataclass(frozen=True)
class D1GridReport:
    """D1 四档敏感性网格报告——不可变。"""

    baseline_mean: float
    points: tuple[D1GridPoint, ...]  # 含基线点（factor 全 1.0）
    n_skipped: int  # 扰动后档界非法（非严格降序/越界）被跳过的组合数
    max_rel_change: float
    passed: bool  # max_rel_change < tolerance
    summary: str


def apply_confidence_bands(
    max_p: float, bands: tuple[tuple[float, float], ...] = DEFAULT_CONFIDENCE_BANDS
) -> float:
    """单点 max(P) → base_confidence（从高到低取首个 max(P)≥下界 的档）。"""
    for bound, coef in bands:
        if max_p >= bound:
            return coef
    return bands[-1][1] if bands else 1.0


def _validate_bands(bands: tuple[tuple[float, float], ...]) -> None:
    if len(bands) < 2:
        raise D1ConfidenceGridError(f"bands 需 ≥2 档: {len(bands)}")
    bounds = [b for b, _ in bands]
    if any(b < 0.0 or b > 1.0 for b in bounds):
        raise D1ConfidenceGridError(f"档界须在 [0,1]: {bounds}")
    if any(bounds[i] <= bounds[i + 1] for i in range(len(bounds) - 1)):
        raise D1ConfidenceGridError(f"档界须严格降序: {bounds}")


def run_d1_threshold_grid(
    max_p_values: Sequence[float],
    bands: tuple[tuple[float, float], ...] = DEFAULT_CONFIDENCE_BANDS,
    pct: float = 0.20,
    tolerance: float = 0.30,
) -> D1GridReport:
    """D1 主入口：四档下界 ±20% 全网格敏感性。

    三档非零下界各取 {×(1−pct), ×1, ×(1+pct)} 共 27 组合；扰动后档界非严格
    降序或越出 (0,1] 的组合跳过（计入 n_skipped）。效果代理指标 = 重放置信
    序列均值（不重跑回测，纯映射重放）。

    Args:
        max_p_values: 逐日 max(P) 序列（既有 walk-forward 产物），值域 [0,1]。
        bands: 四档映射（默认镜像 detector 生产值）。
        pct: 扰动幅度（默认 ±20%）。
        tolerance: 相对变化门槛（§4.4 D 类=0.30）。

    Raises:
        D1ConfidenceGridError: 空序列 / 值越出 [0,1] / 档界非法 / pct 或 tolerance 非正。
    """
    _validate_bands(bands)
    if pct <= 0 or tolerance <= 0:
        raise D1ConfidenceGridError(f"pct/tolerance 需 >0: {pct}/{tolerance}")
    max_p = np.asarray(max_p_values, dtype=float)
    if max_p.size == 0:
        raise D1ConfidenceGridError("max_p_values 不能为空")
    if not np.isfinite(max_p).all() or (max_p < 0.0).any() or (max_p > 1.0).any():
        raise D1ConfidenceGridError("max_p_values 须为 [0,1] 内有限值")

    def _series_stats(thresholds: tuple[float, ...]) -> tuple[float, tuple[float, ...]]:
        new_bounds = list(thresholds) + [bands[-1][0]]
        coefs = [c for _, c in bands]
        series = np.empty(max_p.size, dtype=float)
        for i, v in enumerate(max_p):
            for bound, coef in zip(new_bounds, coefs, strict=True):
                if v >= bound:
                    series[i] = coef
                    break
        shares = tuple(
            float(np.mean(series == coef)) for coef in coefs
        )
        return float(series.mean()), shares

    base_bounds = tuple(b for b, _ in bands[:-1])
    baseline_mean, _ = _series_stats(base_bounds)

    factors = (1.0 - pct, 1.0, 1.0 + pct)
    points: list[D1GridPoint] = []
    n_skipped = 0
    for combo in itertools.product(factors, repeat=len(base_bounds)):
        thresholds = tuple(b * f for b, f in zip(base_bounds, combo, strict=True))
        strictly_desc = all(
            thresholds[i] > thresholds[i + 1] for i in range(len(thresholds) - 1)
        ) and thresholds[-1] > bands[-1][0]
        in_range = all(0.0 < t <= 1.0 for t in thresholds)
        if not (strictly_desc and in_range):
            n_skipped += 1
            continue
        mean_c, shares = _series_stats(thresholds)
        rel = abs(mean_c - baseline_mean) / max(abs(baseline_mean), _EPS)
        points.append(
            D1GridPoint(
                thresholds=thresholds,
                mean_confidence=mean_c,
                band_shares=shares,
                rel_change=rel,
            )
        )

    if not points:
        raise D1ConfidenceGridError("全网格组合均非法（档界扰动后无严格降序组合）")
    max_rel = max(p.rel_change for p in points)
    passed = max_rel < tolerance
    summary = (
        f"D1 四档 ±{pct:.0%} 网格: {len(points)} 合法点（跳过 {n_skipped}）, "
        f"基线均值={baseline_mean:.4f}, 最大相对变化={max_rel:.2%} 门槛<{tolerance:.0%} → "
        f"{'稳健' if passed else '敏感（存在悬崖网格点）'}"
    )
    _logger.info("D1 完成: %s", summary)
    return D1GridReport(
        baseline_mean=baseline_mean,
        points=tuple(points),
        n_skipped=n_skipped,
        max_rel_change=max_rel,
        passed=passed,
        summary=summary,
    )


__all__ = [
    "DEFAULT_CONFIDENCE_BANDS",
    "D1ConfidenceGridError",
    "D1GridPoint",
    "D1GridReport",
    "apply_confidence_bands",
    "run_d1_threshold_grid",
]
