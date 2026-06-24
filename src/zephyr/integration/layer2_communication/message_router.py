# [BLUEPRINT] MOD-INTEGRATION-GATEWAY
# [MODULE] zephyr.integration.layer2_communication.message_router
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_schemas
# [CONSUMERS] zephyr.integration.layer2_communication.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# Re-export from authoritative location
from zephyr.shared.protocols.a2a.a2a_schemas import *  # noqa: F403
