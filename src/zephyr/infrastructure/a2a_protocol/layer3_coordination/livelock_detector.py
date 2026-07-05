# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.livelock_detector
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
# [A_module] module_id=MOD-INF_livelock_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
