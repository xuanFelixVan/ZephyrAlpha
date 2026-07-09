# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.lifecycle.incident_postmortem
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_incident_postmortem | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""事件复盘管理器（CT-INCIDENT）——incident记录+timeline+action_items+postmortem。"""

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
