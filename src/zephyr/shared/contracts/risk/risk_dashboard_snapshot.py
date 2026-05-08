from __future__ import annotations
# ==== BEGIN CODGEN:CTR-P1-008 ====

from dataclasses import dataclass, field

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/risk_dashboard_snapshot.py

CTR-P1-008: RiskDashboardSnapshot / 风险仪表板快照

L04 → L08 风险仪表板实时快照契约。

SSoT: cross-layer-contracts.yaml → CTR-P1-008
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class RiskDashboardSnapshot:
    snapshot_time: str
    portfolio_id: str
    portfolio_var_1d: float
    max_drawdown_current: float
    gross_leverage: float
    top_position_concentration: float
    overall_risk_score: float
    idempotency_key: str
    sector_concentrations: dict[str, float] = field(default_factory=dict)
    active_alerts: list[str] = field(default_factory=list)
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-008 ====
