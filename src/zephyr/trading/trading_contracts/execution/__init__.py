# [A_module] module_id=MOD-EXE_execution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

"""trading-contracts.execution — order execution domain contracts."""

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
