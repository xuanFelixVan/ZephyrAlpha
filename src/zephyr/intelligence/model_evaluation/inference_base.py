# [A_module] module_id=MOD-RSC_inference_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation.inference_base
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]

# MIGRATED: SSoT moved to zephyr.ml_train.trainer_base and zephyr.ml_train.inference_base
from zephyr.ml_train.trainer_base import (  # noqa: F401
    ModelMetadata,
    ModelTrainerBase,
    ModelRegistry,
)
from zephyr.ml_train.inference_base import (  # noqa: F401
    InferenceEngineBase,
)

__all__ = [
    "ModelMetadata",
    "ModelTrainerBase",
    "ModelRegistry",
    "InferenceEngineBase",
]
