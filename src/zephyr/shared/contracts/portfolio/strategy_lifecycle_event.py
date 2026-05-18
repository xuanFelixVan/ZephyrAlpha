# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.contracts.portfolio.strategy_lifecycle_event

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
# ==== BEGIN CODGEN:CTR-P1-006 ====

from dataclasses import dataclass

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/strategy_lifecycle_event.py

CTR-P1-006: StrategyLifecycleEvent / 策略生命周期事件

L05 → L07/L10 策略生命周期事件契约。

SSoT: cross-layer-contracts.yaml → CTR-P1-006
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class StrategyLifecycleEvent:
    strategy_id: str
    event_type: str
    event_timestamp: str
    triggered_by: str
    reason: str
    previous_status: str
    new_status: str
    idempotency_key: str
    schema_version: str = "1.0"
    performance_snapshot: dict[str, float] | None = None


# ==== END CODGEN:CTR-P1-006 ====
