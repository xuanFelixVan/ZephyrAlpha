# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model_capability_exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation.inference_base
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.ml_train.trainer_base; zephyr.ml_train.inference_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-036 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# MIGRATED: SSoT moved to zephyr.ml_train.trainer_base and zephyr.ml_train.inference_base
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_intelligence/algo_flow/inference_base.yaml
"""

from zephyr.ml_train.inference_base import (
    InferenceEngineBase,
)
from zephyr.ml_train.trainer_base import (
    ModelMetadata,
    ModelRegistry,
    ModelTrainerBase,
)

__all__ = [
    "InferenceEngineBase",
    "ModelMetadata",
    "ModelRegistry",
    "ModelTrainerBase",
]
