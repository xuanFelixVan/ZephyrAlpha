# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md
# [MODULE] zephyr.security.access_control.decision_registry
# [DOMAIN] D_SECURITY
# [MATURITY] production
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DecisionRegistry - decision log with query and stats."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Final


@dataclass
class DecisionRecord:
    agent_id: str = ""
    operation: str = ""
    resource: str = ""
    result: str = ""
    rule_id: str = ""
    timestamp: float = field(default_factory=time.time)


class DecisionRegistry:
    def __init__(self) -> None:
        self._records: list[DecisionRecord] = []

    def log(self, agent_id: str, operation: str, resource: str, result: str, rule_id: str = "") -> DecisionRecord:
        record = DecisionRecord(
            agent_id=agent_id, operation=operation, resource=resource, result=result, rule_id=rule_id
        )
        self._records.append(record)
        return record

    def query(self, agent_id: str | None = None) -> list[DecisionRecord]:
        if agent_id is None:
            return list(self._records)
        return [r for r in self._records if r.agent_id == agent_id]

    def stats(self) -> dict[str, Any]:
        total = len(self._records)
        allowed = sum(1 for r in self._records if r.result == "ALLOWED")
        denied = sum(1 for r in self._records if r.result == "DENIED")
        return {"total": total, "allowed": allowed, "denied": denied}


__all__: Final = ["DecisionRecord", "DecisionRegistry"]
