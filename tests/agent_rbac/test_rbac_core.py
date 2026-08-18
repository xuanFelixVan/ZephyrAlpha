# [A_test] module_id: MOD-GOV_rbac_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-447 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.agent_rbac.test_rbac_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: agent-rbac core — identity + permission_guard + rbac_guard + immutable_core + kill_switch"""

import pytest

from zephyr.security.access_control.decision_explainer import DecisionExplainer, Explanation
from zephyr.security.access_control.exceptions import (
    AgentRbacError,
    ColdStartLockedError,
    PermissionDeniedError,
)
from zephyr.security.access_control.guards.abac_guard import ABACContext, ABACGuard, SensitivityLabel, TemporalCategory
from zephyr.security.access_control.guards.input_guard import InputDecision, InputGuard
from zephyr.security.access_control.guards.output_guard import OutputDecision, OutputGuard
from zephyr.security.access_control.guards.rbac_guard import (
    PermissionDecision,
    PermissionResult,
    RBACGuard,
)
from zephyr.security.access_control.guards.sequence_guard import SequenceEvent, SequenceGuard
from zephyr.security.access_control.immutable_core import (
    ImmutableCore,
    IntegrityResult,
)
from zephyr.security.access_control.kill_switch import (
    KillSwitch,
    KillSwitchState,
    TriggerEvent,
    TriggerResult,
)
from zephyr.shared.contracts.identity.agent_identity import (
    MATURITY_AUTO_GUARD_TIMEOUT,
    MATURITY_TLB_LIMITS,
    ROLE_DEFAULT_PERMISSIONS,
    AgentIdentity,
    AgentRole,
    IDESource,
    MaturityLevel,
)
from zephyr.shared.contracts.identity.permission import GuardDecision, GuardResult


@pytest.fixture
def reader_agent():
    return AgentIdentity(
        session_id="session-reader-001",
        maturity=MaturityLevel.L2_REGULAR,
        role=AgentRole.READER,
        ide_source=IDESource.TRAE,
        model="test-model",
        permissions=["read:docs", "read:src", "read:tests"],
    )


@pytest.fixture
def writer_agent():
    return AgentIdentity(
        session_id="session-writer-001",
        maturity=MaturityLevel.L2_REGULAR,
        role=AgentRole.WRITER,
        ide_source=IDESource.TRAE,
        model="test-model",
        auto_guard_eligible=True,
        permissions=["read:docs", "read:src", "write:src", "write:tests"],
    )


@pytest.fixture
def admin_agent():
    return AgentIdentity(
        session_id="session-admin-001",
        maturity=MaturityLevel.L4_PRINCIPAL,
        role=AgentRole.ADMIN,
        ide_source=IDESource.TRAE,
        model="test-model",
        owner_approved=True,
        permissions=["manage:rbac", "manage:kill_switch"],
    )


@pytest.fixture
def intern_agent():
    return AgentIdentity(
        session_id="session-intern-001",
        maturity=MaturityLevel.L0_INTERN,
        role=AgentRole.READER,
        ide_source=IDESource.CLI,
        model="test-model",
    )


@pytest.fixture
def immutable_core():
    return ImmutableCore()


@pytest.fixture
def rbac_guard(immutable_core):
    return RBACGuard(immutable_core=immutable_core)


@pytest.fixture
def kill_switch():
    ks = KillSwitch()
    ks.reset()
    return ks


