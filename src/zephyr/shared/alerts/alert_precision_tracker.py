# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.alerts.alert_precision_tracker
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
class PrecisionMetrics:
    total_alerts: int
    true_positives: int
    false_positives: int
    precision: float
    recall: float


class AlertPrecisionTracker:
    def __init__(self):
        self._true_positives: int = 0
        self._false_positives: int = 0
        self._false_negatives: int = 0

    def record_true_positive(self) -> None:
        self._true_positives += 1

    def record_false_positive(self) -> None:
        self._false_positives += 1

    def record_false_negative(self) -> None:
        self._false_negatives += 1

    def compute(self) -> PrecisionMetrics:
        total = self._true_positives + self._false_positives
        precision = self._true_positives / total if total > 0 else 0.0
        actual_positives = self._true_positives + self._false_negatives
        recall = self._true_positives / actual_positives if actual_positives > 0 else 0.0
        return PrecisionMetrics(total, self._true_positives, self._false_positives, precision, recall)

    def metrics(self) -> PrecisionMetrics:
        return self.compute()
