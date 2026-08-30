# [A_module] module_id=MOD-INF-components | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations
#   code: __init__.py import L32
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 fitness_functions, gate_statistics, knowledge_overview, olap_trend, task_pr…
#   desc: __init__ import L32；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: fitness_functions, gate_statistics, knowledge_overview, olap_trend, task_progre…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.infrastructure.dashboard.components
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent

__all__ = ["fitness_functions", "gate_statistics", "knowledge_overview", "olap_trend", "task_progress"]
