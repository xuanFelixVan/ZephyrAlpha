# [A_module] module_id=MOD-SHR-escalation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.escalation
# [INVARIANTS] BudgetAlert 告警阈值不可被静默;告警事件必须可审计
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.budget_enforcement;zephyr.security.escalation
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] none  # 2026-09-05 AI-00：全仓无测试 import 本模块（原声明路径不存在）
# [TTL] permanent

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/contracts/escalation/escalation__init__.yaml
"""

from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType

__all__ = [
    "BudgetAlert",
    "BudgetSeverity",
    "BudgetType",
    "budget_alert",
]
