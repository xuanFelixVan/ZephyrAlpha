# [BLUEPRINT] MOD-OPS
# [MODULE] zephyr.ops.span_stub
# [DOMAIN] D-OPS
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# Re-export from authoritative location
from zephyr.infrastructure.system_telemetry.traces.span_stub import *  # noqa: F403
