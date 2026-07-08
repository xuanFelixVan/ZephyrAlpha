# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.external.ext_003
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
# [A_module] module_id=MOD-SHR_ext_003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:EXT-003 ====

from __future__ import annotations

from dataclasses import dataclass

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/ext_003.py

EXT-003: LLM Providers / 大模型推理接口

支持降级（LLM 不可用时跳过 AI 增强，主流程不中断）；调用必须经过 AI Agent Ops 层，D_FACTOR~D_REPORTING 禁止直接调用 (INV-007: events crossing this boundary must carry idempotency_key)

SSoT: cross_layer_contracts.yaml -> EXT-003
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class LLM_Providers:
    provider_name: str
    model_id: str
    max_context_tokens: int
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float


# ==== END CODGEN:EXT-003 ====
