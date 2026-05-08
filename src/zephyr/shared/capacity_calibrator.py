"""
Progressive Capacity Calibrator — 非线性涌现校准器 (盲点 #60)
特性：
  - 每 100 模块自动校准
  - 误差 > 20% → 修正因子应用
"""
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CalibrationPoint:
    module_count: int
    predicted_memory_mb: float
    actual_memory_mb: float
    error_pct: float
    timestamp: float = field(default_factory=time.time)


class CapacityCalibrator:
    """
    容量渐进校准器 (盲点 #60)
    """

    CALIBRATION_INTERVAL = 100
    ERROR_THRESHOLD = 0.20

    def __init__(self):
        self._correction_factor = 1.0
        self._points: list[CalibrationPoint] = []

    def record(self, module_count: int, predicted_memory_mb: float,
               actual_memory_mb: float) -> Optional[float]:
        if predicted_memory_mb == 0:
            return None

        error_pct = abs(actual_memory_mb - predicted_memory_mb) / predicted_memory_mb
        point = CalibrationPoint(
            module_count=module_count,
            predicted_memory_mb=predicted_memory_mb,
            actual_memory_mb=actual_memory_mb,
            error_pct=round(error_pct, 3),
        )
        self._points.append(point)

        if error_pct > self.ERROR_THRESHOLD:
            self._correction_factor = actual_memory_mb / predicted_memory_mb

        return self._correction_factor

    def apply_correction(self, raw_estimate: float) -> float:
        return raw_estimate * self._correction_factor

    def get_correction_factor(self) -> float:
        return self._correction_factor

    def get_calibration_history(self) -> list[dict]:
        return [
            {
                "count": p.module_count,
                "predicted": p.predicted_memory_mb,
                "actual": p.actual_memory_mb,
                "error_pct": p.error_pct,
            }
            for p in self._points[-10:]
        ]
