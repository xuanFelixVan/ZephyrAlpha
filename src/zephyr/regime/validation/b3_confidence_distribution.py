# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §4.2 B3 / §0.5.7
# [MODULE] zephyr.regime.validation.b3_confidence_distribution
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan B3 置信度合理性(BM-BT-03-E)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯分析函数: 只消费既有 walk-forward 逐日 max(P) 产物; 默认四档边界(0.60,0.80,0.95)按 memo §4.2 B3(生产档界已改,调用方可传新边界); 判定=低置信占比<40% 且 高置信占比<50% 且 无死档; frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] B3ConfidenceError(ZA-REGIME-0034)
# [TESTS] tests/regime/validation/test_b3_confidence_distribution.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: max_p_values(walk-forward 全区间逐日 max(P) 序列, 既有 detector 产物, 值域[0,1])
# I2: edges 四档边界 + low_share_max=0.40 / high_share_max=0.50(memo §4.2 B3 判定阈值)
# A1: analyze_confidence_distribution(分位数统计 + 四档桶占比 + 死档检测 + 判定)
# O1: B3ConfidenceReport(均值/分位数/桶占比/dead_buckets/passed)
# [/ALGO_FLOW]
"""D_REGIME — B3 置信度合理性分析（11 号 memo §4.2 B3）。

纯分析函数：消费既有 walk-forward 全区间逐日 max(P)（最高态概率）产物，
统计分布（均值/中位数/P10-P90）与四档桶占比，按 §4.2 B3 判定：
  - max(P)<60% 天数占比 < 40%（非长期强收缩，否则节流器变急停器）；
  - max(P)>95% 天数占比 < 50%（非长期虚设，否则 ConfidenceSignal 形同虚设）；
  - 四档均有实际使用（无死档）。

默认四档边界 (0.60,0.80,0.95) 取自 memo §4.2 B3；生产档界经 C1 校准已改为
0.50/0.30/0.15（regime_detector._CONFIDENCE_BANDS），对生产数据分析时调用方
应传入对应边界。

依据: 11_regime_backtest_validation_plan §4.2 B3 / §0.5.7
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

# memo §4.2 B3 四档边界（<60% / 60-80% / 80-95% / >95%）
DEFAULT_EDGES: tuple[float, float, float] = (0.60, 0.80, 0.95)
_BUCKET_NAMES = ("low(<e1)", "mid_low(e1-e2)", "mid_high(e2-e3)", "high(>=e3)")


class B3ConfidenceError(ZephyrBaseError):
    """ZA-REGIME-0034: B3 置信度分布分析错误（输入非法）。"""

    error_code = "ZA-REGIME-0034"


@dataclass(frozen=True)
class B3ConfidenceReport:
    """B3 置信度分布报告——不可变。"""

    n: int
    mean: float
    median: float
    p10: float
    p25: float
    p75: float
    p90: float
    bucket_shares: tuple[float, ...]  # 四档桶占比（与 edges 对应）
    low_share: float  # <edges[0] 占比
    high_share: float  # ≥edges[2] 占比
    dead_buckets: tuple[str, ...]  # 占比=0 的死档名
    passed: bool  # low<low_share_max 且 high<high_share_max 且无死档
    summary: str


def analyze_confidence_distribution(
    max_p_values: Sequence[float],
    edges: tuple[float, float, float] = DEFAULT_EDGES,
    low_share_max: float = 0.40,
    high_share_max: float = 0.50,
) -> B3ConfidenceReport:
    """B3 主入口：max(P) 分布合理性分析。

    Args:
        max_p_values: 逐日 max(P) 序列（值域 [0,1]，非空）。
        edges: 四档边界（严格升序，(0,1) 内）。
        low_share_max: 低置信占比上限（memo=0.40）。
        high_share_max: 高置信占比上限（memo=0.50）。

    Raises:
        B3ConfidenceError: 空序列 / 值越出 [0,1] / 边界或门槛非法。
    """
    if len(edges) != 3 or not (0.0 < edges[0] < edges[1] < edges[2] < 1.0):
        raise B3ConfidenceError(f"edges 须为 (0,1) 内严格升序三元组: {edges}")
    if not 0.0 < low_share_max < 1.0 or not 0.0 < high_share_max < 1.0:
        raise B3ConfidenceError(
            f"占比门槛须在 (0,1): low={low_share_max} high={high_share_max}"
        )
    vals = np.asarray(max_p_values, dtype=float)
    if vals.size == 0:
        raise B3ConfidenceError("max_p_values 不能为空")
    if not np.isfinite(vals).all() or (vals < 0.0).any() or (vals > 1.0).any():
        raise B3ConfidenceError("max_p_values 须为 [0,1] 内有限值")

    buckets = np.digitize(vals, bins=np.asarray(edges))  # 0..3
    shares = tuple(float(np.mean(buckets == k)) for k in range(4))
    low_share, high_share = shares[0], shares[3]
    dead = tuple(name for name, s in zip(_BUCKET_NAMES, shares, strict=True) if s == 0.0)
    passed = (
        low_share < low_share_max and high_share < high_share_max and not dead
    )
    q10, q25, q50, q75, q90 = (float(q) for q in np.quantile(vals, [0.1, 0.25, 0.5, 0.75, 0.9]))
    summary = (
        f"B3 置信度合理性: {vals.size} 天, mean={float(vals.mean()):.3f} median={q50:.3f} "
        f"[P10={q10:.3f} P90={q90:.3f}], 桶占比={[f'{s:.1%}' for s in shares]}, "
        f"低置信={low_share:.1%}(<{low_share_max:.0%}) 高置信={high_share:.1%}(<{high_share_max:.0%}) "
        f"死档={list(dead) or '无'} → {'合理' if passed else '不合理'}"
    )
    _logger.info("B3 完成: %s", summary)
    return B3ConfidenceReport(
        n=int(vals.size),
        mean=float(vals.mean()),
        median=q50,
        p10=q10,
        p25=q25,
        p75=q75,
        p90=q90,
        bucket_shares=shares,
        low_share=low_share,
        high_share=high_share,
        dead_buckets=dead,
        passed=passed,
        summary=summary,
    )


__all__ = [
    "B3ConfidenceError",
    "B3ConfidenceReport",
    "DEFAULT_EDGES",
    "analyze_confidence_distribution",
]
