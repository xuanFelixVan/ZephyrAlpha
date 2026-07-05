# [BLUEPRINT] MOD-L05-001
# [MODULE] zephyr.pf_core.strategy_base
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.strategy_base
# [CONSUMERS] tests.test_portfolio_construction
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Re-export wrapper: strategy_base has migrated to zephyr.portfolio.core.strategy_base"""

from zephyr.governance.strategies.strategy_base import *  # noqa: F403
