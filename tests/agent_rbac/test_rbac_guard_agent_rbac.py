# [A_test] module_id: MOD-GOV_rbac_guard_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_rbac_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试 L1 RBACGuard — 三层权限模型
"""

from zephyr.security.access_control.guards.rbac_guard import (
    ALWAYS_ALLOW_OPERATIONS,
    PermissionDecision,
    PermissionResult,
    RBACGuard,
)
from zephyr.security.access_control.identity import AgentIdentity, AgentRole, MaturityLevel


class TestRBACGuardAllow:
    def test_read_operations_always_allowed(self):
        guard = RBACGuard()
        agent = AgentIdentity(session_id="test-read")
        result = guard.check(agent, "read:docs")
        assert result.decision == PermissionDecision.ALLOW
        assert not guard.is_blocked(result)

    def test_always_allow_operations(self):
        guard = RBACGuard()
        agent = AgentIdentity(session_id="test-always")
        for op in ALWAYS_ALLOW_OPERATIONS[:5]:
            result = guard.check(agent, op)
            assert result.decision == PermissionDecision.ALLOW, f"Expected ALLOW for '{op}'"

    def test_explicit_permission_granted(self):
        guard = RBACGuard()
        agent = AgentIdentity(
            session_id="test-explicit",
            permissions=["custom:operation"],
        )
        result = guard.check(agent, "custom:operation")
        assert result.decision == PermissionDecision.ALLOW

    def test_owner_approved_allows_unknown_operation(self):
        guard = RBACGuard()
        agent = AgentIdentity(
            session_id="test-owner",
            owner_approved=True,
        )
        result = guard.check(agent, "unknown:operation")
        assert result.decision == PermissionDecision.ALLOW


class TestRBACGuardAutoGuard:
    def test_auto_guard_operations(self):
        guard = RBACGuard()
        agent = AgentIdentity(
            session_id="test-ag",
            auto_guard_eligible=True,
        )
        result = guard.check(agent, "write:src")
        assert result.decision == PermissionDecision.AUTO_GUARD
        assert guard.is_auto_guard(result)

    def test_auto_guard_not_eligible_blocked(self):
        guard = RBACGuard()
        agent = AgentIdentity(
            session_id="test-no-ag",
            auto_guard_eligible=False,
            owner_approved=False,
        )
        result = guard.check(agent, "write:src")
        assert result.decision == PermissionDecision.BLOCKED
        assert guard.is_blocked(result)


class TestRBACGuardBlocked:
    def test_always_blocked_operations(self):
        guard = RBACGuard()
        agent = AgentIdentity(session_id="test-blocked")
        result = guard.check(agent, "delete:audit_logs")
        assert result.decision == PermissionDecision.BLOCKED
        assert guard.is_blocked(result)

    def test_protected_path_write_blocked(self):
        guard = RBACGuard()
        agent = AgentIdentity(session_id="test-protected")
        result = guard.check(agent, "write:src", target_path=".git/config")
        assert result.decision == PermissionDecision.BLOCKED

    def test_unknown_operation_blocked_for_unapproved(self):
        guard = RBACGuard()
        agent = AgentIdentity(
            session_id="test-unknown",
            owner_approved=False,
        )
        result = guard.check(agent, "some:unknown:operation")
        assert result.decision == PermissionDecision.BLOCKED

    def test_blocked_by_l0_immutable_core(self):
        guard = RBACGuard()
        agent = AgentIdentity(session_id="test-l0")
        result = guard.check(agent, "modify_immutable_core")
        assert result.decision == PermissionDecision.BLOCKED
        assert "L0" in result.reason


class TestIntegration:
    def test_full_pipeline_allow(self):
        guard = RBACGuard()
        agent = AgentIdentity(
            session_id="test-integration",
            maturity=MaturityLevel.L2_REGULAR,
            role=AgentRole.EXECUTOR,
            owner_approved=True,
        )
        result = guard.check(agent, "execute:tests")
        assert result.decision == PermissionDecision.ALLOW

    def test_full_pipeline_blocked(self):
        guard = RBACGuard()
        agent = AgentIdentity(session_id="test-block")
        result = guard.check(agent, "delete:audit_logs")
        assert guard.is_blocked(result)

    def test_permission_result_properties(self):
        result = PermissionResult(
            decision=PermissionDecision.AUTO_GUARD,
            reason="test",
            auto_guard_timeout=600,
        )
        guard = RBACGuard()
        assert guard.is_auto_guard(result)
        assert not guard.is_blocked(result)
