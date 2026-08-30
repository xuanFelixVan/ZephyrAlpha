# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.permission_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ALWAYS_BLOCKED_OPERATIONS always blocked regardless of role/maturity; seven-layer orchestration
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check() never raises; returns GuardResult with decision
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
PermissionGuard — 七层权限编排器.

依据蓝图 MOD-INF-018 §3:
- 编排七层检查（L0-L6）
- ALWAYS_BLOCKED_OPERATIONS 永远 BLOCKED
- 角色权限决定 ALLOW/AUTO_GUARD

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: permission_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① PermissionGuard
#   name_en: PermissionGuard
#   intro: 七层权限编排器.
#   desc: 七层权限编排器. 编排 L0-L6 七层检查，决定操作是否允许。；公共方法（定义序）: l0, l1, is_blocked, explain, check；源码 L78-L235
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: PermissionGuard
#   downstream: tests/agent_rbac/test_redteam_adversarial.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time

from zephyr.security.access_control.identity import (
    ROLE_DEFAULT_PERMISSIONS,
    AgentRole,
)
from zephyr.security.access_control.immutable_core import ALWAYS_BLOCKED_OPERATIONS

# SSoT 收敛（#ARCH-106）：GuardDecision/GuardResult 真源为 shared.contracts.identity.permission，
# 本模块 re-export 兼容既有导入方。此前本模块与 contracts 各自定义同名枚举，
# `decision is GuardDecision.BLOCKED` 跨定义恒 False，会把 BLOCKED 静默折叠为放行（fail-open）。
from zephyr.shared.contracts.identity.permission import GuardDecision, GuardResult

_CRITICAL_OPERATIONS = {
    "circumvent_gate_engine",
    "bypass_rbac",
    "disable_rbac",
    "circumvent_rbac",
    "disable_audit",
    "bypass_audit",
    "circumvent_permission_guard",
}


class PermissionGuard:
    """七层权限编排器.

    编排 L0-L6 七层检查，决定操作是否允许。
    """

    def __init__(self) -> None:
        from zephyr.security.access_control.guards.rbac_guard import RBACGuard
        from zephyr.security.access_control.immutable_core import ImmutableCore

        self._l0 = ImmutableCore()
        self._l1 = RBACGuard()

    # Stage 4 公共化：l0/l1 公共属性（primary），私有属性向后兼容 thin wrapper。
    # 测试可通过公共属性读写 L0/L1 守卫，无需耦合内部实现。
    @property
    def l0(self):
        """L0 不可变核心层守卫（Stage 4 公共化，primary）。"""
        return self._l0

    @l0.setter
    def l0(self, value) -> None:
        self._l0 = value

    @property
    def l1(self):
        """L1 RBAC 守卫（Stage 4 公共化，primary）。"""
        return self._l1

    @l1.setter
    def l1(self, value) -> None:
        self._l1 = value

    def is_blocked(self, result: GuardResult) -> bool:
        """判断结果是否为 BLOCKED."""
        return result.decision is GuardDecision.BLOCKED

    def explain(self, result: GuardResult) -> dict:
        """解释 GuardResult，返回包含 blocked_layer 的字典."""
        return {
            "decision": result.decision.value if hasattr(result.decision, "value") else str(result.decision),
            "reason": result.reason,
            "blocked_layer": result.layer,
            "rule_id": result.rule_id,
            "target": result.target,
        }

    def check(self, agent: object, operation: str, target_path: str = "") -> GuardResult:
        """检查操作权限.

        Args:
            agent: AgentIdentity 实例
            operation: 操作名称（如 "write:src", "read:docs"）
            target_path: 目标路径（可选）

        Returns:
            GuardResult 包含决策、原因、层、目标、耗时
        """
        start_ns = time.perf_counter_ns()
        result = self._evaluate(agent, operation, target_path)
        result.timing_ns = time.perf_counter_ns() - start_ns
        return result

    def _evaluate(self, agent: object, operation: str, target_path: str) -> GuardResult:
        """执行权限检查逻辑（内部方法）."""
        # L0: 不可变核心检查 — ALWAYS_BLOCKED_OPERATIONS 永远阻止
        if operation in ALWAYS_BLOCKED_OPERATIONS:
            return GuardResult(
                decision=GuardDecision.BLOCKED,
                reason=f"operation in ALWAYS_BLOCKED_OPERATIONS: {operation}",
                layer="L0_immutable_core",
                target=target_path,
            )

        # L0: 额外关键操作黑名单
        if operation in _CRITICAL_OPERATIONS:
            return GuardResult(
                decision=GuardDecision.BLOCKED,
                reason=f"critical operation blocked: {operation}",
                layer="L0_immutable_core",
                target=target_path,
            )

        # L6: 自防 — RBAC 系统修改
        if operation.startswith("modify:rbac") or operation == "modify:rbac_roles":
            role = getattr(agent, "role", None)
            if role is not AgentRole.ADMIN:
                return GuardResult(
                    decision=GuardDecision.BLOCKED,
                    reason="non-admin cannot modify RBAC system",
                    layer="L6_self_defense",
                    target=target_path,
                )
            return GuardResult(
                decision=GuardDecision.AUTO_GUARD,
                reason="admin RBAC modification requires auto-guard",
                layer="L6_self_defense",
                target=target_path,
            )

        # L4: 危险操作 — delete 默认阻止
        if operation.startswith("delete:"):
            return GuardResult(
                decision=GuardDecision.BLOCKED,
                reason="delete operations blocked by default",
                layer="L4_path_guard",
                target=target_path,
            )

        # L1: RBAC 角色权限检查
        role = getattr(agent, "role", None)
        role_perms = ROLE_DEFAULT_PERMISSIONS.get(role, [])

        # 精确匹配
        if operation in role_perms:
            return GuardResult(
                decision=GuardDecision.ALLOW,
                reason=f"allowed by role {role.value if role else 'unknown'}",
                layer="L1_rbac",
                target=target_path,
            )

        # 通配符匹配（如 admin:*）
        for perm in role_perms:
            if perm.endswith(":*") and operation.startswith(perm[:-1]):
                return GuardResult(
                    decision=GuardDecision.ALLOW,
                    reason=f"allowed by wildcard {perm}",
                    layer="L1_rbac",
                    target=target_path,
                )

        # 显式权限检查
        explicit_perms = getattr(agent, "permissions", None) or []
        if operation in explicit_perms:
            return GuardResult(
                decision=GuardDecision.ALLOW,
                reason="allowed by explicit permission",
                layer="L1_rbac",
                target=target_path,
            )

        # AUTO_GUARD 检查
        if getattr(agent, "auto_guard_eligible", False):
            return GuardResult(
                decision=GuardDecision.AUTO_GUARD,
                reason="auto-guard eligible",
                layer="L1_rbac",
                target=target_path,
            )

        # 默认阻止
        return GuardResult(
            decision=GuardDecision.BLOCKED,
            reason="no permission granted",
            layer="L1_rbac",
            target=target_path,
        )


__all__ = [
    "GuardDecision",
    "GuardResult",
    "PermissionGuard",
]
