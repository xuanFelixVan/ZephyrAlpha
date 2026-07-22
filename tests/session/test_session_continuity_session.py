# [A_test] module_id: MOD-GOV_session_continuity_session | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-432 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_session_continuity_session
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] pytest tests/test_session_continuity_session.py
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.shared.session.session_continuity import (
    ContinuityContext,
    SessionContinuity,
    SessionState,
)


class TestSessionStateDataclass:
    def test_default_metadata(self):
        state = SessionState(
            session_id="s-001",
            dialogue_number=1,
            current_layer=0,
            cards_completed=[],
            cards_failed=[],
            last_checkpoint_json="",
            last_journal_line=0,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert state.metadata == {}

    def test_custom_metadata(self):
        state = SessionState(
            session_id="s-002",
            dialogue_number=2,
            current_layer=1,
            cards_completed=["TASK-001"],
            cards_failed=["TASK-002"],
            last_checkpoint_json="cp",
            last_journal_line=10,
            timestamp_utc="2026-01-01T00:00:00+00:00",
            metadata={"key": "value"},
        )
        assert state.metadata == {"key": "value"}
        assert state.cards_completed == ["TASK-001"]


class TestContinuityContextDataclass:
    def test_fields(self):
        ctx = ContinuityContext(
            task_id="SESSION-s-001",
            progress_summary="1 completed",
            remaining_cards=["TASK-002"],
            key_state={"layer": 0},
            next_action="Continue from checkpoint",
        )
        assert ctx.task_id == "SESSION-s-001"
        assert ctx.remaining_cards == ["TASK-002"]


class TestSessionContinuity:
    def test_instantiation_with_path(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        assert sc._project_root == tmp_path
        assert sc._sessions_dir == tmp_path / "session_logs"

    def test_instantiation_default(self):
        sc = SessionContinuity()
        assert sc._project_root == Path.cwd()

    def test_save_session_state(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-20260522-001",
            dialogue_number=1,
            current_layer=0,
            cards_completed=["TASK-001"],
            cards_failed=[],
            last_checkpoint_json="cp1",
            last_journal_line=5,
            timestamp_utc="2026-01-01T00:00:00+00:00",
            metadata={"env": "test"},
        )
        result_path = sc.save_session_state(state)
        assert result_path.exists()
        data = json.loads(result_path.read_text(encoding="utf-8"))
        assert data["session_id"] == "session-20260522-001"
        assert data["cards_completed"] == ["TASK-001"]
        assert data["metadata"] == {"env": "test"}

    def test_load_session_state_exists(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-20260522-002",
            dialogue_number=2,
            current_layer=1,
            cards_completed=["TASK-001", "TASK-002"],
            cards_failed=["TASK-003"],
            last_checkpoint_json="cp2",
            last_journal_line=10,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        sc.save_session_state(state)
        loaded = sc.load_session_state("session-20260522-002")
        assert loaded is not None
        assert loaded.session_id == "session-20260522-002"
        assert loaded.dialogue_number == 2
        assert loaded.cards_completed == ["TASK-001", "TASK-002"]
        assert loaded.cards_failed == ["TASK-003"]

    def test_load_session_state_not_found(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        result = sc.load_session_state("nonexistent")
        assert result is None

    def test_load_session_state_malformed_json(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        sessions_dir = tmp_path / "session_logs"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        bad_file = sessions_dir / "bad-session.json"
        bad_file.write_text("not valid json{{{", encoding="utf-8")
        result = sc.load_session_state("bad-session")
        assert result is None

    def test_load_session_state_missing_key(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        sessions_dir = tmp_path / "session_logs"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        partial_file = sessions_dir / "partial-session.json"
        partial_file.write_text(json.dumps({"session_id": "partial"}), encoding="utf-8")
        result = sc.load_session_state("partial-session")
        assert result is None

    def test_generate_continuity_context_with_completed(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-20260522-003",
            dialogue_number=1,
            current_layer=2,
            cards_completed=["TASK-001", "TASK-002"],
            cards_failed=["TASK-003"],
            last_checkpoint_json="cp3",
            last_journal_line=15,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        ctx = sc.generate_continuity_context(state)
        assert ctx.task_id == "SESSION-session-20260522-003"
        assert "2 cards completed" in ctx.progress_summary
        assert "1 failed" in ctx.progress_summary
        assert ctx.remaining_cards == ["TASK-003"]
        assert ctx.key_state["layer"] == 2
        assert ctx.next_action == "Continue from checkpoint"

    def test_generate_continuity_context_fresh(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-20260522-004",
            dialogue_number=1,
            current_layer=0,
            cards_completed=[],
            cards_failed=[],
            last_checkpoint_json="",
            last_journal_line=0,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        ctx = sc.generate_continuity_context(state)
        assert ctx.next_action == "Start fresh"
        assert ctx.remaining_cards == []

    def test_load_checkpoint_not_found(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        result = sc.load_checkpoint(1)
        assert result is None

    def test_load_checkpoint_exists(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        journals_dir = tmp_path / "_journals"
        journals_dir.mkdir(parents=True, exist_ok=True)
        cp_file = journals_dir / "checkpoint_1.json"
        cp_data = {"step": 1, "status": "active"}
        cp_file.write_text(json.dumps(cp_data), encoding="utf-8")
        result = sc.load_checkpoint(1)
        assert result == cp_data

    def test_load_checkpoint_malformed(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        journals_dir = tmp_path / "_journals"
        journals_dir.mkdir(parents=True, exist_ok=True)
        cp_file = journals_dir / "checkpoint_2.json"
        cp_file.write_text("bad json{{", encoding="utf-8")
        result = sc.load_checkpoint(2)
        assert result is None

    def test_generate_and_save(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        result_path = sc.generate_and_save(
            session_id="session-20260522-005",
            cards_completed=["TASK-010"],
            cards_failed=["TASK-011"],
            metadata={"source": "test"},
        )
        assert result_path.exists()
        data = json.loads(result_path.read_text(encoding="utf-8"))
        assert data["session_id"] == "session-20260522-005"
        assert data["cards_completed"] == ["TASK-010"]
        assert data["cards_failed"] == ["TASK-011"]
        assert data["metadata"] == {"source": "test"}

    def test_generate_and_save_defaults(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        result_path = sc.generate_and_save(session_id="session-20260522-006")
        data = json.loads(result_path.read_text(encoding="utf-8"))
        assert data["cards_completed"] == []
        assert data["cards_failed"] == []
        assert data["metadata"] == {}

    def test_validate_sys_master_dispatch_missing(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        result = sc.validate_sys_master_dispatch()
        assert result["valid"] is False
        assert "missing" in result["error"]

    def test_validate_sys_master_dispatch_no_frontmatter(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        bp_dir = tmp_path / "docs" / "03_modules" / "_system_master"
        bp_dir.mkdir(parents=True, exist_ok=True)
        bp_file = bp_dir / "blueprint.md"
        bp_file.write_text("No frontmatter here", encoding="utf-8")
        result = sc.validate_sys_master_dispatch()
        assert result["valid"] is False
        assert "frontmatter" in result["error"]

    def test_validate_sys_master_dispatch_valid(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        bp_dir = tmp_path / "docs" / "03_modules" / "_system_master"
        bp_dir.mkdir(parents=True, exist_ok=True)
        bp_file = bp_dir / "blueprint.md"
        bp_file.write_text(
            "---\nversion: '1.0'\ndepends_on: []\nai_role_instruction: 'Rule (1) Rule (2)'\n---\n\n### 0.2 AI Agent 分派表\n\n| 任务域 | 描述 |\n|-------|------|\n| A | desc |\n",
            encoding="utf-8",
        )
        result = sc.validate_sys_master_dispatch()
        assert result["valid"] is True
        assert result["version"] == "1.0"
        assert result["ai_rules_count"] == 2

    def test_print_restore_summary_no_sessions(self, tmp_path, capsys):
        sc = SessionContinuity(project_root=tmp_path)
        sc.print_restore_summary()
        captured = capsys.readouterr()
        assert "冷启动" in captured.out
