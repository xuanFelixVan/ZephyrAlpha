# [A_test] module_id: SRC-TST-2064 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-681 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_session_continuity
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
test_session_continuity.py — SessionContinuity 单元测试
========================================================
依据：MOD-INF-039 v0.6.0 + SRC-0056 (session/ canonical version)

覆盖率目标：
  - save/load session state round-trip
  - load nonexistent session returns None
  - generate_continuity_context correct output
  - print_restore_summary does not crash
  - generate_and_save creates session file
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from zephyr.shared.session.session_continuity import (
    ContinuityContext,
    SessionContinuity,
    SessionState,
)


def _make_state(session_id: str = "test-001", **overrides) -> SessionState:
    defaults = dict(
        session_id=session_id,
        dialogue_number=1,
        current_layer=0,
        cards_completed=["CP-1", "CP-2"],
        cards_failed=[],
        last_checkpoint_json="{}",
        last_journal_line=42,
        timestamp_utc=datetime.now(UTC).isoformat(),
        metadata={},
    )
    defaults.update(overrides)
    return SessionState(**defaults)


class TestSaveAndLoad:
    def test_save_creates_json_file(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = _make_state()
        path = sc.save_session_state(state)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["session_id"] == "test-001"
        assert data["cards_completed"] == ["CP-1", "CP-2"]

    def test_load_round_trip(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = _make_state(dialogue_number=7, current_layer=3)
        sc.save_session_state(state)
        loaded = sc.load_session_state("test-001")
        assert loaded is not None
        assert loaded.session_id == "test-001"
        assert loaded.dialogue_number == 7
        assert loaded.current_layer == 3
        assert loaded.cards_completed == ["CP-1", "CP-2"]

    def test_load_nonexistent_returns_none(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        assert sc.load_session_state("no-such-session") is None

    def test_load_corrupt_json_returns_none(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        sessions_dir = tmp_path / "session_logs"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        (sessions_dir / "bad.json").write_text("not json", encoding="utf-8")
        assert sc.load_session_state("bad") is None


class TestContinuityContext:
    def test_generate_continuity_context(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = _make_state(cards_completed=["A", "B", "C"], cards_failed=["X"])
        ctx = sc.generate_continuity_context(state)
        assert isinstance(ctx, ContinuityContext)
        assert "3 cards completed" in ctx.progress_summary
        assert "1 failed" in ctx.progress_summary
        assert ctx.remaining_cards == ["X"]
        assert ctx.next_action == "Continue from checkpoint"

    def test_generate_continuity_context_empty(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = _make_state(cards_completed=[], cards_failed=[])
        ctx = sc.generate_continuity_context(state)
        assert "0 cards completed" in ctx.progress_summary
        assert ctx.next_action == "Start fresh"


class TestGenerateAndSave:
    def test_generate_and_save_creates_file(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        path = sc.generate_and_save(
            session_id="gen-test",
            cards_completed=["T-1"],
            cards_failed=["T-2"],
        )
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["session_id"] == "gen-test"
        assert data["cards_completed"] == ["T-1"]
        assert data["cards_failed"] == ["T-2"]

    def test_generate_and_save_empty(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        path = sc.generate_and_save(session_id="empty")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["cards_completed"] == []
        assert data["cards_failed"] == []


class TestPrintRestoreSummary:
    def test_print_does_not_crash_no_sessions(self, tmp_path, capsys):
        sc = SessionContinuity(project_root=tmp_path)
        sc.print_restore_summary()
        captured = capsys.readouterr()
        assert "冷启动" in captured.out or "没有发现" in captured.out

    def test_print_with_existing_session(self, tmp_path, capsys):
        sc = SessionContinuity(project_root=tmp_path)
        sc.generate_and_save(
            session_id="restore-test",
            cards_completed=["CP-1"],
            cards_failed=[],
        )
        sc.print_restore_summary()
        captured = capsys.readouterr()
        assert "restore-test" in captured.out
