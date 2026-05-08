"""A2A协议安全"""

class A2AProtocolSecurity:
    def __init__(self):
        self._blocked_agents: set = set()

    def block(self, agent_id: str, reason: str) -> dict:
        self._blocked_agents.add(agent_id)
        return {"agent": agent_id, "blocked": True, "reason": reason}

    def is_blocked(self, agent_id: str) -> bool:
        return agent_id in self._blocked_agents
