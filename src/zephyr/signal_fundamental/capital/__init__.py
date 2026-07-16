# [A_module] module_id=MOD-UNK_capital | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.capital
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""Signal Capital Allocation sub-package"""

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
