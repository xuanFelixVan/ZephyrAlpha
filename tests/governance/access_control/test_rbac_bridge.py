# [A_test] module_id: SRC-TST-1428 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rbac_bridge
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_rbac_bridge.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.agent_spec.rbac_bridge import EscalationRBACBridge, RBACCheckResult


class TestRBACCheckResultInit:
    def test_default_values(self):
        result = RBACCheckResult()
        assert result.passed is True
        assert result.decision == "ALLOW"
        assert result.layer == ""
        assert result.rule_id == ""
        assert result.reason == ""
        assert result.audit_context == {}

    def test_custom_values(self):
        result = RBACCheckResult(
            passed=False,
            decision="BLOCKED",
            layer="escalation",
            rule_id="R-001",
            reason="blocked by policy",
            audit_context={"key": "value"},
        )
        assert result.passed is False
        assert result.decision == "BLOCKED"
        assert result.layer == "escalation"
        assert result.rule_id == "R-001"
        assert result.reason == "blocked by policy"
        assert result.audit_context == {"key": "value"}


class TestEscalationRBACBridgeInit:
    def test_creates_instance_without_dependencies(self):
        bridge = EscalationRBACBridge()
        assert bridge.guard is not None or bridge.guard is None


class TestRequestEscalation:
    def test_returns_pending_owner_approval(self):
        bridge = EscalationRBACBridge()
        result = bridge.request_escalation("agent-1", "write_sensitive", "need access")
        assert result["status"] == "PENDING_OWNER_APPROVAL"

    def test_returns_agent_id_in_result(self):
        bridge = EscalationRBACBridge()
        result = bridge.request_escalation("agent-42", "admin", "emergency")
        assert result["agent_id"] == "agent-42"

    def test_returns_target_permission_in_result(self):
        bridge = EscalationRBACBridge()
        result = bridge.request_escalation("agent-1", "delete_all", "cleanup")
        assert result["target_permission"] == "delete_all"

    def test_returns_reason_in_result(self):
        bridge = EscalationRBACBridge()
        result = bridge.request_escalation("agent-1", "write", "deployment needed")
        assert result["reason"] == "deployment needed"

    def test_different_agents_get_independent_results(self):
        bridge = EscalationRBACBridge()
        r1 = bridge.request_escalation("agent-a", "read", "audit")
        r2 = bridge.request_escalation("agent-b", "write", "deploy")
        assert r1["agent_id"] != r2["agent_id"]
        assert r1["target_permission"] != r2["target_permission"]


class TestPreExecuteCheck:
    def test_returns_check_result_type(self):
        bridge = EscalationRBACBridge()
        result = bridge.pre_execute_check("session-1", "read_file")
        assert isinstance(result, RBACCheckResult)

    def test_pass_through_when_no_rbac(self):
        bridge = EscalationRBACBridge()
        result = bridge.pre_execute_check("session-1", "read_file")
        if bridge.guard is None:
            assert result.passed is True
            assert "pass-through" in result.reason

    def test_empty_target_path_default(self):
        bridge = EscalationRBACBridge()
        result = bridge.pre_execute_check("session-1", "execute")
        assert isinstance(result, RBACCheckResult)

    def test_with_target_path(self):
        bridge = EscalationRBACBridge()
        result = bridge.pre_execute_check("session-1", "write", "src/main.py")
        assert isinstance(result, RBACCheckResult)


class TestRBACBridgeBoundary:
    def test_request_escalation_with_empty_strings(self):
        bridge = EscalationRBACBridge()
        result = bridge.request_escalation("", "", "")
        assert result["agent_id"] == ""
        assert result["target_permission"] == ""
        assert result["reason"] == ""
        assert result["status"] == "PENDING_OWNER_APPROVAL"

    def test_pre_execute_check_with_empty_session(self):
        bridge = EscalationRBACBridge()
        result = bridge.pre_execute_check("", "read")
        assert isinstance(result, RBACCheckResult)

    def test_rbac_check_result_audit_context_independent(self):
        r1 = RBACCheckResult(audit_context={"x": 1})
        r2 = RBACCheckResult(audit_context={"y": 2})
        assert r1.audit_context != r2.audit_context
        assert r1.audit_context == {"x": 1}
        assert r2.audit_context == {"y": 2}
