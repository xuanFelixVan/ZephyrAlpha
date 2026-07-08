# ==== BEGIN CODGEN:CTR-P1-006 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.strategy_lifecycle_event
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
from typing import Optional
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/strategy_lifecycle_event.py

CTR-P1-006: StrategyLifecycleEvent / 策略生命周期事件

D_PORTFOLIO_CORE -> D_REPORTING/D_COMPLIANCE 策略生命周期事件契约。

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
    new_status: str
    previous_status: str
    reason: str
    strategy_id: str
    triggered_by: str
    performance_snapshot: Optional[Dict[str, float]] = None
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-006 ====











