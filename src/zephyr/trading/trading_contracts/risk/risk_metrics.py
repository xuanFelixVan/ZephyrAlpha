# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.risk_metrics
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] risk; pf_core; pf_core; ops; l10-compliance
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_risk_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:CTR-P1-011 ====

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RiskMetricsReport:
    as_of_date: datetime
    beta: float
    calculation_method: str
    confidence_level: float
    current_drawdown: float
    cvar_1d_95: float
    cvar_1d_99: float
    idempotency_key: str
    lookback_period: int
    max_drawdown: float
    portfolio_id: str
    sharpe_ratio: float
    sortino_ratio: float
    var_1d_95: float
    var_1d_99: float
    volatility_1d: float
    volatility_1m: float
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-011 ====
