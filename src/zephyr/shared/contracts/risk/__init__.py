# [A_module] module_id=MOD-SHR_risk | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent
"""Backward-compat shim — canonical location is zephyr.trading.trading_contracts.risk."""

import importlib

__all__ = [
    "compliance_rule",
    "risk_dashboard_snapshot",
    "risk_limits",
    "risk_metrics",
    "risk_validator_protocol",
]

from . import compliance_rule, risk_dashboard_snapshot, risk_limits, risk_metrics, risk_validator_protocol

_TRADING_SYMBOLS = {
    "RiskLimits": "zephyr.execution_core.trading.trading_contracts.risk.risk_limits",
    "RiskDashboardSnapshot": "zephyr.execution_core.trading.trading_contracts.risk.risk_dashboard_snapshot",
    "RiskMetricsReport": "zephyr.execution_core.trading.trading_contracts.risk.risk_metrics",
    "ComplianceRule": "zephyr.execution_core.trading.trading_contracts.risk.compliance_rule",
    "RiskValidatorProtocol": "zephyr.execution_core.trading.trading_contracts.risk.risk_validator_protocol",
    "ViolationDetail": "zephyr.execution_core.trading.trading_contracts.risk.risk_validator_protocol",
}


def __getattr__(name):
    if name in _TRADING_SYMBOLS:
        mod = importlib.import_module(_TRADING_SYMBOLS[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
