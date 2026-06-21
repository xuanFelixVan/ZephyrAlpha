# [A_module] module_id=MOD-SHR_capacity_runbook_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

from dataclasses import dataclass, field


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
                RunbookStep(3, "Verify SLO", "python scripts/governance/audit_registration.py", "exit 0"),
            ]
        else:
            steps = [
                RunbookStep(1, "Verify stability", "Monitor for 5 minutes", "no alerts"),
                RunbookStep(2, "Reduce allocation", "Release excess capacity", "utilization within bounds"),
            ]
        return Runbook(scenario, steps, list(reversed(steps)))
