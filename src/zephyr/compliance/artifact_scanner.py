# [BLUEPRINT] MOD-COMPLIANCE
# [MODULE] zephyr.compliance.artifact_scanner
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.governance.drift_detection.artifact_scanner
# [CONSUMERS] zephyr.compliance.__init__
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
"""Re-export wrapper: artifact_scanner has migrated to zephyr.governance.drift_detection.artifact_scanner"""

from zephyr.governance.drift_detection.artifact_scanner import *  # noqa: F403
