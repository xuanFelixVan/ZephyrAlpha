# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_consent
# [DOMAIN] D_INFRA_A2A
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
# [A_module] module_id=MOD-INF_a2a_consent | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""P2: Agent同意管理"""


class A2AConsent:
    def __init__(self):
        self._consents: dict = {}

    def grant(self, agent_id: str, scope: str, granted_by: str) -> dict:
        self._consents.setdefault(agent_id, {})
        self._consents[agent_id][scope] = {"granted": True, "by": granted_by}
        return {"agent": agent_id, "scope": scope, "consent": True}

    def revoke(self, agent_id: str, scope: str) -> dict:
        if agent_id in self._consents:
            self._consents[agent_id].pop(scope, None)
        return {"agent": agent_id, "scope": scope, "revoked": True}
