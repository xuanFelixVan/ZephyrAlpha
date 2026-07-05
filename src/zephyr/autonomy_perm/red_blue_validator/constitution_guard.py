# [BLUEPRINT] MOD-AUTONOMY_PERM
# [MODULE] zephyr.autonomy_perm.red_blue_validator.constitution_guard
# [DOMAIN] D_AUTONOMY_PERM
# [DEPENDENCIES] zephyr.security.adversarial_validation.constitution_guard
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
"""Re-export wrapper: constitution_guard has migrated to zephyr.security.adversarial_validation.constitution_guard"""

from zephyr.security.adversarial_validation.constitution_guard import *  # noqa: F403
