# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.cascade_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
