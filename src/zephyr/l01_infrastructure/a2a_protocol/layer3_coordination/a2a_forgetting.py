# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_forgetting

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A 遗忘机制"""

class A2AForgetting:
    def __init__(self, max_memory: int = 100):
        self._memory: list = []
        self.max_memory = max_memory

    def remember(self, item: dict) -> None:
        self._memory.append(item)
        self._forget()

    def _forget(self) -> None:
        while len(self._memory) > self.max_memory:
            self._memory.pop(0)
