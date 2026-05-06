# ==== BEGIN CODGEN:EXT-001 ====

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
ZephyrAlpha — shared/contracts/ext_001.py

EXT-001: Broker API / 券商交易接口

发单前必须通过 pre_trade/ 风控；成交回报必须触发 Fill 契约并回调策略 (INV-007: events crossing this boundary must carry idempotency_key)

SSoT: cross-layer-contracts.yaml → EXT-001
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class Broker_API:
    pass

# ==== END CODGEN:EXT-001 ====















