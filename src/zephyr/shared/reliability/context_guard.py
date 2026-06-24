# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.reliability.context_guard
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
# 代理模块：将 zephyr.shared.reliability.context_guard 重定向到 zephyr.infrastructure.reliability.context_guard
from zephyr.infrastructure.reliability.context_guard import (
    AccessCheck,
    ContextGuard,
    ContextGuardResult,
)

__all__ = ["AccessCheck", "ContextGuard", "ContextGuardResult"]
