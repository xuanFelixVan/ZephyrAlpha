# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.portfolio.performance_attribution_report
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
# [A_module] module_id=MOD-PRT_performance_attribution_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

# ==== BEGIN CODGEN:CTR-P1-009 ====
from dataclasses import dataclass, field

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/performance_attribution_report.py

CTR-P1-009: PerformanceAttributionReport / 绩效归因报告

D_REPORTING → D_FRONTEND/D_COMPLIANCE 绩效归因报告契约。

SSoT: cross_layer_contracts.yaml → CTR-P1-009
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class PerformanceAttributionReport:
    portfolio_id: str
    period_start: str
    period_end: str
    total_return: float
    allocation_effect: float
    selection_effect: float
    interaction_effect: float
    transaction_cost_drag: float
    idempotency_key: str
    factor_contributions: dict[str, float] = field(default_factory=dict)
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-009 ====
