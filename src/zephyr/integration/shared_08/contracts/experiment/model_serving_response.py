# [A_module] module_id=MOD-INT_model_serving_response | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-172 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md

# [MODULE] zephyr.integration.shared_08.contracts.experiment.model_serving_response

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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

跨层模型推理响应契约。L11 ML Platform 返回推理结果给 L03/L05。

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
