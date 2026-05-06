

# ==== BEGIN CODGEN:CTR-P1-009 ====

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/performance_attribution_report.py

CTR-P1-009: PerformanceAttributionReport / 绩效归因报告

L07 → L08/L10 绩效归因报告契约。

SSoT: cross-layer-contracts.yaml → CTR-P1-009
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
    factor_contributions: Dict[str, float] = field(default_factory=dict)
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-009 ====



