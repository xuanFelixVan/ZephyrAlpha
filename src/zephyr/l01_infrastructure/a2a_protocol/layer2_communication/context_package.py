# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer2_communication.context_package

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Context Package — A2A 上下文包"""

from typing import Dict, Any, Optional
from datetime import datetime


class ContextPackage:
    def __init__(self, task_id: str, source_agent: str):
        self.task_id = task_id
        self.source_agent = source_agent
        self.created_at = datetime.utcnow()
        self.blueprints: Dict[str, str] = {}
        self.decisions: list = []
        self.session_state: Dict[str, Any] = {}
        self.locks_held: list = []

    def add_blueprint(self, name: str, content: str):
        self.blueprints[name] = content

    def add_decision(self, decision_id: str, data: Dict[str, Any]):
        self.decisions.append({"id": decision_id, "data": data})

    def set_session_state(self, state: Dict[str, Any]):
        self.session_state = state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "source_agent": self.source_agent,
            "created_at": self.created_at.isoformat(),
            "blueprint_count": len(self.blueprints),
            "decision_count": len(self.decisions),
            "session_state_keys": list(self.session_state.keys()),
        }
