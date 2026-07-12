# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.resilience.error_budget_tracker
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__; zephyr.feedback_loop.auto_evolution; tests.unit.shared.test_orphan_integration
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


@dataclass
class BudgetStatus:
    total_budget: float
    consumed: float
    remaining: float
    burn_rate: float
    time_to_exhaustion_hours: float


class ErrorBudgetTracker:
    def __init__(self, slo_target: float = 0.999, window_hours: float = 720.0):
        if slo_target < 0.0 or slo_target >= 1.0:
            raise ValueError(f"slo_target must be in [0.0, 1.0), got {slo_target}")
        if window_hours <= 0:
            raise ValueError(f"window_hours must be > 0, got {window_hours}")
        self._slo_target = slo_target
        self._window_hours = window_hours
        self._errors: int = 0
        self._total_requests: int = 0

    def record_success(self) -> None:
        self._total_requests += 1

    def record_error(self) -> None:
        self._errors += 1
        self._total_requests += 1

    def status(self) -> BudgetStatus:
        budget = 1.0 - self._slo_target
        if self._total_requests == 0:
            return BudgetStatus(budget, 0.0, budget, 0.0, float("inf"))
        error_rate = self._errors / self._total_requests
        consumed = max(0.0, error_rate - (1.0 - self._slo_target - budget))
        remaining = max(0.0, budget - consumed)
        burn_rate = consumed / self._window_hours if self._window_hours > 0 else 0.0
        tte = remaining / burn_rate if burn_rate > 0 else float("inf")
        return BudgetStatus(budget, consumed, remaining, burn_rate, tte)
