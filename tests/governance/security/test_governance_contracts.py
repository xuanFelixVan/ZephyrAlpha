# [A_test] module_id: MOD-GOV_governance_contracts | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.contracts
# [DOMAIN] D_SECURITY
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import sys

sys.path.insert(0, "src")

from unittest.mock import MagicMock, patch

import pytest

try:
    from zephyr.security.access_control.contracts import RBACAuditBridge

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestRBACAuditBridgeCheckPermission:
    def test_allowed_permission(self):
        assert RBACAuditBridge.check_permission("agent-1", "read", "file") is True
        assert RBACAuditBridge.check_permission("agent-1", "write", "file") is True
        assert RBACAuditBridge.check_permission("agent-1", "execute", "file") is True

    def test_denied_permission(self):
        assert RBACAuditBridge.check_permission("agent-1", "destroy", "file") is False
        assert RBACAuditBridge.check_permission("agent-1", "admin_override", "file") is False

    def test_unknown_permission(self):
        assert RBACAuditBridge.check_permission("agent-1", "unknown_perm", "file") is False


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestRBACAuditBridgeCheckAndLog:
    @patch("zephyr.security.access_control.contracts.AuditWriter")
    def test_granted_permission(self, mock_audit_writer_cls):
        mock_instance = MagicMock()
        mock_instance.write.return_value = {"event_type": "rbac_decision", "chain_hash": "hash123"}
        mock_audit_writer_cls.return_value = mock_instance
        bridge = RBACAuditBridge()
        result = bridge.check_and_log("agent-1", "read", "resource-1")
        assert result["granted"] is True
        assert "audit_record" in result

    @patch("zephyr.security.access_control.contracts.AuditWriter")
    def test_denied_permission(self, mock_audit_writer_cls):
        mock_instance = MagicMock()
        mock_instance.write.return_value = {"event_type": "rbac_decision", "chain_hash": "hash456"}
        mock_audit_writer_cls.return_value = mock_instance
        bridge = RBACAuditBridge()
        result = bridge.check_and_log("agent-1", "destroy", "resource-1")
        assert result["granted"] is False
        assert "audit_record" in result

    @patch("zephyr.security.access_control.contracts.AuditWriter")
    def test_session_id_passed(self, mock_audit_writer_cls):
        mock_instance = MagicMock()
        mock_instance.write.return_value = {
            "event_type": "rbac_decision",
            "session_id": "sess-001",
            "chain_hash": "hash789",
        }
        mock_audit_writer_cls.return_value = mock_instance
        bridge = RBACAuditBridge()
        result = bridge.check_and_log("agent-1", "read", "res", session_id="sess-001")
        assert result["audit_record"]["session_id"] == "sess-001"

    @patch("zephyr.security.access_control.contracts.AuditWriter")
    def test_audit_record_has_chain_hash(self, mock_audit_writer_cls):
        mock_instance = MagicMock()
        mock_instance.write.return_value = {"event_type": "rbac_decision", "chain_hash": "chain_hash_value"}
        mock_audit_writer_cls.return_value = mock_instance
        bridge = RBACAuditBridge()
        result = bridge.check_and_log("agent-1", "read", "res")
        assert result["audit_record"]["chain_hash"] == "chain_hash_value"
