# [BLUEPRINT] MOD-L10-001
# [MODULE] zephyr.compliance.compliance_manager
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.compliance_gate_a6.compliance_manager
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
"""Re-export wrapper: compliance_manager has migrated to zephyr.governance.compliance_gate_a6.compliance_manager"""

from zephyr.governance.compliance_gate_a6.compliance_manager import *  # noqa: F403
