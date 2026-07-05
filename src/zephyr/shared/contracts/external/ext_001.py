# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.external.ext_001
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
# [A_module] module_id=MOD-SHR_ext_001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:EXT-001 ====

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
ZephyrAlpha — shared/contracts/ext_001.py

EXT-001: Broker API / 券商交易接口

发单前必须通过 pre_trade/ 风控；成交回报必须触发 Fill 契约并回调策略 (INV-007: events crossing this boundary must carry idempotency_key)

SSoT: cross_layer_contracts.yaml → EXT-001
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class Broker_API:
    broker_name: str
    api_endpoint: str
    supported_order_types: tuple[str, ...]
    rate_limit_per_second: int


# ==== END CODGEN:EXT-001 ====
