# [A_test] module_id: MOD-GOV_escalation_gov_rbac_bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_escalation_gov_rbac_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] governance/rbac_bridge.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_escalation_gov_rbac_bridge.py -q
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.governance.agent_spec.rbac_bridge import (
    EscalationRBACBridge,
    RBACCheckResult,
)


class TestRBACCheckResult:
    def test_default_values(self):
        r = RBACCheckResult()
        assert r.passed is True
        assert r.decision == "ALLOW"
        assert r.layer == ""
        assert r.rule_id == ""
        assert r.reason == ""
        assert r.audit_context == {}

    def test_custom_values(self):
        r = RBACCheckResult(
            passed=False,
            decision="BLOCKED",
            layer="escalation",
            rule_id="R-001",
            reason="blocked by rule",
            audit_context={"key": "val"},
        )
        assert r.passed is False
        assert r.decision == "BLOCKED"
        assert r.layer == "escalation"
        assert r.rule_id == "R-001"
        assert r.reason == "blocked by rule"
        assert r.audit_context == {"key": "val"}

    def test_audit_context_explicit(self):
        r = RBACCheckResult(audit_context={"x": 42})
        assert r.audit_context == {"x": 42}

    def test_audit_context_default_empty(self):
        r1 = RBACCheckResult()
        r2 = RBACCheckResult()
        assert r1.audit_context == {}
        assert r1.audit_context is not r2.audit_context


class TestEscalationRBACBridgeInit:
    def test_instantiation(self):
        bridge = EscalationRBACBridge()
        assert bridge is not None

    def test_guard_attribute(self):
        bridge = EscalationRBACBridge()
        assert hasattr(bridge, "_guard")


class TestRequestEscalation:
    def test_returns_pending_approval(self):
        bridge = EscalationRBACBridge()
        result = bridge.request_escalation("agent-1", "write:sensitive", "emergency fix")
        assert result["agent_id"] == "agent-1"
        assert result["target_permission"] == "write:sensitive"
        assert result["reason"] == "emergency fix"
        assert result["status"] == "PENDING_OWNER_APPROVAL"

    def test_empty_strings(self):
        bridge = EscalationRBACBridge()
        result = bridge.request_escalation("", "", "")
        assert result["agent_id"] == ""
        assert result["target_permission"] == ""
        assert result["reason"] == ""
        assert result["status"] == "PENDING_OWNER_APPROVAL"

    def test_long_reason(self):
        bridge = EscalationRBACBridge()
        long_reason = "x" * 10000
        result = bridge.request_escalation("a", "p", long_reason)
        assert result["reason"] == long_reason


class TestPreExecuteCheck:
    def test_pass_through_when_no_rbac(self):
        bridge = EscalationRBACBridge()
        result = bridge.pre_execute_check("sess-1", "read")
        assert isinstance(result, RBACCheckResult)
        assert result.passed is True

    @patch("zephyr.governance.agent_spec.rbac_bridge._AGENT_RBAC_AVAILABLE", False)
    def test_pass_through_without_rbac_available(self):
        bridge = EscalationRBACBridge()
        bridge.guard = None
        result = bridge.pre_execute_check("sess-1", "write", "/some/path")
        assert result.passed is True
        assert "pass-through" in result.reason

    @patch("zephyr.governance.agent_spec.rbac_bridge._AGENT_RBAC_AVAILABLE", True)
    def test_blocked_by_rbac(self):
        mock_result = MagicMock()
        mock_result.decision = MagicMock()
        mock_result.decision.name = "BLOCKED"
        mock_result.layer = "test-layer"
        mock_result.rule_id = "R-001"
        mock_result.reason = "not allowed"
        mock_result.audit_context = {"info": "test"}

        from zephyr.shared.contracts.identity.permission import GuardDecision

        mock_result.decision = GuardDecision.BLOCKED

        mock_guard = MagicMock()
        mock_guard.check.return_value = mock_result

        bridge = EscalationRBACBridge()
        bridge.guard = mock_guard

        result = bridge.pre_execute_check("sess-1", "delete", "/path")
        assert result.passed is False
        assert result.decision == "BLOCKED"

    @patch("zephyr.governance.agent_spec.rbac_bridge._AGENT_RBAC_AVAILABLE", True)
    def test_auto_guard_result(self):
        from zephyr.shared.contracts.identity.permission import GuardDecision

        mock_result = MagicMock()
        mock_result.decision = GuardDecision.AUTO_GUARD
        mock_result.layer = "auto-layer"
        mock_result.rule_id = "R-002"
        mock_result.reason = "auto-guarded"
        mock_result.audit_context = {}

        mock_guard = MagicMock()
        mock_guard.check.return_value = mock_result

        bridge = EscalationRBACBridge()
        bridge.guard = mock_guard

        result = bridge.pre_execute_check("sess-1", "modify", "/path")
        assert result.passed is True
        assert result.decision == "AUTO_GUARD"

    @patch("zephyr.governance.agent_spec.rbac_bridge._AGENT_RBAC_AVAILABLE", True)
    def test_allow_result(self):
        from zephyr.shared.contracts.identity.permission import GuardDecision

        mock_result = MagicMock()
        mock_result.decision = GuardDecision.ALLOW
        mock_result.layer = "allow-layer"
        mock_result.rule_id = ""
        mock_result.reason = "permitted"

        mock_guard = MagicMock()
        mock_guard.check.return_value = mock_result

        bridge = EscalationRBACBridge()
        bridge.guard = mock_guard

        result = bridge.pre_execute_check("sess-1", "read", "/path")
        assert result.passed is True
        assert result.decision == "ALLOW"

    @patch("zephyr.governance.agent_spec.rbac_bridge._AGENT_RBAC_AVAILABLE", True)
    def test_exception_in_rbac_passes_through(self):
        mock_guard = MagicMock()
        mock_guard.check.side_effect = RuntimeError("RBAC down")

        bridge = EscalationRBACBridge()
        bridge.guard = mock_guard

        result = bridge.pre_execute_check("sess-1", "read")
        assert result.passed is True
        assert "RBAC error" in result.reason

    def test_empty_session_and_operation(self):
        bridge = EscalationRBACBridge()
        result = bridge.pre_execute_check("", "")
        assert isinstance(result, RBACCheckResult)
