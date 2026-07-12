# [BLUEPRINT] MOD-L10-001
# [MODULE] zephyr.compliance.financial_compliance
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.governance.financial_governance.financial_compliance
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
"""Re-export wrapper: financial_compliance has migrated to zephyr.governance.financial_compliance"""

from zephyr.governance.financial_governance.financial_compliance import *  # noqa: F403
