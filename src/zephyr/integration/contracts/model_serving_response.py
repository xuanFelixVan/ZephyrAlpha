# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.contracts.model_serving_response
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.contracts.model_serving_response
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
# [TTL] task_bound
from zephyr.shared.contracts.model_serving_response import ModelServingResponse

__all__ = ["ModelServingResponse"]
