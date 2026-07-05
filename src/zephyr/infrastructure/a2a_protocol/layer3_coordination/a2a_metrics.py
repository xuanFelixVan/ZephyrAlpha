# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_metrics
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
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
# [A_module] module_id=MOD-INF_a2a_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 指标收集"""


class A2AMetrics:
    def __init__(self):
        self._metrics: dict = {}

    def record(self, name: str, value: float, tags: dict = None) -> None:
        self._metrics[name] = {"value": value, "tags": tags or {}}

    def get(self, name: str) -> dict:
        return self._metrics.get(name, {})
