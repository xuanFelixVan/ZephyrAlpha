# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.execution_report
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_execution_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:CTR-P1-007 ====

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ExecutionReport:
    order_id: str
    symbol: str
    direction: str
    intended_quantity: int
    actual_quantity: int
    intended_price: Decimal
    vwap_price: Decimal
    slippage_bps: float
    commission: Decimal
    execution_start: str
    execution_end: str
    broker_id: str
    idempotency_key: str
    algo_type: str = "NONE"
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-007 ====
