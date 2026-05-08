"""G-CT-005 契约：Escalation → RBAC 权限升级 + Pipeline 前置 RBAC 检查."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

_logger = logging.getLogger(__name__)

_AGENT_RBAC_AVAILABLE = False
try:
    from zephyr.agent_rbac.identity import AgentIdentity, AgentRole, MaturityLevel, IDESource  # noqa: F401
    from zephyr.agent_rbac.permission_guard import PermissionGuard, GuardDecision  # noqa: F401
    _AGENT_RBAC_AVAILABLE = True
except ImportError:
    pass


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

    def request_escalation(
        self, agent_id: str, target_permission: str, reason: str
    ) -> dict:
        return {
            "agent_id": agent_id,
            "target_permission": target_permission,
            "reason": reason,
            "status": "PENDING_OWNER_APPROVAL",
        }

    def pre_execute_check(
        self, session_id: str, operation: str, target_path: str = ""
    ) -> RBACCheckResult:
        try:
            from zephyr.escalation.adapter import check_operation
            esc_decision = check_operation(operation, target_path, session_id)
            if esc_decision.should_block:
                return RBACCheckResult(
                    passed=False,
                    decision="BLOCKED",
                    reason=f"Escalation blocked: {esc_decision.reason}",
                    audit_context={"escalation": esc_decision.escalation_level, "circuit_state": esc_decision.circuit_state},
                )
        except ImportError:
            pass

        if not _AGENT_RBAC_AVAILABLE or self._guard is None:
            return RBACCheckResult(passed=True, reason="RBAC not available — pass-through")

        try:
            identity = AgentIdentity(
                session_id=session_id,
                maturity=MaturityLevel.L2_REGULAR,
                role=AgentRole.EXECUTOR,
                ide_source=IDESource.CLI,
                owner_approved=True,
            )
            result = self._guard.check(identity, operation, target_path)

            if result.decision == GuardDecision.BLOCKED:
                return RBACCheckResult(
                    passed=False,
                    decision="BLOCKED",
                    layer=result.layer,
                    rule_id=result.rule_id,
                    reason=result.reason,
                    audit_context=result.audit_context,
                )

            if result.decision == GuardDecision.AUTO_GUARD:
                return RBACCheckResult(
                    passed=True,
                    decision="AUTO_GUARD",
                    layer=result.layer,
                    rule_id=result.rule_id,
                    reason=result.reason,
                    audit_context=result.audit_context,
                )

            return RBACCheckResult(
                passed=True,
                decision="ALLOW",
                layer=result.layer,
                reason=result.reason,
            )

        except Exception as exc:
            _logger.warning("RBAC check failed: %s — pass-through", exc)
            return RBACCheckResult(passed=True, reason=f"RBAC error: {exc} — pass-through")
