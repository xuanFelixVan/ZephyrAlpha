# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-PRT-strategies | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""
Re-export wrapper: true source is zephyr.pf_core.default_equity_strategy.

Uses lazy __getattr__ to avoid double-registration in StrategyRegistry
(governance copy deleted; only pf_core true source triggers @register).

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 DefaultEquityStrategy, RebalanceMode（共 2 符号）
#   desc: __init__ import L0；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: DefaultEquityStrategy, RebalanceMode
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

_LAZY = {
    # 5.152 #8 sanctioned: governance(L2)->pf_core(L2) 同层依赖，层级模型允许；
    # PEP 562 lazy 映射避免 StrategyRegistry 双重注册，真源唯一在 pf_core.default_equity_strategy。
    "DefaultEquityStrategy": ("zephyr.pf_core.default_equity_strategy", "DefaultEquityStrategy"),
    "RebalanceMode": ("zephyr.pf_core.default_equity_strategy", "RebalanceMode"),
}


def __getattr__(name):
    if name in _LAZY:
        import importlib

        mod_path, attr = _LAZY[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["DefaultEquityStrategy", "RebalanceMode"]
