# [BLUEPRINT] MOD-L05-001
# [MODULE] zephyr.pf_core.risk_limits
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.trading_contracts.risk.risk_limits
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
"""Re-export wrapper: risk_limits canonical at zephyr.governance.trading_contracts.risk.risk_limits"""

from zephyr.governance.trading_contracts.risk.risk_limits import *  # noqa: F403