class TestAgentIdentity:
    def test_creation_defaults(self):
        agent = AgentIdentity(session_id="test-001")
        assert agent.session_id == "test-001"
        assert agent.maturity == MaturityLevel.L0_INTERN
        assert agent.role == AgentRole.WRITER
        assert agent.ide_source == IDESource.UNKNOWN
        assert agent.model == "unknown"
        assert agent.permissions == []
        assert agent.auto_guard_eligible is False
        assert agent.owner_approved is False

    def test_creation_with_all_fields(self, admin_agent):
        assert admin_agent.session_id == "session-admin-001"
        assert admin_agent.maturity == MaturityLevel.L4_PRINCIPAL
        assert admin_agent.role == AgentRole.ADMIN
        assert admin_agent.ide_source == IDESource.TRAE
        assert admin_agent.owner_approved is True

    def test_sign_and_verify_token(self, reader_agent):
        secret = "test-secret-key"
        token = reader_agent.sign_token(secret)
        assert token != ""
        assert reader_agent.verify_token(secret) is True

    def test_verify_token_wrong_secret(self, reader_agent):
        reader_agent.sign_token("correct-secret")
        assert reader_agent.verify_token("wrong-secret") is False

    def test_verify_token_no_token(self):
        agent = AgentIdentity(session_id="no-token")
        assert agent.verify_token("any-secret") is False

    def test_has_permission_exact(self, writer_agent):
        assert writer_agent.has_permission("write:src") is True
        assert writer_agent.has_permission("write:tests") is True

    def test_has_permission_wildcard(self):
        agent = AgentIdentity(
            session_id="wildcard-agent",
            permissions=["read:*"],
        )
        assert agent.has_permission("read:docs") is True
        assert agent.has_permission("read:src") is True
        assert agent.has_permission("write:src") is False

    def test_has_permission_missing(self, reader_agent):
        assert reader_agent.has_permission("write:src") is False
        assert reader_agent.has_permission("manage:rbac") is False

    def test_get_tlb_limit(self, intern_agent, admin_agent):
        assert intern_agent.get_tlb_limit() == 100
        assert admin_agent.get_tlb_limit() == 50000

    def test_get_auto_guard_timeout(self, intern_agent, admin_agent):
        assert intern_agent.get_auto_guard_timeout() == 300
        assert admin_agent.get_auto_guard_timeout() == 7200

    def test_can_promote_to(self, intern_agent):
        assert intern_agent.can_promote_to(MaturityLevel.L1_JUNIOR) is True
        assert intern_agent.can_promote_to(MaturityLevel.L2_REGULAR) is False

    def test_maturity_level_enum(self):
        levels = list(MaturityLevel)
        assert len(levels) == 5
        assert levels[0] == MaturityLevel.L0_INTERN
        assert levels[4] == MaturityLevel.L4_PRINCIPAL

    def test_agent_role_enum(self):
        roles = list(AgentRole)
        # P1-3: Batch 1 合并后 7 成员（security 5 + shared REVIEWER + AUTONOMOUS_AGENT）
        # 回归测试固化历史行为（P1-1 例外②）
        assert len(roles) == 7
        assert AgentRole.READER in roles
        assert AgentRole.ADMIN in roles

    def test_role_default_permissions(self):
        assert "read:docs" in ROLE_DEFAULT_PERMISSIONS[AgentRole.READER]
        assert "write:src" in ROLE_DEFAULT_PERMISSIONS[AgentRole.WRITER]
        assert "manage:rbac" in ROLE_DEFAULT_PERMISSIONS[AgentRole.ADMIN]
        assert "audit:full" in ROLE_DEFAULT_PERMISSIONS[AgentRole.AUDITOR]

    def test_maturity_tlb_limits(self):
        assert MATURITY_TLB_LIMITS[MaturityLevel.L0_INTERN] == 100
        assert MATURITY_TLB_LIMITS[MaturityLevel.L4_PRINCIPAL] == 50000

    def test_maturity_auto_guard_timeout(self):
        assert MATURITY_AUTO_GUARD_TIMEOUT[MaturityLevel.L0_INTERN] == 300
        assert MATURITY_AUTO_GUARD_TIMEOUT[MaturityLevel.L4_PRINCIPAL] == 7200


