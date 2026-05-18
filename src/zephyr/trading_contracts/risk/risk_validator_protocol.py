# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.risk.risk_validator_protocol

# [INVARIANTS] ViolationDetail is SSoT for cross-layer risk violation data; l04 re-exports from here

# [MODIFY-GUARD] Changes to ViolationDetail fields MUST sync with l04_risk_management.risk_validator

# [CONSUMERS] l06_trade_execution.execution_engine; l04_risk_management.risk_validator

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] ValueError on negative limit_value

# [TESTS] tests/unit/l04_risk_management/test_risk_validator.py; tests/unit/l06_trade_execution/

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class ViolationDetail:
    constraint: str
    description: str
    limit_value: Decimal
    actual_value: Decimal
    severity: str = "HALT"


@runtime_checkable
class RiskValidatorProtocol(Protocol):
    def validate_order(
        self,
        symbol: str,
        target_weight: float,
        current_holdings: dict[str, float],
        limits: Any,
    ) -> list[ViolationDetail]: ...

    def validate_portfolio(
        self,
        holdings: dict[str, float],
        market_values: dict[str, float],
        total_nav: Decimal,
        limits: Any,
    ) -> list[ViolationDetail]: ...


__all__ = ["ViolationDetail", "RiskValidatorProtocol"]
