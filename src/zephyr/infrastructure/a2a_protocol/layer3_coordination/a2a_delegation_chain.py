# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_delegation_chain
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_a2a_delegation_chain | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""委托链"""


class A2ADelegationChain:
    MAX_DEPTH = 5

    def __init__(self):
        self._chains: dict = {}

    def delegate(self, task_id: str, from_agent: str, to_agent: str) -> dict:
        chain = self._chains.get(task_id, [])
        if len(chain) >= self.MAX_DEPTH:
            return {"task_id": task_id, "error": "max_depth_exceeded"}
        chain.append({"from": from_agent, "to": to_agent})
        self._chains[task_id] = chain
        return {"task_id": task_id, "depth": len(chain)}