class TestImmutableCore:
    def test_protected_paths_not_empty(self, immutable_core):
        assert len(immutable_core.protected_paths) > 0

    def test_always_blocked_not_empty(self, immutable_core):
        assert len(immutable_core.always_blocked) > 0

    def test_is_protected_path_git(self, immutable_core):
        assert immutable_core.is_protected_path(".git/config") is True

    def test_is_protected_path_agent_rbac(self, immutable_core):
        assert immutable_core.is_protected_path("src/zephyr/agent-rbac/immutable_core.py") is True

    def test_is_protected_path_safe(self, immutable_core):
        assert immutable_core.is_protected_path("src/zephyr/my_module/helper.py") is False

    def test_is_protected_path_env(self, immutable_core):
        assert immutable_core.is_protected_path(".env") is True
        assert immutable_core.is_protected_path(".env.production") is True

    def test_is_always_blocked(self, immutable_core):
        assert immutable_core.is_always_blocked("modify_immutable_core") is True
        assert immutable_core.is_always_blocked("delete_audit_logs") is True
        assert immutable_core.is_always_blocked("disable_kill_switch") is True

    def test_is_not_blocked(self, immutable_core):
        assert immutable_core.is_always_blocked("read:docs") is False
        assert immutable_core.is_always_blocked("write:src") is False

    def test_verify_integrity(self, immutable_core):
        result = immutable_core.verify_immutable_core_integrity()
        assert isinstance(result, IntegrityResult)
        assert result.intact is True

    def test_verify_static_constants_integrity(self, immutable_core):
        result = immutable_core.verify_static_constants_integrity()
        assert isinstance(result, IntegrityResult)
        assert result.intact is True

    def test_should_cold_start_lock_no_config(self, immutable_core, tmp_path):
        core = ImmutableCore(project_root=tmp_path)
        assert core.should_cold_start_lock() is True

    def test_should_cold_start_lock_with_config(self, immutable_core, tmp_path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "rbac_roles.yaml").write_text("roles: []", encoding="utf-8")
        core = ImmutableCore(project_root=tmp_path)
        assert core.should_cold_start_lock() is False


class TestRBACGuard:
    def test_always_allow_operations(self, rbac_guard, reader_agent):
        for op in ["read:docs", "read:src", "read:tests", "file_search", "code_search"]:
            result = rbac_guard.check(reader_agent, op)
            assert result.decision == PermissionDecision.ALLOW, f"Expected ALLOW for {op}"

    def test_always_blocked_operations(self, rbac_guard, admin_agent):
        for op in ["delete:audit_logs", "modify:immutable_core", "disable:kill_switch"]:
            result = rbac_guard.check(admin_agent, op)
            assert result.decision == PermissionDecision.BLOCKED, f"Expected BLOCKED for {op}"

    def test_auto_guard_operations(self, rbac_guard, writer_agent):
        result = rbac_guard.check(writer_agent, "write:src")
        assert result.decision == PermissionDecision.AUTO_GUARD
        assert result.auto_guard_timeout > 0

    def test_auto_guard_not_eligible(self, rbac_guard, reader_agent):
        result = rbac_guard.check(reader_agent, "write:src")
        assert result.decision == PermissionDecision.BLOCKED

    def test_owner_approved_auto_guard(self, rbac_guard, admin_agent):
        result = rbac_guard.check(admin_agent, "write:src")
        assert result.decision == PermissionDecision.ALLOW

    def test_protected_path_blocks_non_admin(self, rbac_guard, reader_agent):
        result = rbac_guard.check(reader_agent, "read:docs", target_path="src/zephyr/agent-rbac/core.py")
        assert result.decision == PermissionDecision.BLOCKED

    def test_protected_path_allows_admin(self, rbac_guard, admin_agent):
        result = rbac_guard.check(admin_agent, "read:docs", target_path="src/zephyr/agent-rbac/core.py")
        assert result.decision == PermissionDecision.ALLOW

    def test_is_blocked(self, rbac_guard):
        blocked = PermissionResult(decision=PermissionDecision.BLOCKED, reason="test")
        assert rbac_guard.is_blocked(blocked) is True
        allowed = PermissionResult(decision=PermissionDecision.ALLOW, reason="test")
        assert rbac_guard.is_blocked(allowed) is False

    def test_is_auto_guard(self, rbac_guard):
        ag = PermissionResult(decision=PermissionDecision.AUTO_GUARD, reason="test")
        assert rbac_guard.is_auto_guard(ag) is True
        allowed = PermissionResult(decision=PermissionDecision.ALLOW, reason="test")
        assert rbac_guard.is_auto_guard(allowed) is False

    def test_unknown_operation_blocked_without_approval(self, rbac_guard, reader_agent):
        result = rbac_guard.check(reader_agent, "custom:operation")
        assert result.decision == PermissionDecision.BLOCKED


