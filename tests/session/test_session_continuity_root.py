# [A_test] module_id: MOD-GOV_session_continuity_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-430 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §

# [MODULE] tests.test_session_continuity

# [INVARIANTS] tests must not pollute real project data; all paths use tmp_path

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] tests raise AssertionError on failure; no side effects on real DB

# [TESTS] python -m pytest tests/test_session_continuity.py -q
# [TTL] task_bound

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from zephyr.shared.session.session_continuity import (
    ContinuityContext,
    SessionContinuity,
    SessionState,
)


@pytest.fixture
def tmp_env(tmp_path: Path) -> dict[str, Path]:
    db_path = tmp_path / "test_metadata.db"
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)
    return {"db_path": db_path, "project_root": project_root}


@pytest.fixture
def sc(tmp_env: dict[str, Path]) -> SessionContinuity:
    return SessionContinuity(
        db_path=tmp_env["db_path"],
        project_root=tmp_env["project_root"],
    )


class TestSessionState:
    def test_default_instantiation(self):
        state = SessionState()
        assert state.session_id == ""
        assert state.dialogue_number == 0
        assert state.current_layer == 0  # 生产跟进：int 型（session_continuity.py L64）
        assert state.cards_completed == []
        assert state.cards_failed == []
        assert state.last_checkpoint_json == ""
        assert state.last_journal_line == 0  # 生产跟进：int 型（L68）
        assert state.timestamp_utc == ""
        assert state.metadata == {}

    def test_custom_instantiation(self):
        state = SessionState(
            session_id="sess-20260522-001",
            dialogue_number=5,
            current_layer="L1",
            cards_completed=["card-A", "card-B"],
            cards_failed=["card-C"],
            last_checkpoint_json='{"step": 3}',
            last_journal_line="line 42",
            timestamp_utc="2026-05-22T10:00:00+00:00",
            metadata={"key": "value"},
        )
        assert state.session_id == "sess-20260522-001"
        assert state.dialogue_number == 5
        assert state.current_layer == "L1"
        assert state.cards_completed == ["card-A", "card-B"]
        assert state.cards_failed == ["card-C"]
        assert state.last_checkpoint_json == '{"step": 3}'
        assert state.last_journal_line == "line 42"
        assert state.timestamp_utc == "2026-05-22T10:00:00+00:00"
        assert state.metadata == {"key": "value"}

    def test_lists_are_independent(self):
        state1 = SessionState()
        state2 = SessionState()
        state1.cards_completed.append("X")
        assert state2.cards_completed == []


class TestContinuityContext:
    def test_default_instantiation(self):
        ctx = ContinuityContext()
        assert ctx.progress_summary == ""
        assert ctx.remaining_cards == []
        assert ctx.next_action == ""

    def test_custom_instantiation(self):
        ctx = ContinuityContext(
            progress_summary="3 done, 1 failed",
            remaining_cards=["card-C"],
            next_action="Retry card-C",
        )
        assert ctx.progress_summary == "3 done, 1 failed"
        assert ctx.remaining_cards == ["card-C"]
        assert ctx.next_action == "Retry card-C"


class TestSessionContinuityInit:
    def test_custom_paths(self, tmp_env: dict[str, Path]):
        sc = SessionContinuity(
            db_path=tmp_env["db_path"],
            project_root=tmp_env["project_root"],
        )
        assert sc.db_path == tmp_env["db_path"]
        assert sc.project_root == tmp_env["project_root"]

    def test_db_schema_created(self, tmp_env: dict[str, Path]):
        sc = SessionContinuity(
            db_path=tmp_env["db_path"],
            project_root=tmp_env["project_root"],
        )
        conn = sqlite3.connect(str(tmp_env["db_path"]))
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='handoffs'").fetchall()
        conn.close()
        assert len(tables) == 1

    def test_none_db_path_uses_default(self, tmp_path: Path):
        sc = SessionContinuity(project_root=tmp_path)
        assert (
            sc.db_path == tmp_path / "data" / "databases" / "session_continuity.db"
        )  # 生产跟进：独立库（L93/132/134）


