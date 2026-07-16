# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.capital.capital_allocation_result
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.trading.trading_contracts.execution.capital_allocation_result
# [CONSUMERS] signal
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_capital_allocation_result | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_FUNDAMENTAL_SIGNAL — CapitalAllocationResult re-export shim

向后兼容入口。真源在 ``zephyr.trading.trading_contracts.execution.capital_allocation_result``
（CTR-P1-003 跨层契约 SSoT）。本文件原为完整定义副本，与真源完全相同导致多真源漂移风险，
已收敛为 re-export shim。禁止在此重复定义契约类型——多真源同步漂移根因。
"""

from __future__ import annotations

from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult

__all__ = ["CapitalAllocationResult"]
