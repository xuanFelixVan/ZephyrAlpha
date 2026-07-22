# ==== BEGIN CODGEN:CTR-P1-004 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.model_serving_request
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

from typing import Dict
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/model_serving_request.py

CTR-P1-004: ModelServingRequest / 模型推理请求

跨层模型推理请求契约。D_ML_TRAIN ML Platform 提供推理服务，D_SIGNAL/D_PORTFOLIO_CORE 消费。

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











