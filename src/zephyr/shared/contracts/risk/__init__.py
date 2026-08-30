# [A_module] module_id=MOD-SHR-risk | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent
"""
Backward-compat shim — canonical location is zephyr.trading.trading_contracts.risk.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: importlib
#   code: __init__.py import L34
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 compliance_rule, risk_dashboard_snapshot, risk_limits, risk_metrics, risk_v…
#   desc: __init__ import L34；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: compliance_rule, risk_dashboard_snapshot, risk_limits, risk_metrics, risk_valid…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
