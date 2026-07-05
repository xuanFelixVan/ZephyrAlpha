# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.execution.capital_allocation_result
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.execution.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_capital_allocation_result | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Backward-compat shim — canonical location is zephyr.trading.trading_contracts.execution.capital_allocation_result."""

import importlib

_TARGET_MODULE = "zephyr.trading.trading_contracts.execution.capital_allocation_result"


def __getattr__(name):
    mod = importlib.import_module(_TARGET_MODULE)
    if hasattr(mod, name):
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
