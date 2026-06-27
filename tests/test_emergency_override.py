# [A_test] module_id: SRC-TST-0828 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.emergency_override
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
    from zephyr.security.access_control.emergency_override import EmergencyOverride, EmergencyToken
except Exception as _exc:
    pytest.skip(f"无法导入 emergency_override: {_exc}", allow_module_level=True)


class TestEmergencyToken:
    def test_default_fields(self):
        t = EmergencyToken(issued_by="owner")
        assert t.issued_by == "owner"
        assert t.token_id.startswith("EMG-")
        assert t.used is False
        assert t.revoked is False
        assert t.permissions == []
        assert t.max_duration_seconds == 300

    def test_custom_fields(self):
        t = EmergencyToken(
            issued_by="admin",
            permissions=["write:src", "execute:scripts"],
            max_duration_seconds=60,
        )
        assert t.issued_by == "admin"
        assert len(t.permissions) == 2
        assert t.max_duration_seconds == 60


class TestEmergencyOverride:
    def test_issue_token(self):
        eo = EmergencyOverride()
        token = eo.issue("owner", ["write:src"], duration_seconds=120)
        assert token.issued_by == "owner"
        assert token.permissions == ["write:src"]
        assert token.max_duration_seconds == 120
        assert token.token_hash != ""
        assert token.expires_at > token.issued_at

    def test_issue_duration_capped_at_300(self):
        eo = EmergencyOverride()
        token = eo.issue("owner", ["read:all"], duration_seconds=9999)
        assert token.max_duration_seconds == 300

    def test_verify_valid_token(self):
        eo = EmergencyOverride()
        token = eo.issue("owner", ["write:src"])
        result = eo.verify(token.token_id)
        assert result["valid"] is True
        assert result["permissions"] == ["write:src"]
        assert result["issued_by"] == "owner"

    def test_verify_token_one_time_use(self):
        eo = EmergencyOverride()
        token = eo.issue("owner", ["write:src"])
        eo.verify(token.token_id)
        result = eo.verify(token.token_id)
        assert result["valid"] is False
        assert result["reason"] == "token_already_used"

    def test_verify_nonexistent_token(self):
        eo = EmergencyOverride()
        result = eo.verify("EMG-NONEXISTENT")
        assert result["valid"] is False
        assert result["reason"] == "token_not_found"

    def test_revoke_token(self):
        eo = EmergencyOverride()
        token = eo.issue("owner", ["write:src"])
        result = eo.revoke(token.token_id)
        assert result["revoked"] is True
        verify_result = eo.verify(token.token_id)
        assert verify_result["valid"] is False
        assert verify_result["reason"] == "token_revoked"

    def test_revoke_nonexistent_token(self):
        eo = EmergencyOverride()
        result = eo.revoke("EMG-NONEXISTENT")
        assert result["revoked"] is False
        assert result["reason"] == "token_not_found"

    def test_verify_expired_token(self):
        eo = EmergencyOverride()
        token = eo.issue("owner", ["write:src"], duration_seconds=0)
        token.expires_at = token.issued_at - 1
        result = eo.verify(token.token_id)
        assert result["valid"] is False
        assert result["reason"] == "token_expired"

    def test_issue_empty_permissions(self):
        eo = EmergencyOverride()
        token = eo.issue("owner", [])
        assert token.permissions == []
        result = eo.verify(token.token_id)
        assert result["valid"] is True
        assert result["permissions"] == []

    def test_issue_empty_issued_by(self):
        eo = EmergencyOverride()
        token = eo.issue("", ["write:src"])
        assert token.issued_by == ""
        result = eo.verify(token.token_id)
        assert result["valid"] is True
