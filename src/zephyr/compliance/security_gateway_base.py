# [BLUEPRINT] MOD-L10-001
# [MODULE] zephyr.compliance.security_gateway_base
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.security_governance.security_gateway_base
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
"""Re-export wrapper: security_gateway_base has migrated to zephyr.governance.security_governance.security_gateway_base"""

from zephyr.governance.security_governance.security_gateway_base import *  # noqa: F403
