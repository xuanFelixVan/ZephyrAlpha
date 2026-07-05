# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.capacity_governance.capacity_runbook_generator
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


@dataclass
class RunbookStep:
    order: int
    action: str
    command: str
    validation: str


@dataclass
class Runbook:
    scenario: str
    steps: list[RunbookStep]
    rollback_steps: list[RunbookStep]


class CapacityRunbookGenerator:
    def generate(self, scenario: str, current_util: float, target_util: float) -> Runbook:
        if current_util > target_util:
            steps = [
                RunbookStep(1, "Assess load", "python scripts/governance/diagnose_depgraph.py", "exit 0"),
                RunbookStep(2, "Scale resources", "Adjust capacity allocation", "utilization < target"),
                RunbookStep(3, "Verify SLO", "python scripts/governance/d11_compliance/audit_registration.py", "exit 0"),
            ]
        else:
            steps = [
                RunbookStep(1, "Verify stability", "Monitor for 5 minutes", "no alerts"),
                RunbookStep(2, "Reduce allocation", "Release excess capacity", "utilization within bounds"),
            ]
        return Runbook(scenario, steps, list(reversed(steps)))
