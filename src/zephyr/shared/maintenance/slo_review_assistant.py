# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.maintenance.slo_review_assistant
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement.gate_engine; zephyr.infrastructure.capacity_assurance.modules.__init__; tests.unit.shared.test_orphan_integration
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
class SloReview:
    slo_name: str
    target: float
    actual: float
    compliance: bool
    gap: float


SloStatus = SloReview


class SloReviewAssistant:
    def __init__(self):
        self._slos: dict[str, tuple[float, float]] = {}

    def register_slo(self, name: str, target: float) -> None:
        self._slos[name] = (target, 0.0)

    def update_actual(self, name: str, actual: float) -> None:
        if name in self._slos:
            target, _ = self._slos[name]
            self._slos[name] = (target, actual)

    def review(self) -> list[SloReview]:
        results = []
        for name, (target, actual) in self._slos.items():
            results.append(SloReview(name, target, actual, actual >= target, max(0.0, target - actual)))
        return results

    def non_compliant(self) -> list[SloReview]:
        return [r for r in self.review() if not r.compliance]
