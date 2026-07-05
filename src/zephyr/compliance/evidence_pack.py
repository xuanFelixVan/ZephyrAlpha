# [BLUEPRINT] MOD-L10-001
# [MODULE] zephyr.compliance.evidence_pack
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.evidence_pack
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
"""Re-export wrapper: evidence_pack has migrated to zephyr.governance.evidence_pack"""

from zephyr.governance.evidence_pack import *  # noqa: F403
