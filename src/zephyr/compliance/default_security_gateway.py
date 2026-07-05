# [BLUEPRINT] MOD-L10-001
# [MODULE] zephyr.compliance.default_security_gateway
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.security_governance.default_security_gateway
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
"""Re-export wrapper: default_security_gateway has migrated to zephyr.governance.security_governance.default_security_gateway"""

from zephyr.governance.security_governance.default_security_gateway import *  # noqa: F403