class TestSaveLoadSessionState:
    def test_save_and_load_roundtrip(self, sc: SessionContinuity, tmp_env: dict[str, Path]):
        state = SessionState(
            session_id="sess-roundtrip",
            dialogue_number=3,
            current_layer="L2",
            cards_completed=["card-1", "card-2"],
            cards_failed=["card-3"],
            last_checkpoint_json='{"step": 2}',
            last_journal_line="journal line 10",
            timestamp_utc="2026-05-22T12:00:00+00:00",
            metadata={"env": "test"},
        )
        path = sc.save_session_state(state)
        assert path.exists()

        loaded = sc.load_session_state("sess-roundtrip")
        assert loaded is not None
        assert loaded.session_id == "sess-roundtrip"
        assert loaded.dialogue_number == 3
        assert loaded.current_layer == "L2"
        assert loaded.cards_completed == ["card-1", "card-2"]
        assert loaded.cards_failed == ["card-3"]
        assert loaded.last_checkpoint_json == '{"step": 2}'
        assert loaded.last_journal_line == "journal line 10"
        assert loaded.timestamp_utc == "2026-05-22T12:00:00+00:00"
        assert loaded.metadata == {"env": "test"}

    def test_save_auto_fills_timestamp(self, sc: SessionContinuity):
        state = SessionState(session_id="sess-auto-ts")
        assert state.timestamp_utc == ""
        sc.save_session_state(state)
        assert state.timestamp_utc != ""

    def test_load_nonexistent_returns_none(self, sc: SessionContinuity):
        result = sc.load_session_state("no-such-session")
        assert result is None

    def test_save_creates_json_file(self, sc: SessionContinuity, tmp_env: dict[str, Path]):
        state = SessionState(session_id="sess-file-check", cards_completed=["A"])
        path = sc.save_session_state(state)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["session_id"] == "sess-file-check"
        assert data["cards_completed"] == ["A"]

    def test_save_also_writes_handoff_row(self, sc: SessionContinuity, tmp_env: dict[str, Path]):
        state = SessionState(
            session_id="sess-db-check",
            cards_completed=["X"],
            timestamp_utc="2026-05-22T14:00:00+00:00",
        )
        sc.save_session_state(state)
        conn = sqlite3.connect(str(tmp_env["db_path"]))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM handoffs WHERE session_id = ?", ("sess-db-check",)).fetchone()
        conn.close()
        assert row is not None
        assert json.loads(row["completed_tasks"]) == ["X"]


class TestGenerateContinuityContext:
    def test_with_completed_and_failed(self, sc: SessionContinuity):
        state = SessionState(
            cards_completed=["card-A", "card-B"],
            cards_failed=["card-C"],
        )
        ctx = sc.generate_continuity_context(state)
        assert "2 cards completed" in ctx.progress_summary  # 生产措辞跟进
        assert "1 failed" in ctx.progress_summary  # 生产措辞跟进
        assert ctx.remaining_cards == ["card-C"]
        assert "card-B" in ctx.next_action

    def test_with_only_failed(self, sc: SessionContinuity):
        state = SessionState(cards_failed=["card-X"])
        ctx = sc.generate_continuity_context(state)
        assert "0 cards completed" in ctx.progress_summary  # 生产措辞跟进
        assert "1 failed" in ctx.progress_summary  # 生产措辞跟进
        assert ctx.remaining_cards == ["card-X"]
        assert "card-X" in ctx.next_action

    def test_with_empty_state(self, sc: SessionContinuity):
        state = SessionState()
        ctx = sc.generate_continuity_context(state)
        assert "0 cards completed" in ctx.progress_summary  # 生产措辞跟进
        assert ctx.remaining_cards == []
        assert ctx.next_action == "Start fresh"  # 生产措辞跟进（与 unit 文件口径一致）

    def test_with_completed_no_failed(self, sc: SessionContinuity):
        state = SessionState(cards_completed=["card-1"])
        ctx = sc.generate_continuity_context(state)
        assert ctx.remaining_cards == []
        assert "card-1" in ctx.next_action


