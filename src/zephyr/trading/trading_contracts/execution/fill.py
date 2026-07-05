# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.fill
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] ex_core; pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_fill | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-005 ====
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Fill:
    fill_id: str
    fill_price: Decimal
    fill_timestamp: datetime
    filled_quantity: Decimal
    idempotency_key: str
    order_id: str
    strategy_id: str
    symbol: str
    broker_fill_id: str | None = None
    commission: Decimal = Decimal("0")
    schema_version: str = "1.0"
    slippage: Decimal | None = None
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-005 ====
