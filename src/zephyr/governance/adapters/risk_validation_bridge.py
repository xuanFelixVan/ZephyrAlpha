# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.governance.adapters.risk_validation_bridge
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.ex_core.execution_engine
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] RiskValidationBridge wraps RiskValidatorProtocol; execution_engine MUST NOT import trading-contracts.risk directly
# [MODIFY-GUARD] blueprint.md §Cross-Layer; adapters/__init__.py __all__
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RiskValidationBridgeError on adapter failure
# [TESTS] tests/ex_core/test_execution_engine_unit.py
# [A_module] module_id=MOD-EXE_risk_validation_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ex_core
# category: cross_layer_bridge
# status: active
# created: "2026-05-23"
# ---

"""D_EXECUTION_CORE — Risk Validation Bridge (DW-239)

Cross-layer bridge that decouples D_EXECUTION_CORE (trade execution) from D_RISK (risk management)
contract namespace. ExecutionEngine depends on this bridge instead of importing
RiskValidatorProtocol from trading-contracts.risk directly.

Pattern: Adapter — wraps the Protocol-based risk validator behind a local interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from zephyr.shared.contracts.risk_limits import RiskLimits


@dataclass(frozen=True)
class RiskViolation:
    constraint: str
    description: str
    limit_value: Decimal
    actual_value: Decimal
    severity: str = "HALT"


@runtime_checkable
class RiskValidationPort(Protocol):
    def validate_order(
        self,
        symbol: str,
        target_weight: float,
        current_holdings: dict[str, float],
        limits: RiskLimits,
    ) -> list[RiskViolation]: ...

    def validate_portfolio(
        self,
        holdings: dict[str, float],
        market_values: dict[str, float],
        total_nav: Decimal,
        limits: RiskLimits,
    ) -> list[RiskViolation]: ...


class RiskValidationBridge:
    """Adapter bridging trading-contracts.risk.RiskValidatorProtocol to D_EXECUTION_CORE's local RiskValidationPort.

    Usage:
        from zephyr.governance.adapters.risk_validation_bridge import RiskValidationBridge
        bridge = RiskValidationBridge(risk_validator)
        engine = ExecutionEngine(order_manager=om, risk_validator=bridge)
    """

    def __init__(self, risk_validator: RiskValidationPort) -> None:
        self._validator = risk_validator

    def validate_order(
        self,
        symbol: str,
        target_weight: float,
        current_holdings: dict[str, float],
        limits: RiskLimits,
    ) -> list[RiskViolation]:
        raw_violations = self._validator.validate_order(
            symbol=symbol,
            target_weight=target_weight,
            current_holdings=current_holdings,
            limits=limits,
        )
        return [self._convert(v) for v in raw_violations]

    def validate_portfolio(
        self,
        holdings: dict[str, float],
        market_values: dict[str, float],
        total_nav: Decimal,
        limits: RiskLimits,
    ) -> list[RiskViolation]:
        raw_violations = self._validator.validate_portfolio(
            holdings=holdings,
            market_values=market_values,
            total_nav=total_nav,
            limits=limits,
        )
        return [self._convert(v) for v in raw_violations]

    @staticmethod
    def _convert(v: object) -> RiskViolation:
        if isinstance(v, RiskViolation):
            return v
        return RiskViolation(
            constraint=getattr(v, "constraint", str(v)),
            description=getattr(v, "description", ""),
            limit_value=getattr(v, "limit_value", Decimal("0")),
            actual_value=getattr(v, "actual_value", Decimal("0")),
            severity=getattr(v, "severity", "HALT"),
        )


__all__ = ["RiskValidationBridge", "RiskValidationPort", "RiskViolation"]
