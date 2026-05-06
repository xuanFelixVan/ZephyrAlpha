

# ==== BEGIN CODGEN:CTR-P1-004 ====

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/model_serving_request.py

CTR-P1-004: ModelServingRequest / 模型推理请求

跨层模型推理请求契约。L11 ML Platform 提供推理服务，L03/L05 消费。

SSoT: cross-layer-contracts.yaml → CTR-P1-004
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class ModelServingRequest:
    model_id: str
    model_version: str
    request_id: str
    idempotency_key: str
    input_features: Dict[str, float] = field(default_factory=dict)
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-004 ====



