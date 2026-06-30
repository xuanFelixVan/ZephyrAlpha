# [BLUEPRINT] MOD-PF_CORE
# [MODULE] zephyr.pf_core.risk_limits
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.risk_limits
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
"""Re-export wrapper: risk_limits has migrated to zephyr.portfolio.core.risk_limits"""

from zephyr.governance.trading_contracts.risk.risk_limits import *  # noqa: F403
