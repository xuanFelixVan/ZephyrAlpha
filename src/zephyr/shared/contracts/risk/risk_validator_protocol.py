# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §
"""Backward-compat shim — canonical location is zephyr.trading_contracts.risk.risk_validator_protocol."""

from zephyr.trading_contracts.risk.risk_validator_protocol import (  # noqa: F401
    RiskValidatorProtocol,
    ViolationDetail,
)
