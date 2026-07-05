# [A_module] module_id=MOD-EXE_ex_core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_EXECUTION_CORE Trade Execution — Re-export wrapper (DM-298)

All modules have been migrated to zephyr.execution_core.core.
This package re-exports for backward compatibility.
"""

from __future__ import annotations

__all__ = [
    "AlgoType",
    "BrokerInterface",
    "ExecutionConfig",
    "ExecutionEngine",
    "ExecutionEngineRunRecord",
    "FillCallback",
    "OrderAction",
    "OrderManager",
    "adapters",
    "broker_interface",
    "execution_engine",
    "order_manager",
]

_LAZY_IMPORTS = {
    "ExecutionEngine": ("zephyr.ex_core.execution_engine", "ExecutionEngine"),
    "ExecutionEngineRunRecord": ("zephyr.ex_core.execution_engine", "ExecutionEngineRunRecord"),
    "ExecutionConfig": ("zephyr.ex_core.execution_engine", "ExecutionConfig"),
    "AlgoType": ("zephyr.ex_core.execution_engine", "AlgoType"),
    "BrokerInterface": ("zephyr.ex_core.broker_interface", "BrokerInterface"),
    "FillCallback": ("zephyr.ex_core.broker_interface", "FillCallback"),
    "OrderManager": ("zephyr.ex_core.order_manager", "OrderManager"),
    "OrderAction": ("zephyr.ex_core.order_manager", "OrderAction"),
}

_SUBMODULES = ["execution_engine", "order_manager", "broker_interface", "adapters"]


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        import importlib

        mod_path, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr_name)
        globals()[name] = value
        return value
    if name in _SUBMODULES:
        import importlib

        if name == "adapters":
            mod = importlib.import_module("zephyr.ex_core.adapters")
        else:
            mod = importlib.import_module(f"zephyr.ex_core.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
