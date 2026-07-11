# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.correlation.external_health
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_external_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""External Health Monitor — v0.14.0 R193

Blindspot: External dependency health unmonitored; cascading failure misdiagnosed.
Risk: R193 — External API returns 500; FLE diagnoses as internal pipeline failure.

Mitigation: External dependency health scoring with cascading failure suppression.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class DependencyStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"


@dataclass
class DependencyHealth:
    service: str
    status: DependencyStatus = DependencyStatus.HEALTHY
    last_success: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    health_score: float = 100.0


@dataclass
class ExternalHealth:
    dependencies: dict[str, DependencyHealth] = field(default_factory=dict)

    def register(self, service: str) -> DependencyHealth:
        dep = DependencyHealth(service=service)
        self.dependencies[service] = dep
        return dep

    def report_success(self, service: str) -> None:
        if service in self.dependencies:
            dep = self.dependencies[service]
            dep.status = DependencyStatus.HEALTHY
            dep.consecutive_failures = 0
            dep.last_success = time.time()
            dep.health_score = min(100.0, dep.health_score + 10.0)

    def report_failure(self, service: str) -> None:
        if service in self.dependencies:
            dep = self.dependencies[service]
            dep.consecutive_failures += 1
            dep.health_score = max(0.0, dep.health_score - 20.0)
            if dep.consecutive_failures >= 3:
                dep.status = DependencyStatus.DOWN

    def suppress_internal_alerts(self) -> set[str]:
        return {s for s, d in self.dependencies.items() if d.status == DependencyStatus.DOWN}
