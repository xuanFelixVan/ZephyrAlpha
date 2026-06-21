# [A_module] module_id=MOD-INT_ext_002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] SRC-175 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md

# [MODULE] zephyr.integration.shared_08.contracts.external.ext_004_002

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ==== BEGIN CODGEN:EXT-002 ====

from dataclasses import dataclass, field
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
    pass

# ==== END CODGEN:EXT-002 ====

