# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared.events.upgrade_strategy
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.events.upgrade_strategy
# [CONSUMERS] tests/infrastructure/test_cross_blueprint_e2e.py; tests/infrastructure/test_capacity_runtime_red_blue.py; zephyr.infrastructure.event_bus_upgrade
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""EventBus 升级策略引擎 — backward-compat re-export shim。

AI-15 审计治本（2026-08-17）：本文件原为 zephyr.shared.events.upgrade_strategy
的复制漂移副本（execute_upgrade 实现分叉）。唯一真源已收敛至
zephyr.shared.events.upgrade_strategy，本文件 re-export 保持向后兼容。
禁止在本文件重新落地实现（D-D-05）。
"""

from zephyr.shared.events.upgrade_strategy import (
    EventBusUpgrade,
    UpgradePlan,
    UpgradeStatus,
    UpgradeStep,
)

__all__ = [
    "EventBusUpgrade",
    "UpgradePlan",
    "UpgradeStatus",
    "UpgradeStep",
]
