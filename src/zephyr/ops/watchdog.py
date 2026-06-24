# [BLUEPRINT] MOD-OPS
# [MODULE] zephyr.ops.watchdog
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
# Re-export from authoritative location
from zephyr.infrastructure.system_telemetry.watchdog import *  # noqa: F403
