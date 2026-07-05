# [BLUEPRINT] MOD-AUTONOMY_PERM
# [MODULE] zephyr.autonomy_perm.red_blue_validator.defense_runner
# [DOMAIN] D_AUTONOMY_PERM
# [DEPENDENCIES] zephyr.security.adversarial_validation.defense_runner
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
"""Re-export wrapper: defense_runner has migrated to zephyr.security.adversarial_validation.defense_runner"""

from zephyr.security.adversarial_validation.defense_runner import *  # noqa: F403
