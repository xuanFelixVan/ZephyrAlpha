# [A_module] module_id=MOD-UNK-risk_trading_contracts_risk | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

"""
trading-contracts.risk — risk management domain contracts.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: ComplianceRule, RiskDashboardSnapshot, RiskLimitViolationError, RiskL…
#   code: __init__.py import L46
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 ComplianceRule, RiskDashboardSnapshot, RiskLimitViolationError, RiskLimits,…
#   desc: __init__ import L46；__all__ 13 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（13 符号）
#   name_en: __all__
#   intro: ComplianceRule, RiskDashboardSnapshot, RiskLimitViolationError, RiskLimits, Ris…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

# 5.60.1 治本：从 canonical SSoT（shared 层，向下依赖）导入，
# 原经 gov_enforcement shim 导入造成 trading->governance 向上循环边（gov shim 真源即本模块）。
from zephyr.shared.contracts.compliance_rule import ComplianceRule
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
