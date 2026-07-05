# [BLUEPRINT] MOD-AUTONOMY_PERM
# [MODULE] zephyr.autonomy_perm.red_blue_validator.convergence_checker
# [DOMAIN] D_AUTONOMY_PERM
# [DEPENDENCIES] zephyr.security.adversarial_validation.convergence_checker
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
"""Re-export wrapper: convergence_checker has migrated to zephyr.security.adversarial_validation.convergence_checker"""

from zephyr.security.adversarial_validation.convergence_checker import *  # noqa: F403
