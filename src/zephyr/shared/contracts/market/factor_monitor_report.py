# [A_module] module_id=MOD-SHR_factor_monitor_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §

# [MODULE] zephyr.shared.contracts.market.factor_monitor_report

# [INVARIANTS] backward-compat shim — canonical: zephyr.execution.trading.trading_contracts.market.factor_monitor_report

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Backward-compat shim — canonical location is zephyr.execution.trading.trading_contracts.market.factor_monitor_report."""

import importlib

_TARGET_MODULE = "zephyr.execution.trading.trading_contracts.market.factor_monitor_report"


def __getattr__(name):
    mod = importlib.import_module(_TARGET_MODULE)
    if hasattr(mod, name):
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
