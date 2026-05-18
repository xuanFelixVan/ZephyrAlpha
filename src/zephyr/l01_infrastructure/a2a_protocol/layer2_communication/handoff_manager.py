# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer2_communication.handoff_manager

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Handoff Manager — Agent 间任务交接"""

from typing import Dict, Any, Optional
from datetime import datetime


class HandoffRecord:
    def __init__(self, from_agent: str, to_agent: str, task_id: str, reason: str):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.task_id = task_id
        self.reason = reason
        self.timestamp = datetime.utcnow()
        self.acknowledged = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_agent,
            "to": self.to_agent,
            "task_id": self.task_id,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
        }


class HandoffManager:
    def __init__(self):
        self._history: list = []

    def handoff(self, from_agent: str, to_agent: str, task_id: str, reason: str) -> HandoffRecord:
        record = HandoffRecord(from_agent, to_agent, task_id, reason)
        self._history.append(record)
        return record

    def acknowledge(self, to_agent: str, task_id: str) -> bool:
        for record in reversed(self._history):
            if record.to_agent == to_agent and record.task_id == task_id:
                record.acknowledged = True
                return True
        return False

    def get_active_handoffs(self) -> list:
        return [r for r in self._history if not r.acknowledged]
