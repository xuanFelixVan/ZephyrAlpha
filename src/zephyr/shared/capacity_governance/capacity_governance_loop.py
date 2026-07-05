# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.shared.capacity_governance.capacity_governance_loop
# [DOMAIN] D_GOVERNANCE
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
from enum import Enum


class GovernanceAction(Enum):
    HOLD = "hold"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    DEGRADE = "degrade"
    ALERT = "alert"


@dataclass
class GovernanceDecision:
    action: GovernanceAction
    reason: str
    confidence: float


class CapacityGovernanceLoop:
    def __init__(self, upper_threshold: float = 0.85, lower_threshold: float = 0.3) -> None:
        self._upper = upper_threshold
        self._lower = lower_threshold

    def evaluate(self, utilization: float) -> GovernanceDecision:
        if utilization <= 0.0:
            return GovernanceDecision(
                GovernanceAction.ALERT,
                f"utilization {utilization:.1%} is zero or negative — possible monitoring failure or cold start",
                0.5,
            )
        if utilization >= self._upper:
            return GovernanceDecision(
                GovernanceAction.SCALE_UP,
                f"utilization {utilization:.1%} >= {self._upper:.1%}",
                0.9,
            )
        if utilization <= self._lower:
            return GovernanceDecision(
                GovernanceAction.SCALE_DOWN,
                f"utilization {utilization:.1%} <= {self._lower:.1%}",
                0.8,
            )
        return GovernanceDecision(
            GovernanceAction.HOLD,
            f"utilization {utilization:.1%} within bounds",
            1.0,
        )
