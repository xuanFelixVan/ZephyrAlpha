# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.risk.risk_dashboard_snapshot

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l04_risk_management; l08_monitoring

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
# ==== BEGIN CODGEN:CTR-P1-008 ====

from dataclasses import dataclass, field

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
