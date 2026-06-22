# [A_module] module_id=MOD-GOV_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [MODULE] zephyr.security.escalation.governance
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""
Escalation — MOD-INF-022

升级协议：异常事件阶梯升级 L0-L4 + Owner通知.
"""

from zephyr.governance.approval import ApprovalRequest
from zephyr.governance.contracts import EscalationContracts
from zephyr.governance.rbac_bridge import EscalationRBACBridge, RBACCheckResult

from . import a2a_failure, budget_handler

__all__ = [
    "ApprovalRequest",
    "EscalationContracts",
    "EscalationRBACBridge",
    "RBACCheckResult",
    "a2a_failure",
    "approval",
    "auditor",
    "budget_handler",
    "budget_tracker",
    "contracts",
    "data_quality",
    "drift_fix",
    "on_budget_alert",
    "rbac_bridge",
    "result_types",
]

__version__ = "0.1.0"
__module_id__ = "MOD-INF-022"
