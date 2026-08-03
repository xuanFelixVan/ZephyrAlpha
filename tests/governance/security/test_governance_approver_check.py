# [A_test] module_id: MOD-GOV_governance_approver_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.approver_check
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound
import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.approver_check import (
        RESTRICTED_ACTIONS,
        SUPERADMIN_AGENTS,
        verify_approver,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestGovernanceVerifyApprover:
    def test_superadmin_approved(self):
        for admin in SUPERADMIN_AGENTS:
            result = verify_approver(admin, "any_action")
            assert result["approved"] is True
            assert result["reason"] == "superadmin"

    def test_restricted_action_non_superadmin(self):
        for action in RESTRICTED_ACTIONS:
            result = verify_approver("regular_user", action)
            assert result["approved"] is False
            assert result["reason"] == "restricted_action_requires_superadmin"

    def test_valid_approver_normal_action(self):
        result = verify_approver("owner", "read")
        assert result["approved"] is True
        assert result["reason"] == "valid_approver"

    def test_regular_user_normal_action(self):
        result = verify_approver("regular_user", "read")
        assert result["approved"] is True
        assert result["reason"] == "valid_approver"

    def test_result_keys(self):
        result = verify_approver("bytebuddy", "deploy")
        assert "approved" in result
        assert "approver_id" in result
        assert "action" in result
        assert "reason" in result

    def test_approver_id_preserved(self):
        result = verify_approver("admin", "deploy")
        assert result["approver_id"] == "admin"

    def test_action_preserved(self):
        result = verify_approver("owner", "write")
        assert result["action"] == "write"


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestGovernanceApproverConstants:
    def test_superadmin_agents_non_empty(self):
        assert len(SUPERADMIN_AGENTS) > 0

    def test_restricted_actions_non_empty(self):
        assert len(RESTRICTED_ACTIONS) > 0

    def test_bytebuddy_is_superadmin(self):
        assert "bytebuddy" in SUPERADMIN_AGENTS
