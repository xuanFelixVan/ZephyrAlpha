# [A_test] module_id: SRC-TST-0625 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.contracts
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.contracts import RBACAuditBridge

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as e:
    _IMPORT_OK = False
    _IMPORT_REASON = str(e)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestRBACAuditBridgeCheckPermission:
    def test_allowed_permission_read(self):
        result = RBACAuditBridge._check_permission("agent-1", "read", "file.txt")
        assert result is True

    def test_allowed_permission_write(self):
        result = RBACAuditBridge._check_permission("agent-1", "write", "file.txt")
        assert result is True

    def test_allowed_permission_execute(self):
        result = RBACAuditBridge._check_permission("agent-1", "execute", "script.sh")
        assert result is True

    def test_denied_permission_unknown(self):
        result = RBACAuditBridge._check_permission("agent-1", "delete", "file.txt")
        assert result is False

    def test_denied_permission_empty(self):
        result = RBACAuditBridge._check_permission("agent-1", "", "file.txt")
        assert result is False

    def test_permission_check_ignores_agent_id(self):
        r1 = RBACAuditBridge._check_permission("agent-a", "read", "f")
        r2 = RBACAuditBridge._check_permission("agent-b", "read", "f")
        assert r1 == r2


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestRBACAuditBridgeCheckAndLog:
    def test_check_and_log_granted(self):
        bridge = RBACAuditBridge()
        result = bridge.check_and_log(agent_id="agent-1", permission="read", resource="file.txt")
        assert result["granted"] is True
        assert result["audit_record"] is not None

    def test_check_and_log_denied(self):
        bridge = RBACAuditBridge()
        result = bridge.check_and_log(agent_id="agent-1", permission="destroy", resource="file.txt")
        assert result["granted"] is False

    def test_check_and_log_with_session_id(self):
        bridge = RBACAuditBridge()
        result = bridge.check_and_log(
            agent_id="agent-1",
            permission="write",
            resource="file.txt",
            session_id="sess-001",
        )
        assert result["granted"] is True

    def test_check_and_log_empty_agent_id(self):
        bridge = RBACAuditBridge()
        result = bridge.check_and_log(agent_id="", permission="read", resource="file.txt")
        assert result["granted"] is True
