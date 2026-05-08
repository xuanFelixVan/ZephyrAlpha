"""G-CT-004 — Escalation → RBAC 集成测试."""
from __future__ import annotations

import pytest


class TestGCT004EscalationToRBAC:
    """验证 escalation/approval.py 的 ApprovalRequest 可被 agent_rbac/approver_check.py 验证."""

    def test_approval_request_creatable(self):
        from zephyr.governance.escalation.approval import ApprovalRequest
        req = ApprovalRequest(
            task_id="T001", requested_action="deploy",
            human_approver="admin", reason="emergency"
        )
        assert req.task_id == "T001"

    def test_approver_check_accepts_request(self):
        from zephyr.governance.escalation.approval import ApprovalRequest
        from zephyr.governance.agent_rbac.approver_check import verify_approver
        req = ApprovalRequest(
            task_id="T002", requested_action="read:docs",
            human_approver="bytebuddy", reason="test"
        )
        result = verify_approver(req.human_approver, req.requested_action)
        assert isinstance(result, dict)
        assert "approved" in result

    def test_superadmin_always_approved(self):
        from zephyr.governance.agent_rbac.approver_check import verify_approver
        result = verify_approver("bytebuddy", "deploy")
        assert result["approved"] is True

    def test_restricted_action_requires_superadmin(self):
        from zephyr.governance.agent_rbac.approver_check import verify_approver
        result = verify_approver("regular_user", "destroy")
        assert result["approved"] is False
