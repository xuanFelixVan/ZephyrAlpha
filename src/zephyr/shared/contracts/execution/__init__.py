# [A_module] module_id=MOD-EXE_execution_contracts_execution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
