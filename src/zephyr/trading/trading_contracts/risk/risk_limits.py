# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.risk_limits
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] risk; pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_risk_limits | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-003 ====
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class RiskLimits:
    as_of_date: datetime
    idempotency_key: str
    max_drawdown_limit: float | None = None
    max_gross_leverage: float = 1.0
    max_portfolio_var_1d: float | None = None
    max_sector_concentration: float = 0.3
    max_single_position: float = 0.1
    min_single_position: float = 0.0
    schema_version: str = "1.0"
    symbol_overrides: dict[str, float] = field(default_factory=dict)
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-003 ====
