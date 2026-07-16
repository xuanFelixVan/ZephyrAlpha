# [A_module] module_id=MOD-UNK_strategy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.strategy
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""Signal Strategy sub-package"""

from __future__ import annotations

from zephyr.signal_fundamental.strategy.capital_allocator import CapitalAllocationResult, CapitalAllocatorBase

__all__ = [
    "CapitalAllocationResult",
    "CapitalAllocatorBase",
    "capital_allocator",
]
