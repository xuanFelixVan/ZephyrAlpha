# [BLUEPRINT] MOD-L03-001 | 03_modules/l03_signal_generation/signal-generation-core/blueprint.md | §
"""L03 — Signal Generation Concrete Implementations

Phase C 具体实现包。包含所有抽象基类的默认生产级实现。

实现清单：
  - DefaultSignalAggregator   : SignalAggregatorBase 的具体实现（3 种聚合策略）
  - DefaultCapitalAllocator   : CapitalAllocatorBase 的具体实现（4 种分配策略）
"""

from zephyr.l03_signal_generation.implementations.default_signal_aggregator import (
    DefaultSignalAggregator,
)
from zephyr.l03_signal_generation.implementations.default_capital_allocator import (
    DefaultCapitalAllocator,
    AllocationMethod,
)

__all__ = ['AllocationMethod', 'DefaultCapitalAllocator', 'DefaultSignalAggregator', 'default_capital_allocator', 'default_signal_aggregator']
