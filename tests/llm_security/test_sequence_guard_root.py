# [A_test] module_id: SRC-TST-1578 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.sequence_guard
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

import time

from zephyr.security.access_control.guards.sequence_guard import (
    FORBIDDEN_SEQUENCES,
    SEQUENCE_TIMEOUT,
    SequenceEvent,
    SequenceGuard,
)


def _make_event(session_id="sess-001", operation="read:docs", target="file.py", timestamp=None):
    return SequenceEvent(
        session_id=session_id,
        operation=operation,
        target=target,
        timestamp=timestamp or time.time(),
    )


class TestSequenceEvent:
    def test_signature_format(self):
        evt = SequenceEvent(session_id="s1", operation="read:config", target="app.yaml")
        assert evt.signature() == "read:config:app.yaml"

    def test_default_timestamp(self):
        evt = SequenceEvent(session_id="s1", operation="read:docs", target="a.md")
        assert evt.timestamp > 0

    def test_custom_timestamp(self):
        ts = 1000000.0
        evt = SequenceEvent(session_id="s1", operation="read:docs", target="a.md", timestamp=ts)
        assert evt.timestamp == ts


class TestForbiddenSequences:
    def test_forbidden_sequences_defined(self):
        assert len(FORBIDDEN_SEQUENCES) > 0

    def test_each_forbidden_has_required_fields(self):
        for seq in FORBIDDEN_SEQUENCES:
            assert "name" in seq
            assert "pattern" in seq
            assert "description" in seq
            assert len(seq["pattern"]) >= 2

    def test_data_exfiltration_pattern(self):
        names = [s["name"] for s in FORBIDDEN_SEQUENCES]
        assert "data_exfiltration" in names

    def test_privilege_escalation_pattern(self):
        names = [s["name"] for s in FORBIDDEN_SEQUENCES]
        assert "privilege_escalation" in names


class TestSequenceGuardRecord:
    def test_record_returns_none_for_safe_sequence(self):
        guard = SequenceGuard()
        evt = _make_event(operation="read:docs", target="readme.md")
        result = guard.record(evt)
        assert result is None

    def test_record_detects_data_exfiltration(self):
        guard = SequenceGuard()
        now = time.time()
        guard.record(_make_event(operation="read:credential", target="creds", timestamp=now))
        guard.record(_make_event(operation="write:network", target="remote", timestamp=now + 1))
        result = guard.record(_make_event(operation="delete:log", target="audit", timestamp=now + 2))
        assert result is not None
        assert "data_exfiltration" in result

    def test_record_detects_privilege_escalation(self):
        guard = SequenceGuard()
        now = time.time()
        guard.record(_make_event(operation="read:rbac_config", target="rbac", timestamp=now))
        guard.record(_make_event(operation="modify:self_permission", target="perm", timestamp=now + 1))
        result = guard.record(_make_event(operation="execute:admin", target="cmd", timestamp=now + 2))
        assert result is not None
        assert "privilege_escalation" in result

    def test_record_detects_audit_wipe(self):
        guard = SequenceGuard()
        now = time.time()
        guard.record(_make_event(operation="read:audit_log", target="log", timestamp=now))
        guard.record(_make_event(operation="modify:audit_log", target="log", timestamp=now + 1))
        result = guard.record(_make_event(operation="delete:audit_log", target="log", timestamp=now + 2))
        assert result is not None
        assert "audit_wipe" in result


class TestSequenceGuardCrossSession:
    def test_no_collaboration(self):
        guard = SequenceGuard()
        events = [
            _make_event(session_id="s1", operation="read:docs", target="a.md"),
            _make_event(session_id="s2", operation="read:docs", target="b.md"),
        ]
        result = guard.check_cross_session(events)
        assert result is None

    def test_collaboration_detected(self):
        guard = SequenceGuard()
        events = [
            _make_event(session_id="s1", operation="write:data", target="shared"),
            _make_event(session_id="s2", operation="read:data", target="shared"),
            _make_event(session_id="s1", operation="write:more", target="shared2"),
            _make_event(session_id="s2", operation="read:more", target="shared2"),
        ]
        result = guard.check_cross_session(events)
        assert result is not None
        assert "Inter-agent" in result

    def test_empty_events(self):
        guard = SequenceGuard()
        result = guard.check_cross_session([])
        assert result is None

    def test_single_session_events(self):
        guard = SequenceGuard()
        events = [
            _make_event(session_id="s1", operation="read:docs", target="a.md"),
            _make_event(session_id="s1", operation="write:src", target="b.py"),
        ]
        result = guard.check_cross_session(events)
        assert result is None


class TestSequenceGuardWhitelist:
    def test_whitelist_allows_forbidden_pattern(self):
        guard = SequenceGuard()
        guard.add_whitelist(["read:credential:creds", "write:network:remote", "delete:log:audit"])
        now = time.time()
        guard.record(_make_event(operation="read:credential", target="creds", timestamp=now))
        guard.record(_make_event(operation="write:network", target="remote", timestamp=now + 1))
        result = guard.record(_make_event(operation="delete:log", target="audit", timestamp=now + 2))
        assert result is not None

    def test_is_whitelisted_true(self):
        guard = SequenceGuard()
        guard.add_whitelist(["read:docs:file.py"])
        session = [_make_event(operation="read:docs", target="file.py")]
        assert guard.is_whitelisted(session) is True

    def test_is_whitelisted_false(self):
        guard = SequenceGuard()
        session = [_make_event(operation="read:docs", target="file.py")]
        assert guard.is_whitelisted(session) is False


class TestSequenceGuardReset:
    def test_reset_session(self):
        guard = SequenceGuard()
        guard.record(_make_event(session_id="s1", operation="read:docs", target="a.md"))
        guard.reset_session("s1")
        guard.record(_make_event(session_id="s1", operation="read:docs", target="b.md"))
        result = guard.record(_make_event(session_id="s1", operation="read:docs", target="c.md"))
        assert result is None

    def test_reset_all(self):
        guard = SequenceGuard()
        guard.record(_make_event(session_id="s1", operation="read:docs", target="a.md"))
        guard.add_whitelist(["read:docs:a.md"])
        guard.reset_all()
        session = [_make_event(operation="read:docs", target="a.md")]
        assert guard.is_whitelisted(session) is False


class TestSequenceGuardTimeout:
    def test_expired_events_cleaned(self):
        guard = SequenceGuard()
        old_ts = time.time() - SEQUENCE_TIMEOUT - 10
        guard.record(_make_event(operation="read:credential", target="creds", timestamp=old_ts))
        guard.record(_make_event(operation="write:network", target="remote", timestamp=old_ts + 1))
        result = guard.record(_make_event(operation="delete:log", target="audit", timestamp=time.time()))
        assert result is None


class TestSequenceGuardBoundary:
    def test_empty_session_id(self):
        evt = _make_event(session_id="", operation="read:docs", target="a.md")
        guard = SequenceGuard()
        result = guard.record(evt)
        assert result is None

    def test_empty_operation(self):
        evt = _make_event(operation="", target="a.md")
        guard = SequenceGuard()
        result = guard.record(evt)
        assert result is None

    def test_empty_target(self):
        evt = _make_event(operation="read:docs", target="")
        guard = SequenceGuard()
        result = guard.record(evt)
        assert result is None
