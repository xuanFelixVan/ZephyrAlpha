# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation.implementations.default_inference_engine
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.ml_train.implementations.default_inference_engine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 单一真源=zephyr.ml_train.implementations.default_inference_engine; 本模块仅为兼容重导出 shim
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-036 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""D_INTELLIGENCE — Default Inference Engine（兼容 shim）

MIGRATED: SSoT 已迁移至 zephyr.ml_train.implementations.default_inference_engine
（与同包 inference_base.py 的 MIGRATED 裁定一致——D_ML_TRAIN 为训练/推理基类唯一真源）。

治本留痕（AI-AUDIT07, 2026-08-17）：本模块原为 ml_train 版的过期完整副本，
其 load_model() 内 ModelMetadata 构造使用错误字段名（version/input_features/output_type），
调用即 TypeError——副本自迁移日起即坏死的双真源。收敛为 shim 重导出，
保持既有 import 路径（tests/trading/pipeline、tests/governance/trading、
scripts/construction/demo_e2e_pipeline.py 等消费者）零改动。
"""

from __future__ import annotations

# MIGRATED: SSoT moved to zephyr.ml_train.implementations.default_inference_engine
from zephyr.ml_train.implementations.default_inference_engine import (
    DefaultInferenceEngine,
)

__all__ = ["DefaultInferenceEngine"]
