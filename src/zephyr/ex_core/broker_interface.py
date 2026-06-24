# [BLUEPRINT] MOD-EX_CORE
# [MODULE] zephyr.ex_core.broker_interface
# [DOMAIN] D-EX_CORE
# [DEPENDENCIES] zephyr.governance.broker_interface
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
"""Re-export wrapper: broker_interface has migrated to zephyr.execution.core.broker_interface"""

from zephyr.governance.broker_interface import *  # noqa: F403
