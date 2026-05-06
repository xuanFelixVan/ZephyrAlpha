

# ==== BEGIN CODGEN:CTR-P1-005 ====

from __future__ import annotations

from dataclasses import dataclass, field
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/model_serving_response.py

CTR-P1-005: ModelServingResponse / 模型推理响应

跨层模型推理响应契约。L11 ML Platform 返回推理结果给 L03/L05。

SSoT: cross-layer-contracts.yaml → CTR-P1-005
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



