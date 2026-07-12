# [A_test] module_id: SRC-TST-0325 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_approval
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_approval.py -q
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_enforcement.rule_enforcement.approval import ApprovalRequest
from zephyr.shared.contracts.approval_types import ApprovalRequest as DirectApprovalRequest


class TestApprovalRequestInstantiation:
    def test_creates_instance_with_required_fields(self):
        req = ApprovalRequest(
            task_id="T-001",
            requested_action="delete_file",
            human_approver="admin",
            reason="cleanup",
        )
        assert req is not None

    def test_is_correct_type(self):
        req = ApprovalRequest(
            task_id="T-001",
            requested_action="delete_file",
            human_approver="admin",
            reason="cleanup",
        )
        assert isinstance(req, ApprovalRequest)

    def test_reexport_matches_direct_import(self):
        assert ApprovalRequest is DirectApprovalRequest


class TestApprovalRequestFields:
    def test_required_fields_stored(self):
        req = ApprovalRequest(
            task_id="T-002",
            requested_action="modify_config",
            human_approver="owner",
            reason="security update",
        )
        assert req.task_id == "T-002"
        assert req.requested_action == "modify_config"
        assert req.human_approver == "owner"
        assert req.reason == "security update"

    def test_default_priority_is_p2(self):
        req = ApprovalRequest(
            task_id="T-003",
            requested_action="read",
            human_approver="user",
            reason="audit",
        )
        assert req.priority == "P2"

    def test_default_status_is_pending(self):
        req = ApprovalRequest(
            task_id="T-004",
            requested_action="read",
            human_approver="user",
            reason="audit",
        )
        assert req.status == "PENDING"

    def test_created_at_auto_populated(self):
        req = ApprovalRequest(
            task_id="T-005",
            requested_action="read",
            human_approver="user",
            reason="audit",
        )
        assert req.created_at != ""
        assert "T" in req.created_at

    def test_custom_priority(self):
        req = ApprovalRequest(
            task_id="T-006",
            requested_action="emergency_stop",
            human_approver="admin",
            reason="critical",
            priority="P0",
        )
        assert req.priority == "P0"

    def test_custom_status(self):
        req = ApprovalRequest(
            task_id="T-007",
            requested_action="read",
            human_approver="admin",
            reason="check",
            status="APPROVED",
        )
        assert req.status == "APPROVED"


class TestApprovalRequestMissingFields:
    def test_missing_task_id_raises(self):
        with pytest.raises(Exception):
            ApprovalRequest(
                requested_action="delete",
                human_approver="admin",
                reason="test",
            )

    def test_missing_requested_action_raises(self):
        with pytest.raises(Exception):
            ApprovalRequest(
                task_id="T-008",
                human_approver="admin",
                reason="test",
            )

    def test_missing_human_approver_raises(self):
        with pytest.raises(Exception):
            ApprovalRequest(
                task_id="T-009",
                requested_action="delete",
                reason="test",
            )

    def test_missing_reason_raises(self):
        with pytest.raises(Exception):
            ApprovalRequest(
                task_id="T-010",
                requested_action="delete",
                human_approver="admin",
            )


class TestBoundaryConditions:
    def test_empty_string_fields_accepted(self):
        req = ApprovalRequest(
            task_id="",
            requested_action="",
            human_approver="",
            reason="",
        )
        assert req.task_id == ""
        assert req.requested_action == ""
        assert req.human_approver == ""
        assert req.reason == ""

    def test_long_strings_accepted(self):
        long_str = "x" * 10000
        req = ApprovalRequest(
            task_id=long_str,
            requested_action=long_str,
            human_approver=long_str,
            reason=long_str,
        )
        assert len(req.task_id) == 10000

    def test_unicode_fields(self):
        req = ApprovalRequest(
            task_id="任务-001",
            requested_action="删除文件",
            human_approver="管理员",
            reason="安全审查",
        )
        assert req.task_id == "任务-001"
        assert req.requested_action == "删除文件"
