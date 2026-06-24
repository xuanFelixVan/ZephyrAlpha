# [BLUEPRINT] MOD-PF_CORE
# [MODULE] zephyr.pf_core.performance_attribution_report
# [DOMAIN] D-PF_CORE
# [DEPENDENCIES] zephyr.governance.performance_attribution_report
# [CONSUMERS] tests.test_post_trade_analytics
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""Re-export wrapper: performance_attribution_report has migrated to zephyr.portfolio.core.performance_attribution_report"""

from zephyr.governance.performance_attribution_report import *  # noqa: F403
