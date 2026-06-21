# [A_module] module_id=MOD-INT_strategy_lifecycle_event | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# ==== BEGIN CODGEN:CTR-P1-006 ====
from dataclasses import dataclass, field

from typing import Dict
from typing import Optional
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/strategy_lifecycle_event.py

CTR-P1-006: StrategyLifecycleEvent / 策略生命周期事件

L05 → L07/L10 策略生命周期事件契约。

SSoT: cross_layer_contracts.yaml -> CTR-P1-006
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class StrategyLifecycleEvent:
    event_timestamp: str
    event_type: str
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    new_status: str
    previous_status: str
    reason: str
    strategy_id: str
    triggered_by: str
    performance_snapshot: Optional[Dict[str, float]] = None
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-006 ====















































































































































































