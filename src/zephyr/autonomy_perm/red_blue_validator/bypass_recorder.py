# [BLUEPRINT] MOD-AUTONOMY_PERM
# [MODULE] zephyr.autonomy_perm.red_blue_validator.bypass_recorder
# [DOMAIN] D_AUTONOMY_PERM
# [DEPENDENCIES] zephyr.security.adversarial_validation.bypass_recorder
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
"""Re-export wrapper: bypass_recorder has migrated to zephyr.security.adversarial_validation.bypass_recorder"""

from zephyr.security.adversarial_validation.bypass_recorder import *  # noqa: F403
