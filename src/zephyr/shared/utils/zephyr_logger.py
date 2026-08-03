# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.zephyr_logger
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.logging
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from zephyr.shared.utils.logging import (
    LogLevel,
    TraceContext,  # [DEPRECATED] 兼容别名，新代码用 trace_context
    ZephyrLogger,
    configure_root_logger,
    get_logger,
    module_id_var,
    session_id_var,
    trace_context,
    trace_id_var,
)

__all__ = [
    "LogLevel",
    "TraceContext",
    "ZephyrLogger",
    "configure_root_logger",
    "get_logger",
    "module_id_var",
    "session_id_var",
    "trace_context",
    "trace_id_var",
]
