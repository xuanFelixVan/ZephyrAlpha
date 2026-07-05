# ==== BEGIN CODGEN:CTR-P1-005 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.model_serving_response
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] frozen dataclass; SSoT=cross_layer_contracts.yaml; DO NOT EDIT (codegen)
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from dataclasses import dataclass, field
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/model_serving_response.py

CTR-P1-005: ModelServingResponse / 模型推理响应

跨层模型推理响应契约。D_ML_TRAIN ML Platform 返回推理结果给 D_SIGNAL/D_PORTFOLIO_CORE。

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
    inference_ms: int
    model_id: str
    prediction: float
    prediction_type: str
    request_id: str
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-005 ====











