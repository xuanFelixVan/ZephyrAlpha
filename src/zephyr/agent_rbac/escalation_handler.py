# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.escalation_handler

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Escalation Handler — 多级警报与自动降权

MOD-INF-018 §2.17  D-018-25
"""

import time


class EscalationHandler:
    LEVELS = ["P0_OWNER", "P1_URGENT", "P2_HIGH", "P3_MEDIUM", "P4_LOW"]

    def __init__(self) -> None:
        self._escalated: list[dict] = []
        self._cooldowns: dict[str, float] = {}

    def escalate(self, agent_id: str, level: str, reason: str, detail: str = "") -> str:
        event = {
            "agent_id": agent_id,
            "level": level,
            "reason": reason,
            "detail": detail,
            "timestamp": time.time(),
        }
        self._escalated.append(event)

        responses = {
            "P0_OWNER": "P0_TRIGGERED_NOTIFY_OWNER",
            "P1_URGENT": "ESCALATED_AUDIT_ONLY",
            "P2_HIGH": "ESCALATED_AUDIT_ONLY",
            "P3_MEDIUM": "LOGGED",
            "P4_LOW": "LOGGED",
        }
        return responses.get(level, "LOGGED")

    def should_throttle(self, agent_id: str, window: float = 60.0, max_count: int = 5) -> bool:
        cutoff = time.time() - window
        count = sum(1 for e in self._escalated if e["agent_id"] == agent_id and e["timestamp"] > cutoff)
        return count >= max_count

    def get_recent(self, agent_id: str, limit: int = 10) -> list[dict]:
        mine = [e for e in self._escalated if e["agent_id"] == agent_id]
        mine.sort(key=lambda e: e["timestamp"], reverse=True)
        return mine[:limit]

    def reset_agent(self, agent_id: str) -> None:
        self._escalated = [e for e in self._escalated if e["agent_id"] != agent_id]
        self._cooldowns.pop(agent_id, None)