class TestKillSwitch:
    def test_initial_state(self, kill_switch):
        assert kill_switch.status.state == KillSwitchState.NORMAL
        assert kill_switch.is_global_tripped() is False

    def test_is_agent_blocked_normal(self, kill_switch):
        assert kill_switch.is_agent_blocked("agent-001") is False

    def test_manual_trip_global(self, kill_switch):
        kill_switch.manual_trip_global("test")
        assert kill_switch.is_global_tripped() is True
        assert kill_switch.is_agent_blocked("agent-001") is True

    def test_manual_trip_agent(self, kill_switch):
        kill_switch.manual_trip_agent("agent-001")
        assert kill_switch.is_agent_blocked("agent-001") is True
        assert kill_switch.is_agent_blocked("agent-002") is False

    def test_owner_release_global(self, kill_switch):
        kill_switch.manual_trip_global("test")
        kill_switch.owner_release_global()
        assert kill_switch.is_global_tripped() is False
        assert kill_switch.status.owner_override is True

    def test_owner_release_agent(self, kill_switch):
        kill_switch.manual_trip_agent("agent-001")
        kill_switch.owner_release_agent("agent-001")
        assert kill_switch.is_agent_blocked("agent-001") is False

    def test_record_event_warning(self, kill_switch):
        event = TriggerEvent(trigger="rapid_file_deletion", agent_id="agent-001")
        result = kill_switch.record_event(event)
        assert result == TriggerResult.WARNING

    def test_record_event_blocks_agent(self, kill_switch):
        for i in range(3):
            event = TriggerEvent(trigger="rapid_file_deletion", agent_id="agent-001")
            kill_switch.record_event(event)
        assert kill_switch.is_agent_blocked("agent-001") is True

    def test_reset(self, kill_switch):
        kill_switch.manual_trip_global("test")
        kill_switch.reset()
        assert kill_switch.status.state == KillSwitchState.NORMAL
        assert kill_switch.is_global_tripped() is False

    def test_trigger_count(self, kill_switch):
        assert kill_switch.trigger_count == len(kill_switch.triggers)

    def test_owner_revoke_override(self, kill_switch):
        kill_switch.manual_trip_global("test")
        kill_switch.owner_release_global()
        assert kill_switch.status.owner_override is True
        kill_switch.owner_revoke_override()
        assert kill_switch.status.owner_override is False


@pytest.mark.xfail(reason="ARCH-036: stub pending implementation", strict=False)
class TestInputGuard:
    def test_allow_safe_params(self):
        guard = InputGuard()
        result = guard.check_params("write:src", {"content": "hello world"})
        assert result == InputDecision.ALLOW

    def test_block_dangerous_pattern(self):
        guard = InputGuard()
        result = guard.check_params("execute:scripts", {"command": "rm -rf /"})
        assert result == InputDecision.BLOCKED

    def test_block_path_traversal(self):
        guard = InputGuard()
        result, reason = guard.check_path("../../etc/passwd")
        assert result == InputDecision.BLOCKED

    def test_block_absolute_path(self):
        guard = InputGuard()
        result, reason = guard.check_path("/etc/passwd")
        assert result == InputDecision.BLOCKED

    def test_allow_safe_path(self):
        guard = InputGuard()
        result, reason = guard.check_path("src/zephyr/module.py")
        assert result == InputDecision.ALLOW

    def test_block_untrusted_package(self):
        guard = InputGuard()
        result, reason = guard.check_package_install("malicious-package")
        assert result == InputDecision.BLOCKED

    def test_allow_trusted_package(self):
        guard = InputGuard()
        result, reason = guard.check_package_install("pytest")
        assert result == InputDecision.ALLOW

    def test_block_untrusted_network(self):
        guard = InputGuard()
        result, reason = guard.check_network_target("http://evil.example.com")
        assert result == InputDecision.BLOCKED

    def test_allow_localhost(self):
        guard = InputGuard()
        result, reason = guard.check_network_target("http://localhost:8080")
        assert result == InputDecision.ALLOW


