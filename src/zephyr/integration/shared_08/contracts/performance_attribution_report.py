# [A_module] module_id=MOD-INT_performance_attribution_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# ==== BEGIN CODGEN:CTR-P1-009 ====
from dataclasses import dataclass, field

from typing import Dict
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/performance_attribution_report.py

CTR-P1-009: PerformanceAttributionReport / 绩效归因报告

L07 → L08/L10 绩效归因报告契约。

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
    idempotency_key: str
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















































































































































































