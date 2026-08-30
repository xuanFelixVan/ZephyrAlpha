# [A_module] module_id=MOD-UNK-gen | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.gen
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""
Signal Generation sub-package

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations
#   code: __init__.py import L38
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 CapitalAllocatorBase, DegradationMonitorBase, SignalAggregatorBase, aggrega…
#   desc: __init__ import L38；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: CapitalAllocatorBase, DegradationMonitorBase, SignalAggregatorBase, aggregator_…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

__all__ = [
    "CapitalAllocatorBase",
    "DegradationMonitorBase",
    "SignalAggregatorBase",
    "aggregator_base",
]


def __getattr__(name):
    _lazy = {
        "SignalAggregatorBase": ".aggregator_base",
        "CapitalAllocatorBase": ".aggregator_base",
        # DegradationMonitorBase 真源已迁移至 D_SIGQC 域（2026-07-06 域边界修正），
        # 此处跨域 re-export 向后兼容。
        "DegradationMonitorBase": "zephyr.signal_quality.degradation_monitor_base",
    }
    if name in _lazy:
        import importlib

        mod = importlib.import_module(_lazy[name], __name__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
