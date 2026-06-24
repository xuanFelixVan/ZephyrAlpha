# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.contracts.model_serving_response
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.model_serving_response
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
from zephyr.integration.shared_08.contracts.model_serving_response import ModelServingResponse

__all__ = ["ModelServingResponse"]
