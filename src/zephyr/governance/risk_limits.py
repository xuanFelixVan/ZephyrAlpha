# [A_module] module_id=MOD-PRT_risk_limits | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.execution.trading.trading_contracts.risk.risk_limits

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] risk; pf_core

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ==== BEGIN CODGEN:CTR-003 ====
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

__all__ = ["RiskLimits"]
