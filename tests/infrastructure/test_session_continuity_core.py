# [A_test] module_id: SRC-TST-1849 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-477 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.core.test_session_continuity
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
test_session_continuity.py — SessionContinuity 单元测试 (core/ variant)
========================================================================
依据：MOD-INF-039 v0.6.0 + SRC-0056

Tests the canonical session/ version imported through core/ shim.
"""


import json
from datetime import UTC, datetime

from zephyr.shared.session.session_continuity import (
    SessionContinuity,
    SessionState,
)


def _make_state(session_id: str = "core-test", **overrides) -> SessionState:
    defaults = dict(
        session_id=session_id,
        dialogue_number=1,
        current_layer=0,
        cards_completed=["CP-1"],
        cards_failed=[],
        last_checkpoint_json="{}",
        last_journal_line=0,
        timestamp_utc=datetime.now(UTC).isoformat(),
        metadata={},
    )
    defaults.update(overrides)
    return SessionState(**defaults)


class TestSessionContinuityInit:
    def test_init_with_project_root(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        assert sc._project_root == tmp_path


class TestGenerateAndSave:
    def test_generates_session_file(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        path = sc.generate_and_save(
            session_id="gen-test",
            cards_completed=["CP-1"],
            cards_failed=[],
        )
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["session_id"] == "gen-test"

    def test_empty_generates_empty_cards(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        path = sc.generate_and_save(session_id="empty")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["cards_completed"] == []
        assert data["cards_failed"] == []

    def test_corrupt_load_returns_none(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        sessions_dir = tmp_path / "session_logs"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        (sessions_dir / "bad.json").write_text("{invalid", encoding="utf-8")
        assert sc.load_session_state("bad") is None


class TestRestoreSession:
    def test_restore_returns_none_when_no_sessions(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        assert sc.load_session_state("nonexistent") is None

    def test_restore_returns_latest_session(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state1 = _make_state(session_id="first", cards_completed=["A"])
        state2 = _make_state(session_id="second", cards_completed=["A", "B"])
        sc.save_session_state(state1)
        sc.save_session_state(state2)
        loaded = sc.load_session_state("second")
        assert loaded is not None
        assert loaded.session_id == "second"
        assert loaded.cards_completed == ["A", "B"]


class TestPrintRestoreSummary:
    def test_print_on_empty_does_not_crash(self, tmp_path, capsys):
        sc = SessionContinuity(project_root=tmp_path)
        sc.print_restore_summary()
        captured = capsys.readouterr()
        assert "冷启动" in captured.out or "没有发现" in captured.out

    def test_print_restore_after_generate(self, tmp_path, capsys):
        sc = SessionContinuity(project_root=tmp_path)
        sc.generate_and_save(
            session_id="print-test",
            cards_completed=["CP-1"],
            cards_failed=[],
        )
        sc.print_restore_summary()
        captured = capsys.readouterr()
        assert "print-test" in captured.out
