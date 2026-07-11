# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.lifecycle.rolling_upgrade
# [DOMAIN] D_ORCHESTRATOR
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
# [A_module] module_id=MOD-ORC_rolling_upgrade | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""零停机滚动升级（CT-DEPLOY）——graceful shutdown+流量摘除+health check wait。"""


class RollingUpgradeManager:
    def __init__(self):
        self._upgrading = False

    def start_upgrade(self) -> None:
        self._upgrading = True

    def is_draining(self) -> bool:
        return self._upgrading

    def complete_upgrade(self) -> None:
        self._upgrading = False
