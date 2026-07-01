# [BLUEPRINT] MOD-L05-001
# [MODULE] zephyr.pf_core.analytics_base
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.reporting.analytics_base
# [CONSUMERS] tests.test_post_trade_analytics; tests.unit.test_analytics_base_contract
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""Re-export wrapper: analytics_base has migrated to zephyr.reporting.analytics_base"""

from zephyr.reporting.analytics_base import *  # noqa: F403
