# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.rbac_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] READER never allowed write; L0_INTERN never allowed modify:blueprint
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check() never raises; returns PermissionResult with decision
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_rbac_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RBACGuard — 基于角色的权限守卫.

依据蓝图 MOD-INF-018 §3:
- 基于角色判断操作权限
- READER 不能写
- L0_INTERN 不能修改蓝图
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from zephyr.security.access_control.identity import (
    ROLE_DEFAULT_PERMISSIONS,
    AgentRole,
    MaturityLevel,
)
from zephyr.security.access_control.immutable_core import (
    ALWAYS_BLOCKED_OPERATIONS,
    PROTECTED_PATHS,
)


ALWAYS_ALLOW_OPERATIONS = [
    "read:docs",
    "read:src",
    "read:tests",
    "read:config",
    "code_search",
]

AUTO_GUARD_OPERATIONS = [
    "write:src",
    "write:tests",
    "execute:scripts",
    "execute:tests",
]


def _normalize_op(operation: str) -> str:
    """操作名规范化：冒号/连字符/空格统一转为下划线，便于匹配 immutable_core 真源。"""
    return operation.lower().replace(":", "_").replace("-", "_").replace(" ", "_")


class PermissionDecision(str, Enum):
    """权限决策枚举."""

    ALLOW = "ALLOW"
    BLOCKED = "BLOCKED"
    AUTO_GUARD = "AUTO_GUARD"


@dataclass
class PermissionResult:
    """权限检查结果.

    Attributes:
        decision: 决策（ALLOW/BLOCKED/AUTO_GUARD）
        reason: 决策原因
        layer: 检查层
        auto_guard_timeout: auto-guard 超时时间（秒）
        requires_owner_review: 是否需要 Owner 审查
        audit_context: 审计上下文
    """

    decision: PermissionDecision
    reason: str = ""
    layer: str = "L1_rbac"
    auto_guard_timeout: int = 300
    requires_owner_review: bool = False
    audit_context: dict = field(default_factory=dict)


