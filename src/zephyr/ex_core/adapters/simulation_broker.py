# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.adapters.simulation_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.adapters.simulation_broker
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Re-export wrapper: simulation_broker 真源在 zephyr.governance.adapters.simulation_broker"""

from zephyr.governance.adapters.simulation_broker import *  # noqa: F403
