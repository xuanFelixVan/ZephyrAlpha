# [BLUEPRINT] MOD-L05-001
# [MODULE] zephyr.pf_core.default_tca_engine
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.default_tca_engine
# [CONSUMERS] tests.integration.test_e2e_pipeline; tests.integration.test_phase_g_perf; tests.integration.test_phase_e_main_flow
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
"""Re-export wrapper: default_tca_engine has migrated to zephyr.portfolio.core.default_tca_engine"""

from zephyr.governance.default_tca_engine import *  # noqa: F403
