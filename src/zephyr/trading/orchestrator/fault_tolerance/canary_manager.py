# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.fault_tolerance.canary_manager
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_canary_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""金丝雀发布管理器（CT-CANARY）——权重分流+指标对比+自动回滚。"""


class CanaryManager:
    def __init__(self):
        self._canary_weight: float = 0.1

    def set_weight(self, weight: float) -> None:
        self._canary_weight = min(1.0, max(0.0, weight))

    def should_rollback(self, error_rate: float, baseline: float) -> bool:
        return error_rate > baseline * 2.0

    def promote(self) -> None:
        self._canary_weight = 1.0
