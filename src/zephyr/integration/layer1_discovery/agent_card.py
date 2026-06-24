# [BLUEPRINT] MOD-INTEGRATION-GATEWAY
# [MODULE] zephyr.integration.layer1_discovery.agent_card
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_registry
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
# Re-export from authoritative location
from zephyr.shared.protocols.a2a.a2a_registry import *  # noqa: F403
