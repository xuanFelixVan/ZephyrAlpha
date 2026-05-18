# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_metrics

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A 指标收集"""

class A2AMetrics:
    def __init__(self):
        self._metrics: dict = {}

    def record(self, name: str, value: float, tags: dict = None) -> None:
        self._metrics[name] = {"value": value, "tags": tags or {}}

    def get(self, name: str) -> dict:
        return self._metrics.get(name, {})
