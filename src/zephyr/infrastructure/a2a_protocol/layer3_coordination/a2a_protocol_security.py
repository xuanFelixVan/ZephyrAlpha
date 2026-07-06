# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_security
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_protocol_security | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A协议安全"""


class A2AProtocolSecurity:
    def __init__(self):
        self._blocked_agents: set = set()

    def block(self, agent_id: str, reason: str) -> dict:
        self._blocked_agents.add(agent_id)
        return {"agent": agent_id, "blocked": True, "reason": reason}

    def is_blocked(self, agent_id: str) -> bool:
        return agent_id in self._blocked_agents
