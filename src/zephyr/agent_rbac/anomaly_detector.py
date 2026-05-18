# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.anomaly_detector

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""异常检测器——z-score基线+滑动窗口+多指标异常融合评分."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnomalyScore(BaseModel):
    metric: str
    current_value: float
    mean: float
    std: float
    z_score: float = 0.0
    anomalous: bool = False
    anomaly_pct: float = 0.0


class AnomalyDetector:
    _WINDOW_SIZE: int = 100

    def __init__(self) -> None:
        self._history: dict[str, list[float]] = {}

    def feed(self, metric: str, value: float) -> AnomalyScore:
        if metric not in self._history:
            self._history[metric] = []
        self._history[metric].append(value)
        if len(self._history[metric]) > self._WINDOW_SIZE:
            self._history[metric] = self._history[metric][-self._WINDOW_SIZE:]

        values = self._history[metric]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = variance ** 0.5

        z_score = abs(value - mean) / max(std, 0.001)
        anomalous = z_score > 3.0

        return AnomalyScore(
            metric=metric,
            current_value=value,
            mean=mean,
            std=std,
            z_score=z_score,
            anomalous=anomalous,
            anomaly_pct=min(100.0, z_score / 6.0 * 100.0),
        )
