# [BLUEPRINT] MOD-L06-001
# [MODULE] zephyr.ex_core.broker_interface
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.trading_contracts.broker_interface
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
"""Re-export wrapper: broker_interface has migrated to zephyr.execution.core.broker_interface"""

from zephyr.governance.trading_contracts.broker_interface import *  # noqa: F403
