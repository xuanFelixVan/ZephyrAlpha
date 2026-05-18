# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.livelock_detector

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""P2: 活锁检测器"""

class LivelockDetector:
    def __init__(self, cycle_limit: int = 10):
        self._state_history: dict = {}
        self.cycle_limit = cycle_limit

    def check_cycle(self, agent_id: str, state_hash: str) -> bool:
        history = self._state_history.setdefault(agent_id, [])
        count = history.count(state_hash)
        return count >= self.cycle_limit

    def record_state(self, agent_id: str, state_hash: str) -> None:
        self._state_history.setdefault(agent_id, []).append(state_hash)
