# [A_module] module_id=MOD-INT_model_serving_request | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# ==== BEGIN CODGEN:CTR-P1-004 ====
from dataclasses import dataclass, field

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
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
    input_features: dict[str, float] = field(default_factory=dict)


# ==== END CODGEN:CTR-P1-004 ====
