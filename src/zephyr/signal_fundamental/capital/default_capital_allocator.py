# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain-signal/signal-generation-core/blueprint.md
# [MODULE] zephyr.signal_fundamental.capital.default_capital_allocator
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_fundamental.strategy.implementations.default_capital_allocator
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_default_capital_allocator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: signal
# category: allocation_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_SIGNAL — Default Capital Allocator（兼容 re-export shim）

向后兼容入口。真源在 ``zephyr.signal_fundamental.strategy.implementations.default_capital_allocator``
（MATURITY=production）。本文件原为完整实现副本，与真源完全相同导致多真源漂移风险，
已收敛为 re-export shim。禁止在此重复定义实现。
"""

from __future__ import annotations

from zephyr.signal_fundamental.strategy.implementations.default_capital_allocator import (
    AllocationMethod,
    DefaultCapitalAllocator,
)

__all__ = ["AllocationMethod", "DefaultCapitalAllocator"]
