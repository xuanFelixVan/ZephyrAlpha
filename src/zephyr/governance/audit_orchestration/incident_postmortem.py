# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.incident_postmortem
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_orchestration.__init__
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
# [A_module] module_id=MOD-GOV_incident_postmortem | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""事件复盘管理器（CT-INCIDENT）——incident记录+timeline+action_items+postmortem。"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Incident(BaseModel):
    incident_id: str
    severity: str = "P2"
    description: str = ""
    timeline: list[dict] = Field(default_factory=list)
    root_cause: str = ""
    action_items: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class IncidentManager:
    def __init__(self):
        self._incidents: dict[str, Incident] = {}

    def create(self, incident_id: str, description: str, severity: str = "P2") -> Incident:
        inc = Incident(incident_id=incident_id, description=description, severity=severity)
        self._incidents[incident_id] = inc
        return inc

    def add_action_item(self, incident_id: str, action: str) -> bool:
        inc = self._incidents.get(incident_id)
        if inc is None:
            return False
        inc.action_items.append(action)
        return True
