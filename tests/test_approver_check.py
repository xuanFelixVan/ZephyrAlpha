# [A_test] module_id: SRC-TST-0326 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §test
# [MODULE] tests.test_approver_check
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.access_control.approver_check
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_approver_check.py
from zephyr.security.access_control.approver_check import verify_approver, SUPERADMIN_AGENTS, RESTRICTED_ACTIONS


class TestConstants:
    def test_superadmin_agents(self):
        assert "bytebuddy" in SUPERADMIN_AGENTS
        assert "superadmin" in SUPERADMIN_AGENTS

    def test_restricted_actions(self):
        assert "destroy" in RESTRICTED_ACTIONS
        assert "purge" in RESTRICTED_ACTIONS


class TestVerifyApprover:
    def test_superadmin_approved(self):
        result = verify_approver("bytebuddy", "deploy")
        assert result["approved"] is True
        assert result["reason"] == "superadmin"

    def test_admin_approved(self):
        result = verify_approver("admin", "deploy")
        assert result["approved"] is True

    def test_restricted_action_non_superadmin(self):
        result = verify_approver("worker", "destroy")
        assert result["approved"] is False
        assert "restricted" in result["reason"]

    def test_owner_normal_action(self):
        result = verify_approver("owner", "deploy")
        assert result["approved"] is True

    def test_unknown_approver_restricted(self):
        result = verify_approver("stranger", "destroy")
        assert result["approved"] is False
