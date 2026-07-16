# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.capital.capital_allocator
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_fundamental.strategy.capital_allocator
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
# [A_module] module_id=MOD-UNK_capital_allocator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: signal
# category: allocation
# status: active
# created: "2026-05-05"
# ---

"""D_SIGNAL — Capital Allocator（兼容 re-export shim）

向后兼容入口。真源在 ``zephyr.signal_fundamental.strategy.capital_allocator``（同真源
``aggregator_base.CapitalAllocatorBase`` + ``trading_contracts...CapitalAllocationResult``）。
禁止在此重复定义契约类型或 ABC——多真源同步漂移根因。
"""

from __future__ import annotations

from zephyr.signal_fundamental.strategy.capital_allocator import (
    CapitalAllocationResult,
    CapitalAllocatorBase,
)

__all__ = ["CapitalAllocationResult", "CapitalAllocatorBase"]
