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
# [TTL] task_bound
"""
Escalation — MOD-INF-022

升级协议：异常事件阶梯升级 L0-L4 + Owner通知.
"""

from zephyr.governance.approval import ApprovalRequest  # noqa: E402
from zephyr.governance.contracts import EscalationContracts  # noqa: E402
from zephyr.governance.rbac_bridge import EscalationRBACBridge, RBACCheckResult  # noqa: E402

# ARCH-031: 8 stale duplicates removed (approval/contracts/a2a_failure/budget_handler/
# budget_tracker/drift_fix/auditor/result_types) — canonicals exist in access_control/,
# integration/, budget/, drift/, audit/, shared/, infrastructure/rollback/governance/.
# Remaining: rbac_bridge.py (imported by access_control/rbac_bridge.py) +
# data_quality.py (imported by tests/data/test_data_quality.py).
__all__ = [  # noqa: gate-vocab  __all__ 子包导出列表，非 domain 分类
    "ApprovalRequest",
    "EscalationContracts",
    "EscalationRBACBridge",
    "RBACCheckResult",
    "data_quality",
    "rbac_bridge",
]

__version__ = "0.1.0"
__module_id__ = "MOD-INF-022"
