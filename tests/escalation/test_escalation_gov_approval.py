# [A_test] module_id: SRC-TST-0851 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_escalation_gov_approval
# [INVARIANTS] none
# [MODIFY-GUARD] governance/approval.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_escalation_gov_approval.py -q
# [TTL] task_bound

from __future__ import annotations

import pytest
from pydantic import ValidationError

from zephyr.gov_enforcement.rule_enforcement.approval import ApprovalRequest


class TestApprovalRequestInstantiation:
    def test_minimal_fields(self):
        req = ApprovalRequest(
            task_id="T-001",
            requested_action="delete_file",
            human_approver="admin",
            reason="emergency cleanup",
        )
        assert req.task_id == "T-001"
        assert req.requested_action == "delete_file"
        assert req.human_approver == "admin"
        assert req.reason == "emergency cleanup"

    def test_default_priority(self):
        req = ApprovalRequest(
            task_id="T-002",
            requested_action="read",
            human_approver="user",
            reason="check",
        )
        assert req.priority == "P2"

    def test_default_status(self):
        req = ApprovalRequest(
            task_id="T-003",
            requested_action="read",
            human_approver="user",
            reason="check",
        )
        assert req.status == "PENDING"

    def test_default_created_at(self):
        req = ApprovalRequest(
            task_id="T-004",
            requested_action="read",
            human_approver="user",
            reason="check",
        )
        assert req.created_at != ""
        assert "T" in req.created_at

    def test_custom_priority_and_status(self):
        req = ApprovalRequest(
            task_id="T-005",
            requested_action="write",
            human_approver="owner",
            reason="critical fix",
            priority="P0",
            status="APPROVED",
        )
        assert req.priority == "P0"
        assert req.status == "APPROVED"

    def test_custom_created_at(self):
        req = ApprovalRequest(
            task_id="T-006",
            requested_action="read",
            human_approver="user",
            reason="check",
            created_at="2026-01-01T00:00:00+00:00",
        )
        assert req.created_at == "2026-01-01T00:00:00+00:00"


class TestApprovalRequestValidation:
    def test_missing_required_field_task_id(self):
        with pytest.raises(ValidationError):
            ApprovalRequest(
                requested_action="read",
                human_approver="user",
                reason="check",
            )

    def test_missing_required_field_requested_action(self):
        with pytest.raises(ValidationError):
            ApprovalRequest(
                task_id="T-007",
                human_approver="user",
                reason="check",
            )

    def test_missing_required_field_human_approver(self):
        with pytest.raises(ValidationError):
            ApprovalRequest(
                task_id="T-008",
                requested_action="read",
                reason="check",
            )

    def test_missing_required_field_reason(self):
        with pytest.raises(ValidationError):
            ApprovalRequest(
                task_id="T-009",
                requested_action="read",
                human_approver="user",
            )

    def test_empty_strings_allowed(self):
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


class TestApprovalRequestModel:
    def test_model_dump(self):
        req = ApprovalRequest(
            task_id="T-010",
            requested_action="execute",
            human_approver="admin",
            reason="deploy",
        )
        data = req.model_dump()
        assert "task_id" in data
        assert "requested_action" in data
        assert "human_approver" in data
        assert "reason" in data
        assert "created_at" in data
        assert "priority" in data
        assert "status" in data

    def test_model_dump_json(self):
        req = ApprovalRequest(
            task_id="T-011",
            requested_action="execute",
            human_approver="admin",
            reason="deploy",
        )
        json_str = req.model_dump_json()
        assert "T-011" in json_str
        assert "execute" in json_str

    def test_immutability_by_default(self):
        req = ApprovalRequest(
            task_id="T-012",
            requested_action="read",
            human_approver="user",
            reason="check",
        )
        req.status = "APPROVED"
        assert req.status == "APPROVED"

    def test_two_instances_independent(self):
        req1 = ApprovalRequest(
            task_id="T-013",
            requested_action="read",
            human_approver="user",
            reason="check1",
        )
        req2 = ApprovalRequest(
            task_id="T-014",
            requested_action="write",
            human_approver="admin",
            reason="check2",
        )
        assert req1.task_id != req2.task_id
        assert req1.requested_action != req2.requested_action
