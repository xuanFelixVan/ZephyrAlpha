# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.cascade_guard
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_cascade_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""级联守卫——防止失败在Agent间级联"""


class CascadeGuard:
    def __init__(self, threshold: int = 5):
        self.threshold = threshold
        self._failure_count: dict = {}

    def check(self, agent_id: str) -> bool:
        return self._failure_count.get(agent_id, 0) < self.threshold

    def record_failure(self, agent_id: str) -> int:
        self._failure_count[agent_id] = self._failure_count.get(agent_id, 0) + 1
        return self._failure_count[agent_id]
