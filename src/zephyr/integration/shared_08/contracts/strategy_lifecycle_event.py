# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.shared_08.contracts.strategy_lifecycle_event
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] tests.integration.test_phase_f_layers
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# ==== BEGIN CODGEN:CTR-P1-006 ====
from dataclasses import dataclass

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
    performance_snapshot: dict[str, float] | None = None
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-006 ====
