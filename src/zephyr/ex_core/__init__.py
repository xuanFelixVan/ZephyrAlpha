# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

from typing import Final

from zephyr.ex_core import multi_contract_adapter  # noqa: F401 — 包级导出（契约注册中心）

__all__: Final = [
    "AlgoType",
    "BrokerInterface",
    "ExecutionConfig",
    "ExecutionEngine",
    "ExecutionEngineRunRecord",
    "FillCallback",
    "OrderAction",
    "OrderManager",
    "adapters",
    "execution_engine",
    "multi_contract_adapter",
    "order_manager",
]

_LAZY_IMPORTS: Final = {
    "ExecutionEngine": ("zephyr.ex_core.execution_engine", "ExecutionEngine"),
    "ExecutionEngineRunRecord": ("zephyr.ex_core.execution_engine", "ExecutionEngineRunRecord"),
    "ExecutionConfig": ("zephyr.ex_core.execution_engine", "ExecutionConfig"),
    "AlgoType": ("zephyr.ex_core.execution_engine", "AlgoType"),
    # ARCH-GOV-SHIM-001 阶段2：直接指向 canonical 路径（原 ex_core.broker_interface shim 已删除）
    "BrokerInterface": ("zephyr.trading.trading_contracts.broker_interface", "BrokerInterface"),
    "FillCallback": ("zephyr.trading.trading_contracts.broker_interface", "FillCallback"),
    "OrderManager": ("zephyr.ex_core.order_manager", "OrderManager"),
    "OrderAction": ("zephyr.ex_core.order_manager", "OrderAction"),
}

_SUBMODULES: Final = ["execution_engine", "order_manager", "adapters", "multi_contract_adapter"]


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
