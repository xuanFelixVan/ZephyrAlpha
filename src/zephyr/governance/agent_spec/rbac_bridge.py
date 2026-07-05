# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §12
# [MODULE] zephyr.governance.agent_spec.rbac_bridge
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.budget_enforcement
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] RBAC配额降级规则不可绕过;权限降级必须审计
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 budget_context 和 operation_id
# [TESTS] tests/test_budget_enforcer.py
# [A_module] module_id=MOD-RES_rbac_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""[BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget-enforcer/blueprint.md | §12

G-CT-007 契约：Budget → RBAC 配额限制.
G-CT-005 契约：Escalation → RBAC 权限升级 + Pipeline 前置 RBAC 检查.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

_logger = logging.getLogger(__name__)

_AGENT_RBAC_AVAILABLE = False
try:
    from zephyr.shared.contracts.identity.agent_identity import (
        AgentIdentity, AgentRole, IDESource, MaturityLevel,
    )
    from zephyr.shared.contracts.identity.permission import GuardDecision, GuardResult
    from zephyr.security.access_control.guards.permission_guard import PermissionGuard
    _AGENT_RBAC_AVAILABLE = True
except ImportError:
    pass


class BudgetRBACBridge:
    """预算消耗→RBAC权限降级."""

    def check_budget(self, agent_id: str, token_used: int, token_limit: int) -> dict:
        exceeded = token_used > token_limit

        return {
            "agent_id": agent_id,
            "token_used": token_used,
            "token_limit": token_limit,
            "exceeded": exceeded,
            "action": "REVOKE_WRITE" if exceeded else "ALLOW",
        }


@dataclass
class RBACCheckResult:
    passed: bool = True
    decision: str = "ALLOW"
    layer: str = ""
    rule_id: str = ""
    reason: str = ""
    audit_context: dict[str, Any] = field(default_factory=dict)


class EscalationRBACBridge:
    """升级事件→RBAC权限提升 + Pipeline 前置 RBAC 检查."""

    def __init__(self) -> None:
        self._guard = PermissionGuard() if _AGENT_RBAC_AVAILABLE else None

    def request_escalation(self, agent_id: str, target_permission: str, reason: str) -> dict:
        return {
            "agent_id": agent_id,
            "target_permission": target_permission,
            "reason": reason,
            "status": "PENDING_OWNER_APPROVAL",
        }

    def pre_execute_check(self, session_id: str, operation: str, target_path: str = "") -> RBACCheckResult:
        if not _AGENT_RBAC_AVAILABLE:
            return RBACCheckResult(
                passed=True,
                decision="ALLOW",
                layer="rbac_bridge",
                rule_id="AGENT_RBAC_UNAVAILABLE",
                reason="agent_rbac contracts not available, fail-open",
            )

        try:
            identity = AgentIdentity(
                agent_id=session_id,
                role=AgentRole.AUTONOMOUS_AGENT,
                ide_source=IDESource.TRAE,
                maturity=MaturityLevel.PROTOTYPE,
            )
            guard_result: GuardResult = self._guard.check(
                identity=identity,
                operation=operation,
                target_path=target_path or None,
            )
            if guard_result.decision is GuardDecision.BLOCKED:
                return RBACCheckResult(
                    passed=False,
                    decision="BLOCK",
                    layer="permission_guard",
                    rule_id=guard_result.rule_id or "AUTO_GUARD",
                    reason=guard_result.reason,
                    audit_context=guard_result.audit_context or {},
                )
            return RBACCheckResult(
                passed=True,
                decision="ALLOW",
                layer="permission_guard",
                rule_id=guard_result.rule_id or "AUTO_ALLOW",
                reason=guard_result.reason,
                audit_context=guard_result.audit_context or {},
            )
        except Exception as exc:
            _logger.warning("RBAC pre_execute_check failed: %s", exc)
            return RBACCheckResult(
                passed=False,
                decision="BLOCK",
                layer="rbac_bridge",
                rule_id="RBAC_EXCEPTION",
                reason=str(exc),
            )


__all__ = ["BudgetRBACBridge", "EscalationRBACBridge", "RBACCheckResult"]
