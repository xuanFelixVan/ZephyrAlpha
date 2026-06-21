# [A_module] module_id=MOD-EXE_execution_rejection_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.execution.trading.trading_contracts.execution.execution_rejection_error

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] ex_core

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ==== BEGIN CODGEN:CTR-ERR-005 ====
from dataclasses import dataclass, field

from typing import Optional

@dataclass(frozen=True)
class ExecutionRejectionError:
    error_id: str
    idempotency_key: str
    order_id: str
    recovery_hint: str
    rejection_reason: str
    rejection_source: str
    symbol: str
    broker_message: Optional[str] = None
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-ERR-005 ====

__all__ = ["ExecutionRejectionError"]
