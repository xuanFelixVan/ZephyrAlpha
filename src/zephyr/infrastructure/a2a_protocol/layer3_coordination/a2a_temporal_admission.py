# [A_module] module_id=MOD-INF_a2a_temporal_admission | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_temporal_admission

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""时序准入控制"""


class A2ATemporalAdmission:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._active: set = set()

    def admit(self, agent_id: str) -> bool:
        return len(self._active) < self.max_concurrent

    def enter(self, agent_id: str) -> None:
        self._active.add(agent_id)

    def leave(self, agent_id: str) -> None:
        self._active.discard(agent_id)
