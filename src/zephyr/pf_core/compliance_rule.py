# [BLUEPRINT] MOD-L05-001
# [MODULE] zephyr.pf_core.compliance_rule
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.compliance_rule
# [CONSUMERS] tests.integration.test_phase_f_layers
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
"""Re-export wrapper: compliance_rule has migrated to zephyr.portfolio.core.compliance_rule"""

from zephyr.gov_enforcement.rule_enforcement.compliance_rule import *  # noqa: F403
