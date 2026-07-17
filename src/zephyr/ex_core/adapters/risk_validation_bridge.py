# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.adapters.risk_validation_bridge
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.adapters.risk_validation_bridge
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
"""Re-export wrapper: risk_validation_bridge 真源在 zephyr.governance.adapters.risk_validation_bridge"""

from zephyr.governance.adapters.risk_validation_bridge import *  # noqa: F403
