# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_idle_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A 空闲守卫"""

class A2AIdleGuard:
    def __init__(self, idle_timeout: float = 300):
        self.idle_timeout = idle_timeout

    def check_idle(self, agent_id: str, last_active: float, now: float) -> bool:
        return (now - last_active) > self.idle_timeout
