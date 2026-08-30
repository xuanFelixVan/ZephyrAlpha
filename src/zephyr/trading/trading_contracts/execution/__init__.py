# [A_module] module_id=MOD-EXE-execution_trading_contracts_execution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution
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
trading-contracts.execution — order execution domain contracts.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: CapitalAllocationResult, ExecutionRejectionError, ExecutionReport, Fi…
#   code: __init__.py import L44
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 CapitalAllocationResult, ExecutionRejectionError, ExecutionReport, Fill, Mo…
#   desc: __init__ import L44；__all__ 17 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（17 符号）
#   name_en: __all__
#   intro: CapitalAllocationResult, ExecutionRejectionError, ExecutionReport, Fill, ModelS…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.trading.trading_contracts.execution.execution_rejection_error import ExecutionRejectionError
from zephyr.trading.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.model_serving_request import ModelServingRequest
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.trading.trading_contracts.execution.position import PositionSnapshot

__all__ = [
    "CapitalAllocationResult",
    "ExecutionRejectionError",
    "ExecutionReport",
    "Fill",
    "ModelServingRequest",
    "Order",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "PositionSnapshot",
    "capital_allocation_result",
    "execution_rejection_error",
    "execution_report",
    "fill",
    "model_serving_request",
    "order",
    "position",
]