@pytest.mark.xfail(reason="ARCH-036: stub pending implementation", strict=False)
class TestSequenceGuard:
    def test_record_no_forbidden(self):
        guard = SequenceGuard()
        event = SequenceEvent(session_id="s1", operation="read:docs", target="file.py")
        result = guard.record(event)
        assert result is None

    def test_record_forbidden_sequence(self):
        guard = SequenceGuard()
        pattern = [("read", "credential"), ("write", "network"), ("delete", "log")]
        result = None
        for op, tgt in pattern:
            event = SequenceEvent(session_id="s1", operation=op, target=tgt)
            result = guard.record(event)
        assert result is not None

    def test_reset_session(self):
        guard = SequenceGuard()
        event = SequenceEvent(session_id="s1", operation="read:docs", target="file.py")
        guard.record(event)
        guard.reset_session("s1")
        assert "s1" not in guard.sequences

    def test_whitelist(self):
        guard = SequenceGuard()
        guard.add_whitelist(["read:docs"])
        event = SequenceEvent(session_id="s1", operation="read:docs", target="file.py")
        guard.record(event)
        assert guard.is_whitelisted(guard.sequences["s1"]) is True


@pytest.mark.xfail(reason="ARCH-036: stub pending implementation", strict=False)
class TestOutputGuard:
    def test_clean_output(self):
        guard = OutputGuard()
        result = guard.check("Hello, world!", agent_id="agent-1")
        assert result.decision == OutputDecision.CLEAN
        assert result.findings == []

    def test_pii_detection_phone(self):
        guard = OutputGuard()
        result = guard.check("Contact: 13812345678", agent_id="agent-1")
        assert result.decision == OutputDecision.SANITIZED
        assert any("PHONE_CN" in f for f in result.findings)

    def test_pii_detection_email(self):
        guard = OutputGuard()
        result = guard.check("Email: test@example.com", agent_id="agent-1")
        assert result.decision == OutputDecision.SANITIZED
        assert any("EMAIL" in f for f in result.findings)

    def test_credential_detection(self):
        guard = OutputGuard()
        result = guard.check("Key: sk-" + "A" * 32, agent_id="agent-1")
        assert result.decision == OutputDecision.SANITIZED
        assert any("Credential" in f for f in result.findings)

    def test_synthesis_leakage_detection(self):
        guard = OutputGuard()
        for i in range(5):
            guard.record_read("agent-synth", f"source-{i}")
        result = guard.check("Combined output", agent_id="agent-synth")
        assert any("Synthesis leakage" in f for f in result.findings)

    def test_reset_agent(self):
        guard = OutputGuard()
        guard.record_read("agent-reset", "source-1")
        guard.reset_agent("agent-reset")
        assert "agent-reset" not in guard.read_sources


