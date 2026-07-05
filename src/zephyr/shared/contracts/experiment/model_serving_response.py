# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.experiment.model_serving_response
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_model_serving_response | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:CTR-P1-005 ====

from dataclasses import dataclass

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/model_serving_response.py

CTR-P1-005: ModelServingResponse / 模型推理响应

跨层模型推理响应契约。D_ML_TRAIN ML Platform 返回推理结果给 D_SIGNAL/D_PORTFOLIO_CORE。

SSoT: cross_layer_contracts.yaml → CTR-P1-005
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class ModelServingResponse:
    request_id: str
    model_id: str
    prediction: float
    prediction_type: str
    confidence: float
    inference_ms: int
    idempotency_key: str
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-005 ====
