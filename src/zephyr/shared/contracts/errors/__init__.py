# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
"""
Auto-generated contracts package — errors

Backward-compat: trading-domain errors re-exported from trading_contracts.
Infrastructure errors remain here.
"""

from .contract_violation_error import *  # noqa: F403
from .data_quality_error import *  # noqa: F403
from .factor_computation_error import *  # noqa: F403
from zephyr.trading_contracts.execution.execution_rejection_error import ExecutionRejectionError  # noqa: F401
from zephyr.trading_contracts.risk.risk_limit_violation_error import RiskLimitViolationError  # noqa: F401
from zephyr.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning  # noqa: F401

__all__ = ['contract_violation_error', 'data_quality_error', 'execution_rejection_error', 'factor_computation_error', 'risk_limit_violation_error', 'signal_degradation_warning']
