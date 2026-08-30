# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.strategy.capital_allocator
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_fundamental.gen.aggregator_base; zephyr.trading.trading_contracts.execution.capital_allocation_result
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L03-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: signal
# category: allocation
# status: active
# created: "2026-05-05"
# ---

"""
D_FUNDAMENTAL_SIGNAL — Capital Allocator（兼容导出）

``CapitalAllocatorBase`` 真源在 ``zephyr.signal_fundamental.gen.aggregator_base``。
``CapitalAllocationResult`` 真源在 ``zephyr.trading.trading_contracts.execution.capital_allocation_result``（CTR-P1-003）。

本模块仅作向后兼容 re-export，禁止在此重复定义契约类型或 ABC。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: capital_allocator.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 CapitalAllocationResult, CapitalAllocatorBase（共 2 符号）
#   desc: __init__ import L0；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: CapitalAllocationResult, CapitalAllocatorBase
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.signal_fundamental.gen.aggregator_base import CapitalAllocatorBase
from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult

__all__ = ["CapitalAllocationResult", "CapitalAllocatorBase"]
