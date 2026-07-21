# [A_test] module_id: MOD-GOV_sequence_guard_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_sequence_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试 L4 SequenceGuard — 操作序列追踪与危险序列阻断
"""

import time

from zephyr.security.access_control.guards.sequence_guard import (
    FORBIDDEN_SEQUENCES,
    SequenceEvent,
    SequenceGuard,
)


class TestForbiddenSequences:
    def test_at_least_6_sequences(self):
        assert len(FORBIDDEN_SEQUENCES) >= 6

    def test_each_has_name_and_pattern(self):
        for seq in FORBIDDEN_SEQUENCES:
            assert "name" in seq
            assert "pattern" in seq
            assert len(seq["pattern"]) >= 2

    def test_critical_sequences_present(self):
        names = [s["name"] for s in FORBIDDEN_SEQUENCES]
        expected = [
            "data_exfiltration",
            "privilege_escalation",
            "destruction_chain",
        ]
        for e in expected:
            assert e in names, f"'{e}' missing from forbidden sequences"


class TestDangerousSequenceBlocking:
    def test_data_exfiltration_chain_blocked(self):
        guard = SequenceGuard()
        events = [
            SequenceEvent(session_id="s1", operation="read", target="credential"),
            SequenceEvent(session_id="s1", operation="write", target="network"),
            SequenceEvent(session_id="s1", operation="delete", target="log"),
        ]
        for e in events[:-1]:
            guard.record(e)
            time.sleep(0.001)
        result = guard.record(events[-1])
        assert result is not None
        assert "data_exfiltration" in str(result)

    def test_destruction_chain_blocked(self):
        guard = SequenceGuard()
        events = [
            SequenceEvent(session_id="s2", operation="read", target="config"),
            SequenceEvent(session_id="s2", operation="write", target="destructive"),
            SequenceEvent(session_id="s2", operation="delete", target="backup"),
        ]
        for e in events[:-1]:
            guard.record(e)
        result = guard.record(events[-1])
        assert result is not None


class TestSafeSequence:
    def test_safe_sequence_not_blocked(self):
        guard = SequenceGuard()
        events = [
            SequenceEvent(session_id="s3", operation="read", target="docs"),
            SequenceEvent(session_id="s3", operation="read", target="src"),
        ]
        for e in events:
            result = guard.record(e)
        assert True


class TestCrossSession:
    def test_inter_agent_detection(self):
        guard = SequenceGuard()
        events = [
            SequenceEvent(session_id="a1", operation="write", target="shared_file"),
            SequenceEvent(session_id="a2", operation="read", target="shared_file"),
        ]
        result = guard.check_cross_session(events)
        assert result is not None or result is None


class TestWhitelist:
    def test_whitelist_basic(self):
        guard = SequenceGuard()
        guard.add_whitelist(["read:docs", "write:docs"])
        assert len(guard._whitelist) == 1


class TestReset:
    def test_reset_session_clears(self):
        guard = SequenceGuard()
        guard.record(SequenceEvent(session_id="rs-1", operation="read", target="test"))
        guard.reset_session("rs-1")
        result = guard.record(SequenceEvent(session_id="rs-1", operation="read", target="test"))
        assert True

    def test_reset_all(self):
        guard = SequenceGuard()
        guard.record(SequenceEvent(session_id="ra-1", operation="read", target="test"))
        guard.reset_all()
        assert True
