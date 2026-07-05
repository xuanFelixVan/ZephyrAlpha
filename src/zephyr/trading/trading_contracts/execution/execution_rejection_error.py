# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.execution_rejection_error
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] ex_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_execution_rejection_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-ERR-005 ====
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionRejectionError:
    error_id: str
    idempotency_key: str
    order_id: str
    recovery_hint: str
    rejection_reason: str
    rejection_source: str
    symbol: str
    broker_message: str | None = None
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-ERR-005 ====
