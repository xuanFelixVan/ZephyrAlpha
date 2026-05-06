# ==== BEGIN CODGEN:EXT-002 ====

from __future__ import annotations

from dataclasses import dataclass, field
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/ext_002.py

EXT-002: Market Data Provider / 行情数据接口

入站数据必须经过 l00_data_source/quality/ 质量门禁方可下发；缺数据时触发 DataQualityError (INV-007: events crossing this boundary must carry idempotency_key)

SSoT: cross-layer-contracts.yaml → EXT-002
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















