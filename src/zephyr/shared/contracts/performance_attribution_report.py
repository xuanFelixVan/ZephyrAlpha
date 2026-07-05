# ==== BEGIN CODGEN:CTR-P1-009 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.performance_attribution_report
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
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/performance_attribution_report.py

CTR-P1-009: PerformanceAttributionReport / 绩效归因报告

D_REPORTING → D_FRONTEND/D_COMPLIANCE 绩效归因报告契约。

SSoT: cross_layer_contracts.yaml -> CTR-P1-009
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class PerformanceAttributionReport:
    allocation_effect: float
    idempotency_key: str
    interaction_effect: float
    period_end: str
    period_start: str
    portfolio_id: str
    selection_effect: float
    total_return: float
    transaction_cost_drag: float
    factor_contributions: Dict[str, float] = field(default_factory=dict)
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-009 ====











