# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.lifecycle.scope_guard
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
# 代理模块：将 zephyr.shared.lifecycle.scope_guard 重定向到 zephyr.infrastructure.lifecycle.scope_guard
from zephyr.infrastructure.lifecycle.scope_guard import (
    ScopeDrift,
    ScopeGuard,
    ScopeGuardConfig,
)

__all__ = ["ScopeDrift", "ScopeGuard", "ScopeGuardConfig"]
