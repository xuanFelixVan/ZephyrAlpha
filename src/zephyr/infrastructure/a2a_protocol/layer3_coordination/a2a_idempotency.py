# [A_module] module_id=MOD-INF_a2a_idempotency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_idempotency

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A 幂等性保证"""


class A2AIdempotency:
    def __init__(self):
        self._history: set = set()

    def is_duplicate(self, task_id: str, input_hash: str) -> bool:
        key = f"{task_id}:{input_hash}"
        if key in self._history:
            return True
        self._history.add(key)
        return False
