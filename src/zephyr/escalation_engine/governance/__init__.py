# [BLUEPRINT] MOD-INF-022 | src/zephyr/escalation_engine/governance/__init__.py | §
"""
Escalation — MOD-INF-022

升级协议：异常事件阶梯升级 L0-L4 + Owner通知.
"""
from . import a2a_failure
from . import budget_handler

from zephyr.escalation_engine.governance.contracts import EscalationContracts
from zephyr.escalation_engine.governance.rbac_bridge import EscalationRBACBridge, RBACCheckResult
from zephyr.escalation_engine.governance.approval import ApprovalRequest

__all__ = [
    'a2a_failure', 'approval', 'budget_handler', 'contracts', 'rbac_bridge', 'on_budget_alert',
    'EscalationContracts', 'EscalationRBACBridge', 'RBACCheckResult', 'ApprovalRequest',
]


__version__ = "0.1.0"
__module_id__ = "MOD-INF-022"