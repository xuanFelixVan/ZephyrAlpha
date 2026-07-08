# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.governance.autonomy_guard
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_autonomy_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Owner 缺位分级自治（CT-AUTONOMY）——Owner离线->自动降级->最小安全运行。"""


class AutonomyGuard:
    AUTONOMY_LEVELS: dict[str, list[str]] = {
        "level1": ["health_check", "metrics_collect", "dlq_replay"],
        "level2": ["auto_mitigate_p2", "restart_unhealthy"],
        "level3": ["rollback_deploy", "repartition_data"],
    }

    def get_allowed_actions(self, level: str) -> list[str]:
        return self.AUTONOMY_LEVELS.get(level, [])

    def can_autonomously(self, action: str, level: str) -> bool:
        return action in self.get_allowed_actions(level)
