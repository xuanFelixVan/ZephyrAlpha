# [BLUEPRINT] MOD-INF-002 | 03_modules/l01_infrastructure/runtime-integration/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.event_bus_upgrade

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
DEPRECATED: 此文件已废弃。
请使用 zephyr.shared.upgrade_strategy 替代。

本文件保留为 compat shim，将在 Phase 4 物理删除。
"""
# SRC-0037: 版本分叉→独立命名 — compat shim

import warnings

from zephyr.shared.events.upgrade_strategy import *  # noqa: F403

warnings.warn(
    "zephyr.l01_infrastructure.event_bus_upgrade is deprecated; " "use zephyr.shared.events.upgrade_strategy instead.",
    DeprecationWarning,
    stacklevel=2,
)
