# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] src.zephyr.shared.contracts.errors.risk_limit_violation_error
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.contracts.errors.__init__
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
# [A_module] module_id=MOD-SHR_risk_limit_violation_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Backward-compat shim — canonical location is zephyr.execution.trading.trading_contracts.risk.risk_limit_violation_error."""

import importlib

_TARGET_MODULE = "zephyr.execution.trading.trading_contracts.risk.risk_limit_violation_error"


def __getattr__(name):
    mod = importlib.import_module(_TARGET_MODULE)
    if hasattr(mod, name):
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
