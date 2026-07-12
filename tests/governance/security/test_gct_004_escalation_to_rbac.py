# [A_test] module_id: SRC-TST-0127 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-284 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_004_escalation_to_rbac
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""G-CT-004 — Escalation → RBAC 集成测试."""

from __future__ import annotations


class TestGCT004EscalationToRBAC:
    """验证 escalation/approval.py 的 ApprovalRequest 可被 agent-rbac/approver_check.py 验证."""

    def test_approval_request_creatable(self):
        from zephyr.gov_enforcement.rule_enforcement.approval import ApprovalRequest

        req = ApprovalRequest(task_id="T001", requested_action="deploy", human_approver="admin", reason="emergency")
        assert req.task_id == "T001"

    def test_approver_check_accepts_request(self):
        from zephyr.gov_enforcement.rule_enforcement.approval import ApprovalRequest
        from zephyr.security.access_control.approver_check import verify_approver

        req = ApprovalRequest(task_id="T002", requested_action="read:docs", human_approver="bytebuddy", reason="test")
        result = verify_approver(req.human_approver, req.requested_action)
        assert isinstance(result, dict)
        assert "approved" in result

    def test_superadmin_always_approved(self):
        from zephyr.security.access_control.approver_check import verify_approver

        result = verify_approver("bytebuddy", "deploy")
        assert result["approved"] is True

    def test_restricted_action_requires_superadmin(self):
        from zephyr.security.access_control.approver_check import verify_approver

        result = verify_approver("regular_user", "destroy")
        assert result["approved"] is False
