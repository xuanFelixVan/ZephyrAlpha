# [A_module] module_id=MOD-EXE_execution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent
"""Backward-compat shim — canonical location is zephyr.trading.trading_contracts.execution."""

import importlib

__all__ = [
    "capital_allocation_result",
    "execution_report",
    "fill",
    "model_serving_request",
    "order",
]

_TRADING_SYMBOLS = {
    "Order": "zephyr.execution_core.trading.trading_contracts.execution.order",
    "OrderSide": "zephyr.execution_core.trading.trading_contracts.execution.order",
    "OrderStatus": "zephyr.execution_core.trading.trading_contracts.execution.order",
    "OrderType": "zephyr.execution_core.trading.trading_contracts.execution.order",
    "Fill": "zephyr.execution_core.trading.trading_contracts.execution.fill",
    "CapitalAllocationResult": "zephyr.execution_core.trading.trading_contracts.execution.capital_allocation_result",
    "ExecutionReport": "zephyr.execution_core.trading.trading_contracts.execution.execution_report",
    "ModelServingRequest": "zephyr.execution_core.trading.trading_contracts.execution.model_serving_request",
}


def __getattr__(name):
    if name in _TRADING_SYMBOLS:
        mod = importlib.import_module(_TRADING_SYMBOLS[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