@pytest.mark.xfail(reason="ARCH-036: stub pending implementation", strict=False)
class TestABACGuard:
    def test_allow_normal_context(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="abac-1", maturity=MaturityLevel.L2_REGULAR)
        ctx = ABACContext(intent="read", operation="read:docs")
        ok, msg = guard.check(agent, ctx)
        assert ok is True

    def test_block_off_hours_intern(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="abac-intern", maturity=MaturityLevel.L0_INTERN)
        ctx = ABACContext(intent="execute", temporal=TemporalCategory.OFF_HOURS, operation="execute:scripts")
        ok, msg = guard.check(agent, ctx)
        assert ok is False

    def test_block_weekend_intern(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="abac-intern2", maturity=MaturityLevel.L0_INTERN)
        ctx = ABACContext(intent="read", temporal=TemporalCategory.WEEKEND, operation="read:docs")
        ok, msg = guard.check(agent, ctx)
        assert ok is False

    def test_block_low_maturity_high_sensitivity(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="abac-low", maturity=MaturityLevel.L0_INTERN)
        ctx = ABACContext(sensitivity=SensitivityLabel.HIGH, operation="read:secrets")
        ok, msg = guard.check(agent, ctx)
        assert ok is False

    def test_allow_high_maturity_high_sensitivity(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="abac-high", maturity=MaturityLevel.L4_PRINCIPAL)
        ctx = ABACContext(sensitivity=SensitivityLabel.HIGH, operation="read:secrets")
        ok, msg = guard.check(agent, ctx)
        assert ok is True

    def test_tlb_limit(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="abac-tlb", maturity=MaturityLevel.L0_INTERN)
        ctx = ABACContext(operation="read:docs", sensitivity=SensitivityLabel.PUBLIC)
        for _ in range(100):
            ok, _ = guard.check(agent, ctx)
            assert ok is True
        ok, msg = guard.check(agent, ctx)
        assert ok is False
        assert "TLB" in msg

    def test_sensitivity_label_blitz(self):
        guard = ABACGuard()
        for i in range(5):
            guard.record_sensitivity_label_change(f"label-{i}")
        assert guard.is_sensitivity_label_blitz() is True

    def test_classify_temporal(self):
        result = ABACGuard.classify_temporal()
        assert isinstance(result, TemporalCategory)

    def test_detect_sensitivity_from_content(self):
        assert ABACGuard.detect_sensitivity_from_content("top secret info") == SensitivityLabel.RESTRICTED
        assert ABACGuard.detect_sensitivity_from_content("password=abc") == SensitivityLabel.HIGH
        assert ABACGuard.detect_sensitivity_from_content("hello world") == SensitivityLabel.PUBLIC

    def test_reset_all(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="abac-reset", maturity=MaturityLevel.L2_REGULAR)
        ctx = ABACContext(operation="read:docs")
        guard.check(agent, ctx)
        guard.reset_all()
        assert len(guard.tlb_records) == 0


@pytest.mark.xfail(reason="ARCH-036: stub pending implementation", strict=False)
class TestDecisionExplainer:
    def test_structured_rejection(self):
        explainer = DecisionExplainer()
        exp = explainer.structured_rejection(
            blocked_layer="L1",
            rule_id="RBAC-001",
            reason="Operation blocked",
        )
        assert isinstance(exp, Explanation)
        assert exp.blocked_layer == "L1"
        assert exp.rule_id == "RBAC-001"
        assert exp.correction_suggestion != ""

    def test_structured_rejection_to_dict(self):
        explainer = DecisionExplainer()
        exp = explainer.structured_rejection(
            blocked_layer="L0",
            rule_id="KSW-001",
            reason="Kill switch tripped",
        )
        d = exp.to_dict()
        assert d["blocked_layer"] == "L0"
        assert d["rule_id"] == "KSW-001"
        assert "causal_chain" in d

    def test_explain_auto_guard(self):
        explainer = DecisionExplainer()
        exp = explainer.explain_auto_guard("write:src", timeout=300)
        assert exp.rule_id == "AUTO_GUARD"
        assert "300" in exp.correction_suggestion


@pytest.mark.xfail(reason="ARCH-036: stub pending implementation", strict=False)
class TestExceptions:
    def test_agent_rbac_error(self):
        err = AgentRbacError(message="test error", layer="L1", rule_id="TEST-001")
        assert str(err) == "test error"
        assert err.layer == "L1"
        assert err.rule_id == "TEST-001"

    def test_permission_denied_error(self):
        err = PermissionDeniedError(message="denied", operation="write:src", layer="L1", rule_id="RBAC-001")
        assert err.operation == "write:src"

    def test_cold_start_locked_error(self):
        err = ColdStartLockedError()
        assert err.layer == "L1"
        assert err.rule_id == "CSL-001"


class TestGuardResult:
    def test_default_allow(self):
        result = GuardResult()
        assert result.decision == GuardDecision.ALLOW
        assert result.layer == ""
        assert result.timing_ns == 0

    def test_blocked_result(self):
        result = GuardResult(
            decision=GuardDecision.BLOCKED,
            layer="L1",
            reason="Blocked by RBAC",
            rule_id="RBAC-001",
        )
        assert result.decision == GuardDecision.BLOCKED
        assert result.layer == "L1"
        assert result.rule_id == "RBAC-001"

    def test_auto_guard_result(self):
        result = GuardResult(
            decision=GuardDecision.AUTO_GUARD,
            layer="L1",
            reason="Auto-guarded",
            rule_id="AG-001",
        )
        assert result.decision == GuardDecision.AUTO_GUARD
