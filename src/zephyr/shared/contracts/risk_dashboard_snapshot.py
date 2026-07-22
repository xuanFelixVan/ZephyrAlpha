# ==== BEGIN CODGEN:CTR-P1-008 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.risk_dashboard_snapshot
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
from typing import List
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/risk_dashboard_snapshot.py

CTR-P1-008: RiskDashboardSnapshot / 风险仪表板快照

D_RISK -> D_FRONTEND 风险仪表板实时快照契约。

SSoT: cross_layer_contracts.yaml -> CTR-P1-008
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class RiskDashboardSnapshot:
    gross_leverage: float
    idempotency_key: str
    max_drawdown_current: float
    overall_risk_score: float
    portfolio_id: str
    portfolio_var_1d: float
    snapshot_time: str
    top_position_concentration: float
    active_alerts: List[str] = field(default_factory=list)
    schema_version: str = "1.0"
    sector_concentrations: Dict[str, float] = field(default_factory=dict)

# ==== END CODGEN:CTR-P1-008 ====











