# [BLUEPRINT] MOD-L06-001
# [MODULE] zephyr.ex_core.adapters.risk_validation_bridge
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.adapters.risk_validation_bridge
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
# [TTL] permanent
"""Re-export wrapper: risk_validation_bridge has migrated to zephyr.execution.core.adapters.risk_validation_bridge"""

from zephyr.governance.adapters.risk_validation_bridge import *  # noqa: F403
