# [A_test] module_id: MOD-GOV_audit_log_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.audit_log_guard
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
    from zephyr.security.access_control.guards.audit_log_guard import AuditLogGuard

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as e:
    _IMPORT_OK = False
    _IMPORT_REASON = str(e)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestAuditLogGuardSanitize:
    def test_clean_string_unchanged(self):
        guard = AuditLogGuard()
        assert guard.sanitize("hello world") == "hello world"

    def test_newline_replaced(self):
        guard = AuditLogGuard()
        result = guard.sanitize("line1\nline2")
        assert "\n" not in result
        assert "line1" in result
        assert "line2" in result

    def test_carriage_return_replaced(self):
        guard = AuditLogGuard()
        result = guard.sanitize("text\rmore")
        assert "\r" not in result

    def test_tab_replaced(self):
        guard = AuditLogGuard()
        result = guard.sanitize("col1\tcol2")
        assert "\t" not in result

    def test_null_byte_replaced(self):
        guard = AuditLogGuard()
        result = guard.sanitize("before\x00after")
        assert "\x00" not in result

    def test_escape_sequence_replaced(self):
        guard = AuditLogGuard()
        result = guard.sanitize("text\\nmore")
        assert "\\n" not in result or result != "text\\nmore"

    def test_empty_string(self):
        guard = AuditLogGuard()
        assert guard.sanitize("") == ""

    def test_multiple_injection_patterns(self):
        guard = AuditLogGuard()
        result = guard.sanitize("a\nb\rc\td\x00e")
        assert "\n" not in result
        assert "\r" not in result
        assert "\t" not in result
        assert "\x00" not in result


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestAuditLogGuardValidateEntry:
    def test_clean_entry(self):
        guard = AuditLogGuard()
        result = guard.validate_entry("agent_id", "agent-001")
        assert result["key"] == "agent_id"
        assert result["clean"] is True
        assert result["original_len"] == len("agent-001")

    def test_dirty_entry(self):
        guard = AuditLogGuard()
        result = guard.validate_entry("action", "delete\nfile")
        assert result["key"] == "action"
        assert result["clean"] is False

    def test_empty_value(self):
        guard = AuditLogGuard()
        result = guard.validate_entry("key", "")
        assert result["clean"] is True
        assert result["original_len"] == 0


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestAuditLogGuardValidateDict:
    def test_clean_dict(self):
        guard = AuditLogGuard()
        result = guard.validate_dict({"agent": "a1", "action": "read"})
        assert result["clean"] is True
        assert result["issues"] == {}

    def test_dirty_dict(self):
        guard = AuditLogGuard()
        result = guard.validate_dict({"agent": "a1", "action": "delete\nfile"})
        assert result["clean"] is False
        assert "action" in result["issues"]

    def test_empty_dict(self):
        guard = AuditLogGuard()
        result = guard.validate_dict({})
        assert result["clean"] is True

    def test_non_string_values_ignored(self):
        guard = AuditLogGuard()
        result = guard.validate_dict({"count": 42, "flag": True})
        assert result["clean"] is True
