# [BLUEPRINT] MOD-SIG-052 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §2
# [MODULE] zephyr.signal_ashare.adaptive_conformal_tcp_rm_ddci
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] （远期：MOD-SIG-044 rolling 基线的加权升级消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 未 calibrate 时 predict_interval 一律 fail-closed（ValueError）；权重必须非负且不全零；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空校准集/权重长度不符/权重负值或全零/α∉(0,1)/未校准取区间 → ValueError
# [TESTS] tests/signal_ashare/test_adaptive_conformal_tcp_rm_ddci.py
# [A_module] module_id=MOD-SIG-052 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""自适应保形 TCP-RM/DDCI（MOD-SIG-052，91 号 memo BM-SEL-14-A）。

MOD-SIG-044 rolling conformal（slow unweighted，Phase 0 基线）的**加权变体**
（TCP-RM/DDCI 路线登记 Phase 2 远期）：校准残差带权重（如近期加权/regime 加权），
安全缓冲 q̂ 取**加权**第 ⌈(n+1)(1−α)⌉ 分位——权重非负且归一，近期权重大时
margin 跟随近期残差尺度收缩。

轻量实现口径：加权 split-conformal 核心算法即可测交付；DDCI（分布漂移检测
触发权重重置）留接口位（calibrate 可反复调用，权重由调用方供给）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np

__all__: Final = [
    "AdaptiveConformalTcpRmDdci",
    "WeightedPredictionInterval",
]


@dataclass(frozen=True)
class WeightedPredictionInterval:
    """加权保形预测区间。"""

    point: float
    lower: float
    upper: float
    alpha: float
    margin: float
    n_calibration: int
    weighted: bool


def _weighted_conformal_quantile(scores: np.ndarray, weights: np.ndarray, alpha: float) -> float:
    """加权 split-conformal 分位数：最小 s 使累计权重比 ≥ ceil((n+1)(1−α))/n。"""
    order = np.argsort(scores)
    s_sorted = scores[order]
    w_sorted = weights[order]
    cum = np.cumsum(w_sorted) / w_sorted.sum()
    n = len(scores)
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    target = min(max(k, 1), n) / n
    idx = int(np.searchsorted(cum, target, side="left"))
    return float(s_sorted[min(idx, n - 1)])


class AdaptiveConformalTcpRmDdci:
    """自适应保形（TCP-RM/DDCI 加权变体）。"""

    def __init__(self, *, alpha: float = 0.05) -> None:
        if not 0.0 < alpha < 1.0:
            raise ValueError(f"alpha 必须 ∈ (0,1): {alpha}")
        self._alpha = alpha
        self._margin: float | None = None
        self._n_cal = 0

    @property
    def margin(self) -> float | None:
        return self._margin

    def calibrate(self, residuals: np.ndarray, weights: np.ndarray | None = None) -> "AdaptiveConformalTcpRmDdci":
        """校准加权安全缓冲。weights 缺省=均匀（退化为 split-conformal 口径）。"""
        r = np.asarray(residuals, dtype=float).ravel()
        if r.size == 0:
            raise ValueError("校准集为空")
        if not np.all(np.isfinite(r)):
            raise ValueError("校准残差含非有限值")
        scores = np.abs(r)
        if weights is None:
            w = np.ones_like(scores)
        else:
            w = np.asarray(weights, dtype=float).ravel()
            if w.shape != scores.shape:
                raise ValueError(f"权重长度不符: {w.size} vs {scores.size}")
            if not np.all(np.isfinite(w)) or np.any(w < 0.0):
                raise ValueError("权重必须为非负有限值")
            if w.sum() <= 0.0:
                raise ValueError("权重全零（无法归一）")
        self._margin = _weighted_conformal_quantile(scores, w, self._alpha)
        self._n_cal = int(scores.size)
        return self

    def predict_interval(self, point: float) -> WeightedPredictionInterval:
        """区间 = point ± 加权 q̂。未校准 fail-closed。"""
        if self._margin is None:
            raise ValueError("未校准（calibrate 未调用）——predict_interval fail-closed")
        return WeightedPredictionInterval(
            point=float(point),
            lower=float(point) - self._margin,
            upper=float(point) + self._margin,
            alpha=self._alpha,
            margin=self._margin,
            n_calibration=self._n_cal,
            weighted=True,
        )
