# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.adapters.simulation_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.adapters.simulation_broker
# [CONSUMERS] tests.integration.test_e2e_pipeline; tests.integration.test_phase_g_perf; tests.integration.test_phase_e_main_flow; tests.unit.test_execution_engine_unit
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
