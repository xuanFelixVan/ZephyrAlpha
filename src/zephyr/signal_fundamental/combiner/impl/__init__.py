# [A_module] module_id=MOD-UNK-impl | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.combiner.impl
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
D_SIGNAL — Signal Combiner Concrete Implementations

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, DefaultSignalAggregator, AllocationMethod, DefaultCapita…
#   code: __init__.py import L43
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AllocationMethod, DefaultCapitalAllocator, DefaultSignalAggregator, default…
#   desc: __init__ import L43；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: AllocationMethod, DefaultCapitalAllocator, DefaultSignalAggregator, default_cap…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.signal_fundamental.gen.implementations.default_signal_aggregator import DefaultSignalAggregator
from zephyr.signal_fundamental.strategy.implementations.default_capital_allocator import (
    AllocationMethod,
    DefaultCapitalAllocator,
)

__all__ = [
    "AllocationMethod",
    "DefaultCapitalAllocator",
    "DefaultSignalAggregator",
    "default_capital_allocator",
    "default_signal_aggregator",
]
