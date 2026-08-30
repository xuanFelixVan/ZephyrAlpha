# [A_module] module_id=MOD-UNK-capital | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.capital
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""
Signal Capital Allocation sub-package

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, CapitalAllocationResult, CapitalAllocatorBase, Allocatio…
#   code: __init__.py import L38
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AllocationMethod, CapitalAllocationResult, CapitalAllocatorBase, DefaultCap…
#   desc: __init__ import L38；__all__ 7 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（7 符号）
#   name_en: __all__
#   intro: AllocationMethod, CapitalAllocationResult, CapitalAllocatorBase, DefaultCapital…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.signal_fundamental.capital.capital_allocation_result import CapitalAllocationResult
from zephyr.signal_fundamental.capital.capital_allocator import CapitalAllocatorBase
from zephyr.signal_fundamental.capital.default_capital_allocator import AllocationMethod, DefaultCapitalAllocator

__all__ = [
    "AllocationMethod",
    "CapitalAllocationResult",
    "CapitalAllocatorBase",
    "DefaultCapitalAllocator",
    "capital_allocation_result",
    "capital_allocator",
    "default_capital_allocator",
]
