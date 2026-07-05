# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain-signal/signal-generation-core/blueprint.md
# [MODULE] zephyr.signal_fundamental.capital.capital_allocator
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_fundamental.gen.aggregator_base; zephyr.trading.trading_contracts.execution.capital_allocation_result
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

"""D_SIGNAL — Capital Allocator（兼容导出）

``CapitalAllocatorBase`` 真源在 ``aggregator_base.py``（与 ``SignalAggregatorBase`` / ``DegradationMonitorBase`` 同文件）。
``CapitalAllocationResult`` 真源在 ``zephyr.shared.contracts.capital_allocation_result``（CTR-P1-003）。

本模块仅作向后兼容 re-export，禁止在此重复定义契约类型或 ABC。
"""

from __future__ import annotations

from zephyr.signal_fundamental.gen.aggregator_base import CapitalAllocatorBase
from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult

__all__ = ["CapitalAllocationResult", "CapitalAllocatorBase"]