class RBACGuard:
    """基于角色的权限守卫.

    根据角色和成熟度判断操作权限。
    """

    def __init__(self, immutable_core: object = None) -> None:
        self._immutable_core = immutable_core

    def check(
        self,
        agent: object,
        operation: str,
        target_path: str | None = None,
    ) -> PermissionResult:
        """检查操作权限.

        Args:
            agent: AgentIdentity 实例
            operation: 操作名称
            target_path: 操作目标路径（可选，用于受保护路径检查）

        Returns:
            PermissionResult 包含决策和原因
        """
        role = getattr(agent, "role", None)
        maturity = getattr(agent, "maturity", None)

        # 按优先级顺序执行权限检查链（惰性求值，首个非 None 结果即返回）
        checkers = (
            lambda: self._check_immutable_core_op(operation),
            lambda: self._check_always_blocked_op(operation),
            lambda: self._check_protected_path(agent, target_path),
            lambda: self._check_reader_write(role, operation),
            lambda: self._check_intern_modify(maturity, operation),
            lambda: self._check_always_allow_op(operation),
            lambda: self._check_auto_guard_op(agent, operation),
            lambda: self._check_role_permission(role, operation),
            lambda: self._check_explicit_permission(agent, operation),
            lambda: self._check_owner_approved(agent),
        )
        for checker in checkers:
            result = checker()
            if result is not None:
                return result

        # 默认阻止
        return PermissionResult(
            decision=PermissionDecision.BLOCKED,
            reason="no permission granted",
            layer="L1_rbac",
        )

    # ===== 权限检查链各步骤（返回 None 表示继续下一步） =====

    def _check_immutable_core_op(self, operation: str) -> PermissionResult | None:
        """L0 immutable_core 修改阻断。"""
        if "immutable_core" in operation:
            return PermissionResult(
                decision=PermissionDecision.BLOCKED,
                reason="L0 immutable_core cannot be modified",
                layer="L0",
            )
        return None

    def _check_always_blocked_op(self, operation: str) -> PermissionResult | None:
        """永远阻止的操作（规范化后匹配 immutable_core 真源）。"""
        if _normalize_op(operation) in ALWAYS_BLOCKED_OPERATIONS:
            return PermissionResult(
                decision=PermissionDecision.BLOCKED,
                reason=f"always blocked: {operation}",
                layer="L1_rbac",
            )
        return None

    def _check_protected_path(
        self, agent: object, target_path: str | None
    ) -> PermissionResult | None:
        """受保护路径检查（immutable_core 真源，glob 模式匹配）。

        ADMIN / AUDITOR 角色可读访问受保护路径（审计/管理需要）。
        """
        if not target_path:
            return None
        from fnmatch import fnmatch

        role = getattr(agent, "role", None)
        role_value = str(getattr(role, "value", role)).lower() if role else ""
        if role_value in ("admin", "auditor"):
            return None
        for pattern in PROTECTED_PATHS:
            base = pattern.replace("/**", "").rstrip("*")
            if base and (target_path.startswith(base) or fnmatch(target_path, pattern)):
                return PermissionResult(
                    decision=PermissionDecision.BLOCKED,
                    reason=f"protected path: {target_path}",
                    layer="L1_rbac",
                )
        return None

    def _check_reader_write(
        self, role: object, operation: str
    ) -> PermissionResult | None:
        """READER 不能写。"""
        if role is AgentRole.READER and operation.startswith("write:"):
            return PermissionResult(
                decision=PermissionDecision.BLOCKED,
                reason="READER cannot write",
                layer="L1_rbac",
            )
        return None

    def _check_intern_modify(
        self, maturity: object, operation: str
    ) -> PermissionResult | None:
        """L0_INTERN 不能修改蓝图。"""
        if maturity is MaturityLevel.L0_INTERN and operation.startswith("modify:"):
            return PermissionResult(
                decision=PermissionDecision.BLOCKED,
                reason=f"INTERN cannot modify: {operation}",
                layer="L1_rbac",
            )
        return None

    def _check_always_allow_op(self, operation: str) -> PermissionResult | None:
        """永远允许的操作。"""
        if operation in ALWAYS_ALLOW_OPERATIONS:
            return PermissionResult(
                decision=PermissionDecision.ALLOW,
                reason=f"always allowed: {operation}",
                layer="L1_rbac",
            )
        return None

    def _check_auto_guard_op(
        self, agent: object, operation: str
    ) -> PermissionResult | None:
        """AUTO_GUARD 操作 — 在角色权限检查之前判定。"""
        if operation not in AUTO_GUARD_OPERATIONS:
            return None
        if getattr(agent, "auto_guard_eligible", False):
            timeout = 0
            if hasattr(agent, "get_auto_guard_timeout"):
                timeout = agent.get_auto_guard_timeout()
            return PermissionResult(
                decision=PermissionDecision.AUTO_GUARD,
                reason="auto-guard eligible",
                layer="L1_rbac",
                auto_guard_timeout=timeout,
            )
        if getattr(agent, "owner_approved", False):
            return PermissionResult(
                decision=PermissionDecision.ALLOW,
                reason="owner approved",
                layer="L1_rbac",
            )
        return PermissionResult(
            decision=PermissionDecision.BLOCKED,
            reason="auto-guard not eligible and not owner approved",
            layer="L1_rbac",
        )

    def _check_role_permission(
        self, role: object, operation: str
    ) -> PermissionResult | None:
        """角色权限检查 — 精确匹配 + 通配符匹配（如 admin:*）。"""
        role_perms = ROLE_DEFAULT_PERMISSIONS.get(role, [])
        if operation in role_perms:
            return PermissionResult(
                decision=PermissionDecision.ALLOW,
                reason=f"allowed by role {role.value if role else 'unknown'}",
                layer="L1_rbac",
            )
        for perm in role_perms:
            if perm.endswith(":*") and operation.startswith(perm[:-1]):
                return PermissionResult(
                    decision=PermissionDecision.ALLOW,
                    reason=f"allowed by wildcard {perm}",
                    layer="L1_rbac",
                )
        return None

    def _check_explicit_permission(
        self, agent: object, operation: str
    ) -> PermissionResult | None:
        """显式权限检查 — 精确匹配 + 通配符匹配。"""
        explicit_perms = getattr(agent, "permissions", None) or []
        if operation in explicit_perms:
            return PermissionResult(
                decision=PermissionDecision.ALLOW,
                reason="allowed by explicit permission",
                layer="L1_rbac",
            )
        for perm in explicit_perms:
            if perm.endswith(":*") and operation.startswith(perm[:-1]):
                return PermissionResult(
                    decision=PermissionDecision.ALLOW,
                    reason=f"allowed by wildcard {perm}",
                    layer="L1_rbac",
                )
        return None

    def _check_owner_approved(self, agent: object) -> PermissionResult | None:
        """owner_approved 允许未知操作。"""
        if getattr(agent, "owner_approved", False):
            return PermissionResult(
                decision=PermissionDecision.ALLOW,
                reason="owner approved",
                layer="L1_rbac",
            )
        return None

    def is_blocked(self, result: PermissionResult) -> bool:
        """判断结果是否为 BLOCKED."""
        return result.decision is PermissionDecision.BLOCKED

    def is_auto_guard(self, result: PermissionResult) -> bool:
        """判断结果是否为 AUTO_GUARD."""
        return result.decision is PermissionDecision.AUTO_GUARD


__all__ = [
    "ALWAYS_ALLOW_OPERATIONS",
    "ALWAYS_BLOCKED_OPERATIONS",
    "AUTO_GUARD_OPERATIONS",
    "PROTECTED_PATHS",
    "PermissionDecision",
    "PermissionResult",
    "RBACGuard",
]
