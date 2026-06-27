# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.lifecycle.task_lifecycle_manager
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# 代理模块：将 zephyr.shared.lifecycle.task_lifecycle_manager 重定向到 zephyr.infrastructure.lifecycle.task_lifecycle_manager
from zephyr.infrastructure.lifecycle.task_lifecycle_manager import (
    GateID,
    GateResult,
    LifecycleState,
    TaskLifecycleManager,
    TaskStatus,
)

__all__ = ["GateID", "GateResult", "LifecycleState", "TaskLifecycleManager", "TaskStatus"]
