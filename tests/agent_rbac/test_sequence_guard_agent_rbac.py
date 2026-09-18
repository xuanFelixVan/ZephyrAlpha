# [A_test] module_id: MOD-GOV_sequence_guard_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_sequence_guard
# [DOMAIN] D_AUTONOMY_PERM
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
        # B2 审计修复：原 assert True 恒绿——安全序列必须显式断言不被误拦
        assert result is None, f"安全序列被误拦: {result}"


class TestCrossSession:
    def test_inter_agent_detection(self):
        guard = SequenceGuard()
        events = [
            SequenceEvent(session_id="a1", operation="write", target="shared_file"),
            SequenceEvent(session_id="a2", operation="read", target="shared_file"),
        ]
        result = guard.check_cross_session(events)
        # B2 审计修复：原 `assert result is not None or result is None` 恒真式——
        # M15 变异实证（check_cross_session 恒返 None）该测试仍绿。补上真断言：
        # 同一 target 被两个会话操作必须报跨会话共享风险。
        assert result is not None, "跨会话共享 target 未检出"
        assert "shared_file" in result


class TestWhitelist:
    def test_whitelist_basic(self):
        guard = SequenceGuard()
        guard.add_whitelist(["read:docs", "write:docs"])
        assert len(guard.whitelist) == 1


class TestReset:
    def test_reset_session_clears(self):
        guard = SequenceGuard()
        # 先录入 data_exfiltration 序列的前两步
        guard.record(SequenceEvent(session_id="rs-1", operation="read", target="credential"))
        guard.record(SequenceEvent(session_id="rs-1", operation="write", target="network"))
        guard.reset_session("rs-1")
        result = guard.record(SequenceEvent(session_id="rs-1", operation="delete", target="log"))
        # B2 审计修复：原 assert True 恒绿——reset 后历史必须真清空，
        # 否则第三步会凑齐 data_exfiltration 禁止序列而触发（M14 变异实证该断言缺失）
        assert result is None, f"reset_session 后历史未清空，半截序列误触: {result}"

    def test_reset_all(self):
        guard = SequenceGuard()
        guard.record(SequenceEvent(session_id="ra-1", operation="read", target="credential"))
        guard.record(SequenceEvent(session_id="ra-1", operation="write", target="network"))
        guard.reset_all()
        result = guard.record(SequenceEvent(session_id="ra-1", operation="delete", target="log"))
        # B2 审计修复：同上
        assert result is None, f"reset_all 后历史未清空，半截序列误触: {result}"
