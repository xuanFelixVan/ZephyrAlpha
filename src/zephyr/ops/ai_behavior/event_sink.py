# [BLUEPRINT] MOD-OPS
# [MODULE] zephyr.ops.ai_behavior.event_sink
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
from zephyr.infrastructure.system_telemetry.ai_behavior.event_sink import *  # noqa: F403
