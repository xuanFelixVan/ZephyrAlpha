# [A_module] module_id=MOD-EXE_risk_limit_violation_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.execution.trading.trading_contracts.risk.risk_limit_violation_error

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] risk; pf_core

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from typing import Optional

class RiskLimitViolationError(Exception):
    __slots__ = (
        "actual_value",
        "error_id",
        "idempotency_key",
        "limit_value",
        "portfolio_id",
        "recovery_hint",
        "violated_constraint",
        "violation_detail",
        "schema_version",
        "trace_context",
    )

    def __init__(
        self,
        *,
        error_id: str,
        portfolio_id: str,
        violated_constraint: str,
        violation_detail: str,
        limit_value: float,
        actual_value: float,
        recovery_hint: str,
        idempotency_key: str,
        schema_version: str = "1.0",
        trace_context: Optional[TraceContext] = None,
    ) -> None:
        super().__init__(violation_detail)
        self.actual_value = actual_value
        self.error_id = error_id
        self.idempotency_key = idempotency_key
        self.limit_value = limit_value
        self.portfolio_id = portfolio_id
        self.recovery_hint = recovery_hint
        self.violated_constraint = violated_constraint
        self.violation_detail = violation_detail
        self.schema_version = schema_version
        self.trace_context = trace_context

__all__ = ["RiskLimitViolationError"]
