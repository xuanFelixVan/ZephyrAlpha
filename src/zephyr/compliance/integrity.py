# [BLUEPRINT] MOD-COMPLIANCE
# [MODULE] zephyr.compliance.integrity
# [DOMAIN] D-COMPLIANCE
# [DEPENDENCIES] zephyr.governance.integrity
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
"""Re-export wrapper: integrity has migrated to zephyr.governance.integrity"""

from zephyr.governance.integrity import *  # noqa: F403
