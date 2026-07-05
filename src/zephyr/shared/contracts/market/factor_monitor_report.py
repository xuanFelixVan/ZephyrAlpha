# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.market.factor_monitor_report
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] backward-compat shim — canonical: zephyr.trading.trading_contracts.market.factor_monitor_report
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_factor_monitor_report | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Backward-compat shim — canonical location is zephyr.trading.trading_contracts.market.factor_monitor_report."""

import importlib

_TARGET_MODULE = "zephyr.trading.trading_contracts.market.factor_monitor_report"


def __getattr__(name):
    mod = importlib.import_module(_TARGET_MODULE)
    if hasattr(mod, name):
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
