# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-PRT-strategies_pf_core_strategies | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

Re-export wrapper: true source is zephyr.pf_core.default_equity_strategy.

Uses lazy __getattr__ to avoid double-registration in StrategyRegistry
(pf_core.strategies copy deleted; only pf_core.default_equity_strategy triggers @register).

# [ALGO_FLOW] external: docs/03_modules/_domain_portfolio_core/algo_flow/strategies__init__.yaml
"""

from typing import TYPE_CHECKING, Final

_LAZY = {
    "DefaultEquityStrategy": ("zephyr.pf_core.default_equity_strategy", "DefaultEquityStrategy"),
    "RebalanceMode": ("zephyr.pf_core.default_equity_strategy", "RebalanceMode"),
    # P0-4①（2026-08-21，CAND-SIG-012 晋升）：3 个 sleeve 组装策略类。
    # 真实模块放本包下、经本表 lazy 映射保证 import 只发生一次——
    # StrategyRegistry.register 对重复 strategy_id 直接 raise（strategy_base.py L114-115），
    # 禁止在本文件实体 import 三个类（历史双份拷贝致重复注册 raise 教训）。
    "DabanSleeveStrategy": ("zephyr.pf_core.strategies.daban_sleeve_strategy", "DabanSleeveStrategy"),
    "MultifactorSleeveStrategy": ("zephyr.pf_core.strategies.multifactor_sleeve_strategy", "MultifactorSleeveStrategy"),
    "EventDrivenSleeveStrategy": (
        "zephyr.pf_core.strategies.event_driven_sleeve_strategy",
        "EventDrivenSleeveStrategy",
    ),
}

# ORPHAN-MODULE 可发现性（2026-08-21）：TYPE_CHECKING 静态引用——仅类型检查期生效，
# 运行时不执行、不触发 @register（与上方"禁实体 import"约束兼容）；为 IDE/静态分析/
# 孤儿门禁提供三 sleeve 类的显式导入关系。符号已在 __all__ 再导出，非 unused。
if TYPE_CHECKING:
    from zephyr.pf_core.strategies.daban_sleeve_strategy import DabanSleeveStrategy
    from zephyr.pf_core.strategies.event_driven_sleeve_strategy import EventDrivenSleeveStrategy
    from zephyr.pf_core.strategies.multifactor_sleeve_strategy import MultifactorSleeveStrategy


def __getattr__(name):
    if name in _LAZY:
        import importlib

        mod_path, attr = _LAZY[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__: Final = [
    "DefaultEquityStrategy",
    "RebalanceMode",
    "DabanSleeveStrategy",
    "MultifactorSleeveStrategy",
    "EventDrivenSleeveStrategy",
]
