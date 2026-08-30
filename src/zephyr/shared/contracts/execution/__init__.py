# [A_module] module_id=MOD-EXE-execution_contracts_execution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent
"""
Backward-compat shim — canonical location is zephyr.trading.trading_contracts.execution.

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
#   intro: 再导出 capital_allocation_result, execution_report, fill, model_serving_request, o…
#   desc: __init__ import L34；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: capital_allocation_result, execution_report, fill, model_serving_request, order
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import importlib

__all__ = [
    "capital_allocation_result",
    "execution_report",
    "fill",
    "model_serving_request",
    "order",
]

_SHARED_SYMBOLS = {
    "Order": "zephyr.shared.contracts.order",
    "OrderSide": "zephyr.shared.contracts.enums.order_enums",
    "OrderStatus": "zephyr.shared.contracts.enums.order_enums",
    "OrderType": "zephyr.shared.contracts.enums.order_enums",
    "Fill": "zephyr.shared.contracts.fill",
    "CapitalAllocationResult": "zephyr.shared.contracts.capital_allocation_result",
    "ExecutionReport": "zephyr.shared.contracts.execution_report",
    "ModelServingRequest": "zephyr.shared.contracts.model_serving_request",
}


def __getattr__(name):
    if name in _SHARED_SYMBOLS:
        mod = importlib.import_module(_SHARED_SYMBOLS[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
