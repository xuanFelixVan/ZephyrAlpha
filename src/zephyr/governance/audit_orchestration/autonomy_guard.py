# [A_module] module_id=MOD-GOV_autonomy_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.governance.audit_orchestration.autonomy_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Owner 缺位分级自治（CT-AUTONOMY）——Owner离线→自动降级→最小安全运行。"""

from __future__ import annotations

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
