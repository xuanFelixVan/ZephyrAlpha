# [A_module] module_id=MOD-SHR-risk | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent
"""
Backward-compat shim — canonical location is zephyr.trading.trading_contracts.risk.

# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/contracts/risk/risk__init__.yaml
"""

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
    # B3 治本（2026-09-05）：RiskLimits 改指 CTR-003 登记真源（trading_contracts
    # 副本已降级 re-export shim，见 cross_layer_contracts.yaml physical_path）
    "RiskLimits": "zephyr.shared.contracts.risk_limits",
    "RiskDashboardSnapshot": "zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot",
    "RiskMetricsReport": "zephyr.trading.trading_contracts.risk.risk_metrics",
    "ComplianceRule": "zephyr.trading.trading_contracts.risk.compliance_rule",
    "RiskValidatorProtocol": "zephyr.trading.trading_contracts.risk.risk_validator_protocol",
    "ViolationDetail": "zephyr.trading.trading_contracts.risk.risk_validator_protocol",
}


def __getattr__(name):
    if name in _TRADING_SYMBOLS:
        mod = importlib.import_module(_TRADING_SYMBOLS[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
