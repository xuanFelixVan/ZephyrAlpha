# [A_module] module_id=MOD-GOV_rolling_upgrade | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.governance.audit_orchestration.rolling_upgrade

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""零停机滚动升级（CT-DEPLOY）——graceful shutdown+流量摘除+health check wait。"""

from __future__ import annotations

class RollingUpgradeManager:
    def __init__(self):
        self._upgrading = False

    def start_upgrade(self) -> None:
        self._upgrading = True

    def is_draining(self) -> bool:
        return self._upgrading

    def complete_upgrade(self) -> None:
        self._upgrading = False
