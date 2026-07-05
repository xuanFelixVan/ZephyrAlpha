# [BLUEPRINT] MOD-AUTONOMY_PERM
# [MODULE] zephyr.autonomy_perm.red_blue_validator.attack_registry
# [DOMAIN] D_AUTONOMY_PERM
# [DEPENDENCIES] zephyr.security.adversarial_validation.attack_registry
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
"""Re-export wrapper: attack_registry has migrated to zephyr.security.adversarial_validation.attack_registry"""

from zephyr.security.adversarial_validation.attack_registry import *  # noqa: F403
