# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_delegation_chain

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
