# [A_test] module_id: SRC-TST-1043 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3.3

# [MODULE] tests.test_gate_override

# [INVARIANTS] OverrideRecord.is_expired reflects UTC now vs expires_at; GateOverride._active keys are gate_id strings; audit-trail is append-only

# [MODIFY-GUARD] changes require source gate_override.py review

# [CONSUMERS] pytest

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] grant returns OverrideRecord; is_overridden returns bool; cleanup_expired returns int; revoke returns None

# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_override import GateOverride, OverrideRecord


class TestOverrideRecord:
    def test_instantiation_defaults(self):
        r = OverrideRecord(
            gate_id="G0",
            session_id="sess-1",
            reason="emergency",
            granted_by="admin",
            expires_at=datetime.now(UTC) + timedelta(minutes=30),
        )
        assert r.gate_id == "G0"
        assert r.session_id == "sess-1"
        assert r.reason == "emergency"
        assert r.granted_by == "admin"
        assert isinstance(r.created_at, datetime)
        assert r.created_at.tzinfo is not None

    def test_is_expired_false(self):
        r = OverrideRecord(
            gate_id="G1",
            session_id="sess-2",
            reason="test",
            granted_by="owner",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert r.is_expired is False

    def test_is_expired_true(self):
        r = OverrideRecord(
            gate_id="G2",
            session_id="sess-3",
            reason="test",
            granted_by="owner",
            expires_at=datetime.now(UTC) - timedelta(seconds=1),
        )
        assert r.is_expired is True

    def test_is_expired_exactly_now(self):
        now = datetime.now(UTC)
        r = OverrideRecord(
            gate_id="G3",
            session_id="sess-4",
            reason="boundary",
            granted_by="owner",
            expires_at=now,
        )
        assert r.is_expired is True

    def test_custom_created_at(self):
        custom = datetime(2025, 1, 1, tzinfo=UTC)
        r = OverrideRecord(
            gate_id="G4",
            session_id="sess-5",
            reason="custom",
            granted_by="owner",
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
            created_at=custom,
        )
        assert r.created_at == custom

    def test_empty_strings(self):
        r = OverrideRecord(
            gate_id="",
            session_id="",
            reason="",
            granted_by="",
            expires_at=datetime.now(UTC) + timedelta(minutes=1),
        )
        assert r.gate_id == ""
        assert r.session_id == ""
        assert r.reason == ""
        assert r.granted_by == ""


class TestGateOverride:
    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_instantiation(self, mock_write):
        go = GateOverride()
        assert go.audit_trail == []

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_grant_returns_record(self, mock_write):
        go = GateOverride()
        record = go.grant("G0", "sess-1", "emergency bypass")
        assert isinstance(record, OverrideRecord)
        assert record.gate_id == "G0"
        assert record.session_id == "sess-1"
        assert record.reason == "emergency bypass"
        assert record.granted_by == "unknown"
        assert record.is_expired is False

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_grant_custom_granted_by(self, mock_write):
        go = GateOverride()
        record = go.grant("G1", "sess-2", "planned", granted_by="admin-alice")
        assert record.granted_by == "admin-alice"

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_grant_custom_ttl(self, mock_write):
        go = GateOverride()
        record = go.grant("G2", "sess-3", "short ttl", ttl_minutes=5)
        assert record.is_expired is False
        delta = record.expires_at - datetime.now(UTC)
        assert delta.total_seconds() > 240
        assert delta.total_seconds() < 360

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_grant_calls_write_to_core(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "emergency")
        mock_write.assert_called_once()
        call_args = mock_write.call_args
        assert call_args[0][0] == "gate_override"
        payload = call_args[0][1]
        assert payload["gate_id"] == "G0"
        assert payload["session_id"] == "sess-1"
        assert payload["reason"] == "emergency"

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_is_overridden_true(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "bypass")
        assert go.is_overridden("G0", "sess-1") is True

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_is_overridden_false_different_session(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "bypass")
        assert go.is_overridden("G0", "sess-99") is False

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_is_overridden_false_different_gate(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "bypass")
        assert go.is_overridden("G1", "sess-1") is False

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_is_overridden_false_no_grants(self, mock_write):
        go = GateOverride()
        assert go.is_overridden("G0", "sess-1") is False

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_is_overridden_cleans_expired(self, mock_write):
        go = GateOverride()
        record = go.grant("G0", "sess-1", "bypass", ttl_minutes=-1)
        assert record.is_expired is True
        assert go.is_overridden("G0", "sess-1") is False

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_revoke(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "bypass")
        go.revoke("G0", "sess-1")
        assert go.is_overridden("G0", "sess-1") is False

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_revoke_preserves_other_session(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "bypass")
        go.grant("G0", "sess-2", "other bypass")
        go.revoke("G0", "sess-1")
        assert go.is_overridden("G0", "sess-1") is False
        assert go.is_overridden("G0", "sess-2") is True

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_revoke_nonexistent_gate(self, mock_write):
        go = GateOverride()
        go.revoke("G99", "sess-1")

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_revoke_nonexistent_session(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "bypass")
        go.revoke("G0", "sess-99")
        assert go.is_overridden("G0", "sess-1") is True

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_cleanup_expired_removes_expired(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "expired", ttl_minutes=-1)
        go.grant("G0", "sess-2", "active", ttl_minutes=30)
        removed = go.cleanup_expired()
        assert removed == 1
        assert go.is_overridden("G0", "sess-2") is True

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_cleanup_expired_none_expired(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "active", ttl_minutes=30)
        removed = go.cleanup_expired()
        assert removed == 0

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_cleanup_expired_all_expired(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "expired1", ttl_minutes=-1)
        go.grant("G0", "sess-2", "expired2", ttl_minutes=-1)
        removed = go.cleanup_expired()
        assert removed == 2

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_cleanup_expired_empty(self, mock_write):
        go = GateOverride()
        removed = go.cleanup_expired()
        assert removed == 0

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_audit_trail_records_all_grants(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "reason1")
        go.grant("G1", "sess-2", "reason2")
        trail = go.audit_trail
        assert len(trail) == 2
        assert trail[0].gate_id == "G0"
        assert trail[1].gate_id == "G1"

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_audit_trail_preserves_revoked(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "bypass")
        go.revoke("G0", "sess-1")
        trail = go.audit_trail
        assert len(trail) == 1

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_audit_trail_is_copy(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "bypass")
        trail = go.audit_trail
        trail.clear()
        assert len(go.audit_trail) == 1

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_multiple_grants_same_gate_session(self, mock_write):
        go = GateOverride()
        go.grant("G0", "sess-1", "first")
        go.grant("G0", "sess-1", "second")
        assert go.is_overridden("G0", "sess-1") is True
        trail = go.audit_trail
        assert len(trail) == 2

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_grant_zero_ttl(self, mock_write):
        go = GateOverride()
        record = go.grant("G0", "sess-1", "zero ttl", ttl_minutes=0)
        assert record.is_expired is True

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_grant_negative_ttl(self, mock_write):
        go = GateOverride()
        record = go.grant("G0", "sess-1", "negative ttl", ttl_minutes=-10)
        assert record.is_expired is True

    @patch("zephyr.gov_enforcement.rule_enforcement.gate_override.write_to_core")
    def test_default_ttl_is_30(self, mock_write):
        assert GateOverride.DEFAULT_TTL_MINUTES == 30