class TestGenerateAndSave:
    def test_with_cards(self, sc: SessionContinuity, tmp_env: dict[str, Path]):
        path = sc.generate_and_save(
            session_id="sess-gas",
            cards_completed=["T1"],
            cards_failed=["T2"],
        )
        assert path is not None
        assert Path(path).exists()
        loaded = sc.load_session_state("sess-gas")
        assert loaded is not None
        assert loaded.cards_completed == ["T1"]
        assert loaded.cards_failed == ["T2"]

    def test_with_no_cards(self, sc: SessionContinuity):
        path = sc.generate_and_save(session_id="sess-gas-empty")
        assert path is not None
        assert Path(path).exists()

    def test_with_none_cards_treated_as_empty(self, sc: SessionContinuity):
        path = sc.generate_and_save(
            session_id="sess-gas-none",
            cards_completed=None,
            cards_failed=None,
        )
        assert path is not None
        loaded = sc.load_session_state("sess-gas-none")
        assert loaded is not None
        assert loaded.cards_completed == []
        assert loaded.cards_failed == []


class TestGetLatestHandoff:
    def test_no_handoffs_returns_none(self, sc: SessionContinuity):
        result = sc.get_latest_handoff()
        assert result is None

    def test_with_saved_handoff(self, sc: SessionContinuity):
        state = SessionState(
            session_id="sess-handoff",
            cards_completed=["A", "B"],
            timestamp_utc="2026-05-22T15:00:00+00:00",
        )
        sc.save_session_state(state)
        result = sc.get_latest_handoff()
        assert result is not None
        assert result["session_id"] == "sess-handoff"
        assert result["completed_tasks"] == ["A", "B"]

    def test_latest_among_multiple(self, sc: SessionContinuity):
        sc.save_session_state(
            SessionState(
                session_id="sess-early",
                timestamp_utc="2026-05-22T10:00:00+00:00",
            )
        )
        sc.save_session_state(
            SessionState(
                session_id="sess-late",
                timestamp_utc="2026-05-22T20:00:00+00:00",
            )
        )
        result = sc.get_latest_handoff()
        assert result is not None
        assert result["session_id"] == "sess-late"


class TestRestoreSession:
    def test_no_handoff_returns_none(self, sc: SessionContinuity):
        assert sc.restore_session() is None

    def test_returns_latest_handoff(self, sc: SessionContinuity):
        sc.save_session_state(
            SessionState(
                session_id="sess-restore",
                cards_completed=["R1"],
                timestamp_utc="2026-05-22T16:00:00+00:00",
            )
        )
        result = sc.restore_session()
        assert result is not None
        assert result["session_id"] == "sess-restore"


class TestPrintRestoreSummary:
    def test_no_handoff_prints_first_session(self, sc: SessionContinuity, capsys: pytest.CaptureFixture[str]):
        sc.print_restore_summary()
        output = capsys.readouterr().out
        assert "没有发现历史交接包" in output or "冷启动" in output  # 生产文案跟进（L734）

    def test_with_handoff_prints_summary(self, sc: SessionContinuity, capsys: pytest.CaptureFixture[str]):
        sc.save_session_state(
            SessionState(
                session_id="sess-print",
                cards_completed=["P1"],
                timestamp_utc="2026-05-22T17:00:00+00:00",
            )
        )
        sc.print_restore_summary()
        output = capsys.readouterr().out
        assert "sess-print" in output


class TestDetectAgentContext:
    def test_returns_dict_with_required_keys(self, sc: SessionContinuity):
        ctx = sc.detect_agent_context()
        assert "ide_source" in ctx
        assert "maturity" in ctx
        assert "role" in ctx
        assert "auto_guard_eligible" in ctx
        assert "owner_approved" in ctx

    def test_unknown_env_returns_unknown(self, sc: SessionContinuity):
        ctx = sc.detect_agent_context()
        assert ctx["ide_source"] in ("unknown", "trae", "cursor", "vscode")


class TestAutoGenerateQuestions:
    def test_with_blocked_items(self, sc: SessionContinuity):
        blocked = [{"task_id": "T1"}, {"task_id": "T2"}]
        questions = sc.auto_generate_questions(blocked, 0)
        assert any("T1" in q for q in questions)

    def test_with_many_completed(self, sc: SessionContinuity):
        questions = sc.auto_generate_questions([], 15)
        assert any("15" in q for q in questions)

    def test_with_empty_inputs(self, sc: SessionContinuity):
        questions = sc.auto_generate_questions([], 0)
        assert isinstance(questions, list)
        assert len(questions) >= 1

    def test_always_includes_blueprint_question(self, sc: SessionContinuity):
        questions = sc.auto_generate_questions([], 0)
        assert any("蓝图" in q for q in questions)
