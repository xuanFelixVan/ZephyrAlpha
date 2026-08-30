# [A_module] module_id=MOD-SHR-escalation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.contracts.escalation
# [INVARIANTS] BudgetAlert 告警阈值不可被静默;告警事件必须可审计
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.budget_enforcement;zephyr.security.escalation
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_budget_enforcer.py
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: BudgetAlert, BudgetSeverity, BudgetType
#   code: __init__.py import L44
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BudgetAlert, BudgetSeverity, BudgetType, budget_alert（共 4 符号）
#   desc: __init__ import L44；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: BudgetAlert, BudgetSeverity, BudgetType, budget_alert
#   downstream: zephyr.security.budget_enforcement;zephyr.security.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType

__all__ = [
    "BudgetAlert",
    "BudgetSeverity",
    "BudgetType",
    "budget_alert",
]
