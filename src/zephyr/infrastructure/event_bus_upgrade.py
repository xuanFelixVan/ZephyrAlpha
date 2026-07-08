# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.event_bus_upgrade
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.integration.shared.events.upgrade_strategy; zephyr.shared.events.upgrade_strategy
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_event_bus_upgrade | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
DEPRECATED: 此文件已废弃。
请使用 zephyr.shared.upgrade_strategy 替代。

本文件保留为 compat shim，将在 Phase 4 物理删除。
"""

# SRC-0037: 版本分叉->独立命名 — compat shim

import warnings

from zephyr.integration.shared.events.upgrade_strategy import *  # noqa: F403
from zephyr.shared.events.upgrade_strategy import EventBusUpgrade as _SharedEventBusUpgrade
from zephyr.shared.events.upgrade_strategy import UpgradePlan as _SharedUpgradePlan

warnings.warn(
    "zephyr.infrastructure.event_bus_upgrade is deprecated; "
    "use zephyr.integration.shared.events.upgrade_strategy instead.",
    DeprecationWarning,
    stacklevel=2,
)


def validate_upgrade_from_shared(version_from: str = "v1.0.0", version_to: str = "v2.0.0") -> _SharedUpgradePlan:
    upgrader = _SharedEventBusUpgrade()
    return upgrader.generate_upgrade_plan(version_from=version_from, version_to=version_to)
