# [BLUEPRINT] MOD-L10-001
# [MODULE] zephyr.compliance.merkle_hourly
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.governance.merkle_hourly
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
"""Re-export wrapper: merkle_hourly has migrated to zephyr.governance.merkle_hourly"""

from zephyr.governance.merkle_hourly import *  # noqa: F403
