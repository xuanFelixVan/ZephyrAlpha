# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
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


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: inference_base.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 InferenceEngineBase, ModelMetadata, ModelRegistry, ModelTrainerBase（共 4 符号）
#   desc: __init__ import L0；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: InferenceEngineBase, ModelMetadata, ModelRegistry, ModelTrainerBase
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
