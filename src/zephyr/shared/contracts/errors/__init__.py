# [A_module] module_id=MOD-SHR_errors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
"""
Auto-generated contracts package — errors

Backward-compat: trading-domain errors re-exported from trading-contracts.
Infrastructure errors remain here.
"""

import importlib

from zephyr.shared.contracts.errors.contract_violation_error import ContractViolationError
from zephyr.shared.contracts.errors.data_quality_error import DataQualityError
from zephyr.shared.contracts.errors.factor_computation_error import FactorComputationError

_TRADING_SYMBOLS = {
    "ExecutionRejectionError": "zephyr.execution_core.trading.trading_contracts.execution.execution_rejection_error",
    "RiskLimitViolationError": "zephyr.execution_core.trading.trading_contracts.risk.risk_limit_violation_error",
    "SignalDegradationWarning": "zephyr.execution_core.trading.trading_contracts.market.signal_degradation_warning",
}


def __getattr__(name):
    if name in _TRADING_SYMBOLS:
        mod = importlib.import_module(_TRADING_SYMBOLS[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ContractViolationError",
    "DataQualityError",
    "ExecutionRejectionError",
    "FactorComputationError",
    "RiskLimitViolationError",
    "SignalDegradationWarning",
    "contract_violation_error",
    "data_quality_error",
    "execution_rejection_error",
    "factor_computation_error",
    "risk_limit_violation_error",
    "signal_degradation_warning",
]
