# [A_test] module_id: SRC-TST-0806 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_gov_approval
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

from zephyr.gov_enforcement.rule_enforcement.approval import ApprovalRequest


class TestApprovalRequest:
    def test_instantiation_with_required_fields(self):
        ar = ApprovalRequest(
            task_id="T-001",
            requested_action="deploy",
            human_approver="owner-1",
            reason="critical fix",
        )
        assert ar.task_id == "T-001"
        assert ar.requested_action == "deploy"
        assert ar.human_approver == "owner-1"
        assert ar.reason == "critical fix"
        assert ar.priority == "P2"
        assert ar.status == "PENDING"
        assert ar.created_at is not None

    def test_default_priority_and_status(self):
        ar = ApprovalRequest(
            task_id="T-002",
            requested_action="rollback",
            human_approver="owner-2",
            reason="regression",
        )
        assert ar.priority == "P2"
        assert ar.status == "PENDING"

    def test_custom_priority(self):
        ar = ApprovalRequest(
            task_id="T-003",
            requested_action="emergency_stop",
            human_approver="owner-3",
            reason="security",
            priority="P0",
        )
        assert ar.priority == "P0"

    def test_custom_status(self):
        ar = ApprovalRequest(
            task_id="T-004",
            requested_action="approve",
            human_approver="owner-4",
            reason="review",
            status="APPROVED",
        )
        assert ar.status == "APPROVED"

    def test_created_at_is_iso8601(self):
        ar = ApprovalRequest(
            task_id="T-005",
            requested_action="test",
            human_approver="owner-5",
            reason="testing",
        )
        assert "T" in ar.created_at
