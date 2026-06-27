# [BLUEPRINT] MOD-COMPLIANCE
# [MODULE] zephyr.compliance.default_security_gateway
# [DOMAIN] D-COMPLIANCE
# [DEPENDENCIES] zephyr.governance.default_security_gateway
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
# [TTL] task_bound
"""Re-export wrapper: default_security_gateway has migrated to zephyr.governance.default_security_gateway"""

from zephyr.governance.default_security_gateway import *  # noqa: F403
