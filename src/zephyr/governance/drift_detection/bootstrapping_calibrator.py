# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.drift_detection.bootstrapping_calibrator
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/budget/test_budget_enforcer_submodules.py; tests/governance/lifecycle/test_bootstrapping_calibrator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_bootstrapping_calibrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class CalibrationPoint:
    actual_tokens: int
    estimated_tokens: int
    actual_cost: float
    estimated_cost: float
    actual_time: float
    estimated_time: float
    error_ratio: float
    timestamp: float = field(default_factory=time.time)


class BootstrappingCalibrator:
    def __init__(self, min_data_points: int = 100, duration_days: int = 30):
        self._min_data_points = min_data_points
        self._duration_days = duration_days
        self._points: deque[CalibrationPoint] = deque(maxlen=200)
        self._calibrated: bool = False
        self._correction_factor: float = 1.0
        self._start_time: float = time.time()

    def record(
        self,
        actual_tokens: int,
        estimated_tokens: int,
        actual_cost: float = 0.0,
        estimated_cost: float = 0.0,
        actual_time: float = 0.0,
        estimated_time: float = 1.0,
    ) -> CalibrationPoint:
        est_total = estimated_tokens + estimated_cost * 10000 + estimated_time * 100
        act_total = actual_tokens + actual_cost * 10000 + actual_time * 100
        error = act_total / est_total if est_total > 0 else 1.0

        point = CalibrationPoint(
            actual_tokens=actual_tokens,
            estimated_tokens=estimated_tokens,
            actual_cost=actual_cost,
            estimated_cost=estimated_cost,
            actual_time=actual_time,
            estimated_time=estimated_time,
            error_ratio=error,
        )
        self._points.append(point)
        self._recalibrate()
        return point

    def _recalibrate(self) -> None:
        if len(self._points) < self._min_data_points:
            return
        avg_error = sum(p.error_ratio for p in self._points) / len(self._points)
        self._correction_factor = avg_error
        self._calibrated = True

    def calibrate_estimate(self, estimated_tokens: int) -> int:
        if not self._calibrated:
            return estimated_tokens
        return int(estimated_tokens * self._correction_factor)

    @property
    def is_calibrated(self) -> bool:
        return self._calibrated

    @property
    def correction_factor(self) -> float:
        return self._correction_factor

    def data_points(self) -> int:
        return len(self._points)

    def days_elapsed(self) -> float:
        return (time.time() - self._start_time) / 86400.0

    def is_bootstrapping(self) -> bool:
        return self.days_elapsed() < self._duration_days and not self._calibrated

    def get_hard_limit_multiplier(self) -> float:
        if not self._calibrated:
            return 3.0
        cf = self._correction_factor
        return max(1.5, min(3.0, cf * 2.0))

    def reset(self) -> None:
        self._points.clear()
        self._calibrated = False
        self._correction_factor = 1.0
        self._start_time = time.time()
