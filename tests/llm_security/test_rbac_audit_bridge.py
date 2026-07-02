# [A_test] module_id: SRC-TST-1427 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §test
# [MODULE] tests.test_rbac_audit_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.access_control.contracts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_rbac_audit_bridge.py
# [TTL] task_bound
from unittest.mock import MagicMock, patch

from zephyr.security.access_control.contracts import RBACAuditBridge


class TestRBACAuditBridge:
    def test_instantiation(self):
        with patch("zephyr.security.access_control.contracts.AuditWriter"):
            b = RBACAuditBridge()
            assert b._audit is not None

    def test_check_and_log_granted(self):
        with patch("zephyr.security.access_control.contracts.AuditWriter") as MockAW:
            mock_writer = MagicMock()
            mock_writer.write.return_value = {"id": 1}
            MockAW.return_value = mock_writer
            b = RBACAuditBridge()
            result = b.check_and_log("agent1", "read", "resource1")
            assert result["granted"] is True
            assert "audit_record" in result

    def test_check_and_log_denied(self):
        with patch("zephyr.security.access_control.contracts.AuditWriter") as MockAW:
            mock_writer = MagicMock()
            mock_writer.write.return_value = {"id": 2}
            MockAW.return_value = mock_writer
            b = RBACAuditBridge()
            result = b.check_and_log("agent1", "destroy", "resource1")
            assert result["granted"] is False

    def test_check_permission_static(self):
        assert RBACAuditBridge._check_permission("a", "read", "r") is True
        assert RBACAuditBridge._check_permission("a", "write", "r") is True
        assert RBACAuditBridge._check_permission("a", "execute", "r") is True
        assert RBACAuditBridge._check_permission("a", "destroy", "r") is False
