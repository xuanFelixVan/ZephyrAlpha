# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.position
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] ex_core; pf_core; risk; l11-ml-platform
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_position | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-006 ====
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class PositionSnapshot:
    as_of_timestamp: datetime
    idempotency_key: str
    portfolio_id: str
    cash: Decimal = Decimal("0")
    gross_leverage: float = 1.0
    holdings: dict[str, Decimal] = field(default_factory=dict)
    market_values: dict[str, Decimal] = field(default_factory=dict)
    schema_version: str = "1.0"
    total_market_value: Decimal = Decimal("0")
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-006 ====
