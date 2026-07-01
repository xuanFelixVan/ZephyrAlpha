# [BLUEPRINT] MOD-COMPLIANCE
# [MODULE] zephyr.compliance.compliance_manager
# [DOMAIN] D_COMPLIANCE
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
# [TTL] task_bound
"""Re-export wrapper: compliance_manager has migrated to zephyr.governance.compliance_gate_a6.compliance_manager"""

from zephyr.governance.compliance_gate_a6.compliance_manager import *  # noqa: F403
