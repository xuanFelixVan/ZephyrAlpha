# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.external.ext_002
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
# [A_module] module_id=MOD-SHR_ext_002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:EXT-002 ====

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
ZephyrAlpha — shared/contracts/ext_002.py

EXT-002: Market Data Provider / 行情数据接口

入站数据必须经过 data/quality/ 质量门禁方可下发；缺数据时触发 DataQualityError (INV-007: events crossing this boundary must carry idempotency_key)

SSoT: cross_layer_contracts.yaml → EXT-002
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class Market_Data_Provider:
    provider_name: str
    data_feed_url: str
    supported_instruments: tuple[str, ...]
    update_frequency_ms: int


# ==== END CODGEN:EXT-002 ====
