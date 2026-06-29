# [BLUEPRINT] MOD-OPS
# [MODULE] zephyr.ops.auto_bootstrap
# [DOMAIN] D_OPS
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
from zephyr.infrastructure.system_telemetry.auto_bootstrap import *  # noqa: F403
