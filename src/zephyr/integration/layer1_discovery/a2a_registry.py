# [BLUEPRINT] MOD-INTEGRATION-GATEWAY
# [MODULE] zephyr.integration.layer1_discovery.a2a_registry
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_registry
# [CONSUMERS] zephyr.integration.layer1_discovery.__init__
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
from zephyr.shared.protocols.a2a.a2a_registry import *  # noqa: F403
