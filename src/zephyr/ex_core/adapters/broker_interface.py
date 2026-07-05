# [BLUEPRINT] MOD-L06-001
# [MODULE] zephyr.ex_core.adapters.broker_interface
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.trading_contracts.broker_interface
# [CONSUMERS] tests.test_trade_execution; tests.integration.test_e2e_pipeline
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""Re-export wrapper: broker_interface has migrated to zephyr.execution.core.adapters.broker_interface"""

from zephyr.governance.trading_contracts.broker_interface import *  # noqa: F403
