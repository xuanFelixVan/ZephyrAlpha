# [A_test] module_id: MOD-GOV_e_gov_rbac_bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_gov_rbac_bridge
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.agent_spec.rbac_bridge import (
    EscalationRBACBridge,
    RBACCheckResult,
)


class TestRBACCheckResult:
    def test_default_values(self):
        result = RBACCheckResult()
        assert result.passed is True
        assert result.decision == "ALLOW"
        assert result.layer == ""
        assert result.rule_id == ""
        assert result.reason == ""
        assert result.audit_context == {}

    def test_blocked(self):
        result = RBACCheckResult(
            passed=False,
            decision="BLOCKED",
            reason="permission denied",
        )
        assert result.passed is False
        assert result.decision == "BLOCKED"


class TestEscalationRBACBridge:
    def test_request_escalation(self):
        bridge = EscalationRBACBridge()
        result = bridge.request_escalation("agent-1", "write_prod", "emergency")
        assert result["agent_id"] == "agent-1"
        assert result["target_permission"] == "write_prod"
        assert result["status"] == "PENDING_OWNER_APPROVAL"

    def test_pre_execute_check_without_rbac(self):
        bridge = EscalationRBACBridge()
        result = bridge.pre_execute_check("session-1", "read", "/tmp")
        assert result.passed is True

    def test_pre_execute_check_pass_through(self):
        bridge = EscalationRBACBridge()
        result = bridge.pre_execute_check("session-1", "dispatch_task")
        assert isinstance(result, RBACCheckResult)
