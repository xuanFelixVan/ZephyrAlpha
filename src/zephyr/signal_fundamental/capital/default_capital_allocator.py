# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.capital.default_capital_allocator
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_fundamental.strategy.implementations.default_capital_allocator
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
# category: allocation_implementation
# status: active
# created: "2026-05-05"
# ---

"""
D_SIGNAL — Default Capital Allocator（兼容 re-export shim）

向后兼容入口。真源在 ``zephyr.signal_fundamental.strategy.implementations.default_capital_allocator``
（MATURITY=production）。本文件原为完整实现副本，与真源完全相同导致多真源漂移风险，
已收敛为 re-export shim。禁止在此重复定义实现。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: default_capital_allocator.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AllocationMethod, DefaultCapitalAllocator（共 2 符号）
#   desc: __init__ import L0；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: AllocationMethod, DefaultCapitalAllocator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.signal_fundamental.strategy.implementations.default_capital_allocator import (
    AllocationMethod,
    DefaultCapitalAllocator,
)

__all__ = ["AllocationMethod", "DefaultCapitalAllocator"]
