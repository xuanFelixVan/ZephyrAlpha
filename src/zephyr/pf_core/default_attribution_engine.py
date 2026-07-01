# [BLUEPRINT] MOD-L05-001
# [MODULE] zephyr.pf_core.default_attribution_engine
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.default_attribution_engine
# [CONSUMERS] tests.integration.test_e2e_pipeline
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
"""Re-export wrapper: default_attribution_engine has migrated to zephyr.portfolio.core.default_attribution_engine"""

from zephyr.governance.default_attribution_engine import *  # noqa: F403
