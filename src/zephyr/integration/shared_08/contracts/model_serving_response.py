# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.shared_08.contracts.model_serving_response
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] zephyr.integration.contracts.model_serving_response; tests.integration.test_phase_f_layers
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# ==== BEGIN CODGEN:CTR-P1-005 ====
from dataclasses import dataclass

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/model_serving_response.py

CTR-P1-005: ModelServingResponse / 模型推理响应

跨层模型推理响应契约。L11 ML Platform 返回推理结果给 L03/L05。

SSoT: cross_layer_contracts.yaml -> CTR-P1-005
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class ModelServingResponse:
    confidence: float
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    inference_ms: int
    model_id: str
    prediction: float
    prediction_type: str
    request_id: str
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-005 ====
