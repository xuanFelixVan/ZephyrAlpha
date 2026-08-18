# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §12
# [MODULE] zephyr.governance.agent_spec.rbac_bridge
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.budget_enforcement
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] RBAC配额降级规则不可绕过;权限降级必须审计
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 budget_context 和 operation_id
# [TESTS] tests/test_budget_enforcer.py
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget-enforcer/blueprint.md | §12

G-CT-007 契约：Budget -> RBAC 配额限制.
G-CT-005 契约：Escalation -> RBAC 权限升级 + Pipeline 前置 RBAC 检查.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

_logger = logging.getLogger(__name__)

_AGENT_RBAC_AVAILABLE = False
try:
    from zephyr.security.access_control.guards.permission_guard import (
        GuardDecision,
        GuardResult,
        PermissionGuard,
    )
    from zephyr.shared.contracts.identity.agent_identity import (
        AgentIdentity,
        AgentRole,
        IDESource,
        MaturityLevel,
    )
    _AGENT_RBAC_AVAILABLE = True
except ImportError:
    pass


class BudgetRBACBridge:
    """预算消耗->RBAC权限降级."""

    def evaluate_budget(self, agent_id: str, token_used: int, token_limit: int) -> dict:
        """评估预算消耗并返回配额裁决（5.177 修复：原名 check_budget，
        返回 dict 违反 check_ 前缀返回布尔的命名直觉，更名 evaluate_budget）。"""
        exceeded = token_used > token_limit

        return {
            "agent_id": agent_id,
            "token_used": token_used,
            "token_limit": token_limit,
            "exceeded": exceeded,
            "action": "REVOKE_WRITE" if exceeded else "ALLOW",
        }

    def check_budget(self, agent_id: str, token_used: int, token_limit: int) -> dict:
        """向后兼容别名 — 委托到 evaluate_budget（测试 SSoT）。"""
        return self.evaluate_budget(agent_id, token_used, token_limit)


@dataclass
class RBACCheckResult:
    passed: bool = True
    decision: str = "ALLOW"
    layer: str = ""
    rule_id: str = ""
    reason: str = ""
    audit_context: dict[str, Any] = field(default_factory=dict)


class EscalationRBACBridge:
    """升级事件->RBAC权限提升 + Pipeline 前置 RBAC 检查."""

    def __init__(self) -> None:
        self._guard = PermissionGuard() if _AGENT_RBAC_AVAILABLE else None

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def guard(self):
        """只读：guard（Stage 4 公共化）。"""
        return self._guard

    @guard.setter
    def guard(self, value):
        """写入：guard（Stage 4 公共化）。"""
        self._guard = value


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
                session_id=session_id,
                role=AgentRole.AUTONOMOUS_AGENT,
                ide_source=IDESource.TRAE,
                maturity=MaturityLevel.L0_INTERN,
                auto_guard_eligible=True,
            )
            guard_result: GuardResult = self._guard.check(
                identity,
                operation=operation,
                target_path=target_path or "",
            )
            if guard_result.decision is GuardDecision.BLOCKED:
                return RBACCheckResult(
                    passed=False,
                    decision="BLOCK",
                    layer="permission_guard",
                    rule_id=guard_result.rule_id or "AUTO_GUARD",
                    reason=guard_result.reason,
                    audit_context={"target": getattr(guard_result, "target", "")},
                )
            return RBACCheckResult(
                passed=True,
                decision="ALLOW",
                layer="permission_guard",
                rule_id=guard_result.rule_id or "AUTO_ALLOW",
                reason=guard_result.reason,
                audit_context={"target": getattr(guard_result, "target", "")},
            )
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.warning("RBAC pre_execute_check failed: %s", exc, exc_info=True)
            return RBACCheckResult(
                passed=False,
                decision="BLOCK",
                layer="rbac_bridge",
                rule_id="RBAC_EXCEPTION",
                reason=str(exc),
            )


__all__ = ["BudgetRBACBridge", "EscalationRBACBridge", "RBACCheckResult"]
