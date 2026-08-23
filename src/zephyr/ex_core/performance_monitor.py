# [BLUEPRINT] MOD-EX-036 | docs/03_modules/MOD-EX-036/
# [MODULE] zephyr.ex_core.performance_monitor
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] 无（纯标准库）
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 单机进程内存态（无 DB/网络）；窗口有界（超出逐出最旧样本）；告警判定只读不写
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPerformanceInputError(ZA-EX-0022)——负值/非有限值/空指标名/非法窗口/非法阈值
# [TESTS] tests/ex_core/test_performance_monitor.py
# [A_module] module_id=MOD-EX-036 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""执行核心性能监控器（MOD-EX-036）——单机轻量实现。

记录执行链路关键操作的延迟/数值样本（下单延迟/成交回报延迟/风控门耗时等），
滑动窗口内存态聚合（count/mean/min/max/p95），阈值越线经注入的 alerter 回调外发。
约束二单机前提：无 DB/网络/后台线程，调用方线程内 record + check_alerts 即可。
"""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

__all__: Final = [
    "InvalidPerformanceInputError",
    "MetricStats",
    "PerformanceMonitor",
]

_DEFAULT_WINDOW_SIZE: Final[int] = 512


class InvalidPerformanceInputError(Exception):
    """ZA-EX-0022: 性能监控输入非法。"""

    error_code = "ZA-EX-0022"


@dataclass(frozen=True)
class MetricStats:
    """单指标滑动窗口聚合。"""

    metric: str
    count: int
    mean: float
    min: float
    max: float
    p95: float


def _percentile(sorted_values: list[float], q: float) -> float:
    """最近邻分位数（q ∈ (0,1]）。"""
    if not sorted_values:
        return 0.0
    idx = max(0, min(len(sorted_values) - 1, math.ceil(q * len(sorted_values)) - 1))
    return sorted_values[idx]


class PerformanceMonitor:
    """执行核心性能监控器（单机轻量）。"""

    def __init__(
        self,
        *,
        window_size: int = _DEFAULT_WINDOW_SIZE,
        alerter: Callable[[dict], None] | None = None,
    ) -> None:
        if window_size <= 0:
            raise InvalidPerformanceInputError(f"window_size 必须为正: {window_size}")
        self._window_size = window_size
        self._alerter = alerter
        self._samples: dict[str, deque[float]] = {}
        self._thresholds: dict[str, float] = {}

    # ── 采样 ─────────────────────────────────────────────────────────

    def record(self, metric: str, value: float) -> None:
        """记录一条样本（如 operation 延迟 ms）。非法输入 → ZA-EX-0022。"""
        if not metric:
            raise InvalidPerformanceInputError("metric 名不得为空")
        v = float(value)
        if not math.isfinite(v):
            raise InvalidPerformanceInputError(f"样本值必须有限: {value}")
        if v < 0.0:
            raise InvalidPerformanceInputError(f"样本值不得为负: {value}")
        if metric not in self._samples:
            self._samples[metric] = deque(maxlen=self._window_size)
        self._samples[metric].append(v)

    def metrics(self) -> list[str]:
        return sorted(self._samples)

    # ── 聚合 ─────────────────────────────────────────────────────────

    def stats(self, metric: str) -> MetricStats:
        values = sorted(self._samples.get(metric, ()))
        if not values:
            return MetricStats(metric=metric, count=0, mean=0.0, min=0.0, max=0.0, p95=0.0)
        return MetricStats(
            metric=metric,
            count=len(values),
            mean=sum(values) / len(values),
            min=values[0],
            max=values[-1],
            p95=_percentile(values, 0.95),
        )

    # ── 阈值告警 ─────────────────────────────────────────────────────

    def set_threshold(self, metric: str, threshold: float) -> None:
        """设定指标越线阈值（latest 样本 > threshold 即告警）。"""
        if not metric:
            raise InvalidPerformanceInputError("metric 名不得为空")
        t = float(threshold)
        if not math.isfinite(t) or t < 0.0:
            raise InvalidPerformanceInputError(f"阈值必须为非负有限值: {threshold}")
        self._thresholds[metric] = t

    def check_alerts(self) -> list[dict]:
        """逐阈值指标判定最新样本是否越线；越线经 alerter 回调外发并返回清单。"""
        breaches: list[dict] = []
        for metric, threshold in sorted(self._thresholds.items()):
            samples = self._samples.get(metric)
            if not samples:
                continue
            latest = samples[-1]
            if latest > threshold:
                breach = {"metric": metric, "value": latest, "threshold": threshold}
                breaches.append(breach)
                if self._alerter is not None:
                    self._alerter(breach)
        return breaches

    # ── 快照 ─────────────────────────────────────────────────────────

    def snapshot(self) -> dict:
        return {
            "metrics": {
                name: {
                    "count": s.count,
                    "mean": s.mean,
                    "min": s.min,
                    "max": s.max,
                    "p95": s.p95,
                }
                for name in self.metrics()
                for s in [self.stats(name)]
            },
            "thresholds": dict(self._thresholds),
            "window_size": self._window_size,
        }
