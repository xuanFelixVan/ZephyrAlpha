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
"""

D_EXECUTION_CORE 执行核心域 — 包入口（懒加载聚合导出）

本包即执行核心域 canonical 实现（MOD-L06-001），非迁移残留 shim。
包级命名空间通过 _LAZY_IMPORTS 懒加载，避免包导入即拉起执行链重依赖。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: typing 子模块符号 1个
#   fields: Final
#   code: typing
# - id: I2
#   name: ex_core 子模块符号 1个
#   fields: multi_contract_adapter
#   code: zephyr.ex_core
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.ex_core.__init__
#   intro: D_EXECUTION_CORE 执行核心域包入口（canonical 实现，非 shim）
#   desc: MOD-L06-001 包入口，包级聚合再导出并声明 __all__（12项）
#   inputs: I1 I2
#   outputs: zephyr.ex_core 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（12项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.ex_core 包公共 API
#   name_en: __all__ 12项
#   intro: 执行核心域对外统一出口（懒加载，canonical 实现）
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
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
