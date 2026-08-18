# [A_test] module_id: MOD-GOV_rbac_guard_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.rbac_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

from zephyr.security.access_control.guards.rbac_guard import (
    ALWAYS_ALLOW_OPERATIONS,
    ALWAYS_BLOCKED_OPERATIONS,
    PermissionDecision,
    PermissionResult,
    RBACGuard,
)
from zephyr.shared.contracts.identity.agent_identity import (
    AgentIdentity,
    AgentRole,
    IDESource,
    MaturityLevel,
)


def _make_agent(
    role=AgentRole.WRITER,
    maturity=MaturityLevel.L2_REGULAR,
    owner_approved=False,
    auto_guard_eligible=False,
    permissions=None,
    session_id="test-session-001",
):
    return AgentIdentity(
        session_id=session_id,
        role=role,
        maturity=maturity,
        owner_approved=owner_approved,
        auto_guard_eligible=auto_guard_eligible,
        ide_source=IDESource.TRAE,
        permissions=permissions or [],
    )


class TestPermissionDecision:
    def test_enum_values(self):
        assert PermissionDecision.ALLOW.value == "ALLOW"
        assert PermissionDecision.AUTO_GUARD.value == "AUTO_GUARD"
        assert PermissionDecision.BLOCKED.value == "BLOCKED"

    def test_enum_members_count(self):
        assert len(PermissionDecision) == 3


class TestPermissionResult:
    def test_default_values(self):
        r = PermissionResult(decision=PermissionDecision.ALLOW)
        assert r.reason == ""
        assert r.requires_owner_review is False
        assert r.auto_guard_timeout == 300
        assert r.audit_context == {}

    def test_custom_values(self):
        r = PermissionResult(
            decision=PermissionDecision.BLOCKED,
            reason="test reason",
            requires_owner_review=True,
            auto_guard_timeout=600,
            audit_context={"key": "value"},
        )
        assert r.decision == PermissionDecision.BLOCKED
        assert r.reason == "test reason"
        assert r.requires_owner_review is True
        assert r.auto_guard_timeout == 600
        assert r.audit_context == {"key": "value"}


class TestRBACGuardAlwaysAllow:
    def test_read_docs_allowed(self):
        guard = RBACGuard()
        agent = _make_agent()
        result = guard.check(agent, "read:docs")
        assert result.decision == PermissionDecision.ALLOW

    def test_code_search_allowed(self):
        guard = RBACGuard()
        agent = _make_agent()
        result = guard.check(agent, "code_search")
        assert result.decision == PermissionDecision.ALLOW

    def test_all_always_allow_operations(self):
        guard = RBACGuard()
        agent = _make_agent()
        for op in ALWAYS_ALLOW_OPERATIONS:
            result = guard.check(agent, op)
            assert result.decision == PermissionDecision.ALLOW, f"{op} should be ALLOW"


class TestRBACGuardAlwaysBlocked:
    def test_delete_audit_logs_blocked(self):
        guard = RBACGuard()
        agent = _make_agent(owner_approved=True)
        result = guard.check(agent, "delete:audit_logs")
        assert result.decision == PermissionDecision.BLOCKED

    def test_modify_immutable_core_blocked(self):
        guard = RBACGuard()
        agent = _make_agent(owner_approved=True)
        result = guard.check(agent, "modify:immutable_core")
        assert result.decision == PermissionDecision.BLOCKED

    def test_all_always_blocked_operations(self):
        guard = RBACGuard()
        agent = _make_agent(owner_approved=True)
        for op in ALWAYS_BLOCKED_OPERATIONS:
            result = guard.check(agent, op)
            assert result.decision == PermissionDecision.BLOCKED, f"{op} should be BLOCKED"

    def test_blocked_overrides_owner_approval(self):
        guard = RBACGuard()
        agent = _make_agent(owner_approved=True, role=AgentRole.ADMIN)
        result = guard.check(agent, "shell:true_execution")
        assert result.decision == PermissionDecision.BLOCKED


