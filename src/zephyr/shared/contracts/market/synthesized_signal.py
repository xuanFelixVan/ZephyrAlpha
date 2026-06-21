# [A_module] module_id=MOD-SHR_synthesized_signal | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §
"""Backward-compat shim — canonical location is zephyr.execution.trading.trading_contracts.market.synthesized_signal."""

import importlib

_TARGET_MODULE = "zephyr.execution.trading.trading_contracts.market.synthesized_signal"


def __getattr__(name):
    mod = importlib.import_module(_TARGET_MODULE)
    if hasattr(mod, name):
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
