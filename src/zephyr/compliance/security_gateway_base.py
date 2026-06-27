# [BLUEPRINT] MOD-COMPLIANCE
# [MODULE] zephyr.compliance.security_gateway_base
# [DOMAIN] D-COMPLIANCE
# [DEPENDENCIES] zephyr.governance.security_gateway_base
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
"""Re-export wrapper: security_gateway_base has migrated to zephyr.governance.security_gateway_base"""

from zephyr.governance.security_gateway_base import *  # noqa: F403
