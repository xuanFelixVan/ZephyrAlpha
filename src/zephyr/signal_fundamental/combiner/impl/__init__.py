# [A_module] module_id=MOD-UNK_impl | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
"""D_SIGNAL — Signal Combiner Concrete Implementations"""

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