class TestRBACGuardAutoGuard:
    def test_write_src_auto_guard_eligible(self):
        guard = RBACGuard()
        agent = _make_agent(auto_guard_eligible=True)
        result = guard.check(agent, "write:src")
        assert result.decision == PermissionDecision.AUTO_GUARD

    def test_write_src_not_eligible_blocked(self):
        guard = RBACGuard()
        agent = _make_agent(auto_guard_eligible=False)
        result = guard.check(agent, "write:src")
        assert result.decision == PermissionDecision.BLOCKED

    def test_auto_guard_with_owner_approved_becomes_allow(self):
        guard = RBACGuard()
        agent = _make_agent(owner_approved=True)
        result = guard.check(agent, "write:src")
        assert result.decision == PermissionDecision.ALLOW

    def test_auto_guard_timeout_from_agent(self):
        guard = RBACGuard()
        agent = _make_agent(auto_guard_eligible=True, maturity=MaturityLevel.L3_SENIOR)
        result = guard.check(agent, "write:src")
        assert result.decision == PermissionDecision.AUTO_GUARD
        assert result.auto_guard_timeout == 1800


class TestRBACGuardRolePermissions:
    def test_reader_role_read_allowed(self):
        guard = RBACGuard()
        agent = _make_agent(role=AgentRole.READER)
        result = guard.check(agent, "read:docs")
        assert result.decision == PermissionDecision.ALLOW

    def test_admin_role_manage_rbac(self):
        guard = RBACGuard()
        agent = _make_agent(role=AgentRole.ADMIN, owner_approved=True)
        result = guard.check(agent, "manage:rbac")
        assert result.decision == PermissionDecision.ALLOW

    def test_unknown_operation_blocked_for_unapproved(self):
        guard = RBACGuard()
        agent = _make_agent(role=AgentRole.READER, owner_approved=False, auto_guard_eligible=False)
        result = guard.check(agent, "some:unknown_op")
        assert result.decision == PermissionDecision.BLOCKED


class TestRBACGuardHelperMethods:
    def test_is_blocked(self):
        guard = RBACGuard()
        r = PermissionResult(decision=PermissionDecision.BLOCKED)
        assert guard.is_blocked(r) is True

    def test_is_not_blocked(self):
        guard = RBACGuard()
        r = PermissionResult(decision=PermissionDecision.ALLOW)
        assert guard.is_blocked(r) is False

    def test_is_auto_guard(self):
        guard = RBACGuard()
        r = PermissionResult(decision=PermissionDecision.AUTO_GUARD)
        assert guard.is_auto_guard(r) is True

    def test_is_not_auto_guard(self):
        guard = RBACGuard()
        r = PermissionResult(decision=PermissionDecision.ALLOW)
        assert guard.is_auto_guard(r) is False


class TestRBACGuardProtectedPath:
    def test_protected_path_blocked_for_writer(self):
        guard = RBACGuard()
        agent = _make_agent(role=AgentRole.WRITER)
        result = guard.check(agent, "read:src", target_path="src/zephyr/agent-rbac/rbac_guard.py")
        assert result.decision == PermissionDecision.BLOCKED

    def test_protected_path_allowed_for_admin(self):
        guard = RBACGuard()
        agent = _make_agent(role=AgentRole.ADMIN)
        result = guard.check(agent, "read:src", target_path="src/zephyr/agent-rbac/rbac_guard.py")
        assert result.decision == PermissionDecision.ALLOW

    def test_protected_path_allowed_for_auditor(self):
        guard = RBACGuard()
        agent = _make_agent(role=AgentRole.AUDITOR)
        result = guard.check(agent, "read:src", target_path="src/zephyr/agent-rbac/rbac_guard.py")
        assert result.decision == PermissionDecision.ALLOW


class TestRBACGuardExplicitPermission:
    def test_explicit_permission_grants_access(self):
        guard = RBACGuard()
        agent = _make_agent(permissions=["custom:operation"])
        result = guard.check(agent, "custom:operation")
        assert result.decision == PermissionDecision.ALLOW

    def test_wildcard_permission(self):
        guard = RBACGuard()
        agent = _make_agent(permissions=["custom:*"])
        result = guard.check(agent, "custom:something")
        assert result.decision == PermissionDecision.ALLOW


class TestRBACGuardBoundary:
    def test_empty_operation_string(self):
        guard = RBACGuard()
        agent = _make_agent(owner_approved=False, auto_guard_eligible=False)
        result = guard.check(agent, "")
        assert result.decision == PermissionDecision.BLOCKED

    def test_owner_approved_allows_unknown(self):
        guard = RBACGuard()
        agent = _make_agent(owner_approved=True)
        result = guard.check(agent, "unknown:operation")
        assert result.decision == PermissionDecision.ALLOW
