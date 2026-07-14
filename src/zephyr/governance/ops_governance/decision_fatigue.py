# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_governance.decision_fatigue
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-GOV_decision_fatigue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class EisenhowerPriority(str, Enum):
    P0_DO_NOW = "P0"
    P1_SCHEDULE = "P1"
    P2_DELEGATE = "P2"
    P3_ELIMINATE = "P3"


class TaskTriage(BaseModel):
    task_id: str
    description: str
    urgent: bool = False
    important: bool = False
    priority: EisenhowerPriority = EisenhowerPriority.P3_ELIMINATE

    def classify(self) -> EisenhowerPriority:
        if self.urgent and self.important:
            self.priority = EisenhowerPriority.P0_DO_NOW
        elif self.important and not self.urgent:
            self.priority = EisenhowerPriority.P1_SCHEDULE
        elif self.urgent and not self.important:
            self.priority = EisenhowerPriority.P2_DELEGATE
        else:
            self.priority = EisenhowerPriority.P3_ELIMINATE
        return self.priority


def triage(tasks: list[TaskTriage]) -> dict[EisenhowerPriority, list[TaskTriage]]:
    result: dict[EisenhowerPriority, list[TaskTriage]] = {p: [] for p in EisenhowerPriority}
    for t in tasks:
        t.classify()
        result[t.priority].append(t)
    return result


def filter_priority(tasks: list[TaskTriage], level: EisenhowerPriority) -> list[TaskTriage]:
    return [t for t in tasks if t.priority == level]
