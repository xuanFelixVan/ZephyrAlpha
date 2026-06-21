# [A_module] module_id=MOD-SHR_capacity_calibrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


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
            self._measurements[metric_name] = self._measurements[metric_name][-self._history_window:]

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
            datetime.now(timezone.utc).isoformat(),
        )
