# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.deadlock_guard
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
# [A_module] module_id=MOD-INF_deadlock_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""P2: 死锁守卫"""


class DeadlockGuard:
    def __init__(self):
        self._locks: dict = {}

    def try_acquire(self, resource: str, holder: str) -> bool:
        if resource in self._locks:
            return False
        self._locks[resource] = holder
        return True

    def release(self, resource: str, holder: str) -> bool:
        if self._locks.get(resource) == holder:
            del self._locks[resource]
            return True
        return False
