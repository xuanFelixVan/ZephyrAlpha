# [A_module] module_id=MOD-UNK_risk_trading_contracts_risk | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent

"""trading-contracts.risk — risk management domain contracts."""

from zephyr.gov_enforcement.rule_enforcement.compliance_rule import ComplianceRule
from zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.trading.trading_contracts.risk.risk_limit_violation_error import RiskLimitViolationError
from zephyr.trading.trading_contracts.risk.risk_limits import RiskLimits
from zephyr.trading.trading_contracts.risk.risk_metrics import RiskMetricsReport
from zephyr.trading.trading_contracts.risk.risk_validator_protocol import (
    RiskValidatorProtocol,
    ViolationDetail,
)

__all__ = [
    "ComplianceRule",
    "RiskDashboardSnapshot",
    "RiskLimitViolationError",
    "RiskLimits",
    "RiskMetricsReport",
    "RiskValidatorProtocol",
    "ViolationDetail",
    "compliance_rule",
    "risk_dashboard_snapshot",
    "risk_limit_violation_error",
    "risk_limits",
    "risk_metrics",
    "risk_validator_protocol",
]
