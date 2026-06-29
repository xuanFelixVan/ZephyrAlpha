# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.integration.governance.phase_hold
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_protocol
# [CONSUMERS] zephyr.integration.governance
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
# Re-export from authoritative location
from zephyr.shared.protocols.a2a.a2a_protocol import *  # noqa: F403
