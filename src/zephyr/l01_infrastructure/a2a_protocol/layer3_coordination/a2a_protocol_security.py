# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_security

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A协议安全"""

class A2AProtocolSecurity:
    def __init__(self):
        self._blocked_agents: set = set()

    def block(self, agent_id: str, reason: str) -> dict:
        self._blocked_agents.add(agent_id)
        return {"agent": agent_id, "blocked": True, "reason": reason}

    def is_blocked(self, agent_id: str) -> bool:
        return agent_id in self._blocked_agents
