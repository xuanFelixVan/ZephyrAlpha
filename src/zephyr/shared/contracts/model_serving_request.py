# ==== BEGIN CODGEN:CTR-P1-004 ====
from dataclasses import dataclass, field

from typing import Dict
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-06-24"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/model_serving_request.py

CTR-P1-004: ModelServingRequest / 模型推理请求

跨层模型推理请求契约。L11 ML Platform 提供推理服务，L03/L05 消费。

SSoT: cross_layer_contracts.yaml -> CTR-P1-004
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class ModelServingRequest:
    idempotency_key: str
    model_id: str
    model_version: str
    request_id: str
    input_features: Dict[str, float] = field(default_factory=dict)

# ==== END CODGEN:CTR-P1-004 ====
