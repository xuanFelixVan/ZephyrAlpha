# [A_module] module_id=MOD-UNK-strategy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.strategy
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""
Signal Strategy sub-package

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, CapitalAllocationResult, CapitalAllocatorBase
#   code: __init__.py import L38
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 CapitalAllocationResult, CapitalAllocatorBase, capital_allocator（共 3 符号）
#   desc: __init__ import L38；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: CapitalAllocationResult, CapitalAllocatorBase, capital_allocator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.signal_fundamental.strategy.capital_allocator import CapitalAllocationResult, CapitalAllocatorBase

__all__ = [
    "CapitalAllocationResult",
    "CapitalAllocatorBase",
    "capital_allocator",
]
