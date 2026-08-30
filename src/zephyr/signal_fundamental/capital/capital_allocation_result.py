# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.capital.capital_allocation_result
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.trading.trading_contracts.execution.capital_allocation_result
# [CONSUMERS] signal
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L03-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D_FUNDAMENTAL_SIGNAL — CapitalAllocationResult re-export shim

向后兼容入口。真源在 ``zephyr.trading.trading_contracts.execution.capital_allocation_result``
（CTR-P1-003 跨层契约 SSoT）。本文件原为完整定义副本，与真源完全相同导致多真源漂移风险，
已收敛为 re-export shim。禁止在此重复定义契约类型——多真源同步漂移根因。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: capital_allocation_result.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 CapitalAllocationResult（共 1 符号）
#   desc: __init__ import L0；__all__ 1 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: CapitalAllocationResult
#   downstream: signal
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult

__all__ = ["CapitalAllocationResult"]
