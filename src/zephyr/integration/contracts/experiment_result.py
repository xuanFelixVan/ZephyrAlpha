# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.contracts.experiment_result
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.experiment_result
# [CONSUMERS] zephyr.simulation.pipeline_base_from_resear; zephyr.simulation.pipeline_base
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
from zephyr.integration.shared_08.contracts.experiment_result import ExperimentResult

__all__ = ["ExperimentResult"]
