# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
"""Backward-compat shim — canonical location is zephyr.trading_contracts.risk."""

from zephyr.trading_contracts.risk.risk_limits import RiskLimits  # noqa: F401
from zephyr.trading_contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot  # noqa: F401
from zephyr.trading_contracts.risk.risk_metrics import RiskMetricsReport  # noqa: F401
from zephyr.trading_contracts.risk.compliance_rule import ComplianceRule  # noqa: F401
from zephyr.trading_contracts.risk.risk_validator_protocol import (  # noqa: F401
    RiskValidatorProtocol, ViolationDetail,
)
from . import compliance_rule
from . import risk_dashboard_snapshot
from . import risk_limits
from . import risk_metrics
from . import risk_validator_protocol
