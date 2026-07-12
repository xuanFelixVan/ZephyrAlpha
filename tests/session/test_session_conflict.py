# [A_test] module_id: SRC-TST-1582 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_session_conflict
# [INVARIANTS] file-level mutual exclusion across sessions; same session re-register overwrites
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] register_session returns False on conflict; release_session silently ignores unknown session
# [TESTS] test_session_conflict.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.lifecycle.session_conflict import SessionConflictGuard


class TestSessionConflictGuard:
    @pytest.fixture()
    def guard(self):
        return SessionConflictGuard()

    def test_register_session_no_conflict(self, guard):
        result = guard.register_session("s1", ["file_a.py", "file_b.py"])
        assert result is True

    def test_register_session_empty_files(self, guard):
        result = guard.register_session("s1", [])
        assert result is True

    def test_register_two_sessions_no_overlap(self, guard):
        assert guard.register_session("s1", ["file_a.py"]) is True
        assert guard.register_session("s2", ["file_b.py"]) is True

    def test_register_two_sessions_with_overlap(self, guard):
        guard.register_session("s1", ["file_a.py", "file_b.py"])
        result = guard.register_session("s2", ["file_b.py", "file_c.py"])
        assert result is False

    def test_register_same_session_id_replaces(self, guard):
        guard.register_session("s1", ["file_a.py"])
        result = guard.register_session("s1", ["file_b.py"])
        assert result is True

    def test_register_conflict_after_release(self, guard):
        guard.register_session("s1", ["file_a.py"])
        guard.release_session("s1")
        result = guard.register_session("s2", ["file_a.py"])
        assert result is True

    def test_release_session(self, guard):
        guard.register_session("s1", ["file_a.py"])
        guard.release_session("s1")
        assert "s1" not in guard._active_sessions

    def test_release_nonexistent_session(self, guard):
        guard.release_session("nonexistent")

    def test_multiple_files_conflict(self, guard):
        guard.register_session("s1", ["a.py", "b.py", "c.py"])
        result = guard.register_session("s2", ["c.py"])
        assert result is False

    def test_three_sessions_first_conflicts_with_third(self, guard):
        guard.register_session("s1", ["x.py"])
        guard.register_session("s2", ["y.py"])
        result = guard.register_session("s3", ["x.py"])
        assert result is False

    def test_no_self_conflict(self, guard):
        guard.register_session("s1", ["file_a.py"])
        result = guard.register_session("s1", ["file_a.py", "file_b.py"])
        assert result is True
