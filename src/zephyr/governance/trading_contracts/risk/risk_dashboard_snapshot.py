# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.execution.trading.trading_contracts.risk.risk_dashboard_snapshot
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] risk; ops
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_risk_dashboard_snapshot | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

__all__ = ["RiskDashboardSnapshot"]
