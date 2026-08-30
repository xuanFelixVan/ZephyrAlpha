# [BLUEPRINT] MOD-INF-016 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-UNK-pf_alloc | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Final, batched_position_builder
#   code: __init__.py import L34
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Final, batched_position_builder（共 2 符号）
#   desc: __init__ import L34；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: Final, batched_position_builder
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

from zephyr.pf_alloc import (
    batched_position_builder,  # noqa: F401  # ORPHAN-MODULE: 新模块引用登记（41_buy_flow MOD-PA-006）
)

__all__: Final = ["strategy_lifecycle_event", "batched_position_builder"]
