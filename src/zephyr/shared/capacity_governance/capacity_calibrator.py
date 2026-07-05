# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.capacity_governance.capacity_calibrator
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.resource_optimization; tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class CalibrationResult:
    metric_name: str
    current_value: float
    calibrated_threshold: float
    confidence: float
    timestamp: str


class CapacityCalibrator:
    def __init__(self, history_window: int = 100) -> None:
        self._history_window = history_window
        self._measurements: dict[str, list[float]] = {}

    def record(self, metric_name: str, value: float) -> None:
        if metric_name not in self._measurements:
            self._measurements[metric_name] = []
        self._measurements[metric_name].append(value)
        if len(self._measurements[metric_name]) > self._history_window:
            self._measurements[metric_name] = self._measurements[metric_name][-self._history_window :]

    def calibrate(self, metric_name: str, percentile: float = 0.95) -> CalibrationResult:
        values = self._measurements.get(metric_name, [])
        if not values:
            return CalibrationResult(metric_name, 0.0, 0.0, 0.0, "")
        sorted_vals = sorted(values)
        idx = min(int(len(sorted_vals) * percentile), len(sorted_vals) - 1)
        return CalibrationResult(
            metric_name,
            sorted_vals[-1],
            sorted_vals[idx],
            percentile,
            datetime.now(UTC).isoformat(),
        )
