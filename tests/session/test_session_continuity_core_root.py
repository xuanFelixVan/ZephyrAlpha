# [A_test] module_id: SRC-TST-1583 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-431 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_session_continuity_core
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
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
        s = SessionState(
            session_id="s1",
            dialogue_number=1,
            current_layer=0,
            cards_completed=[],
            cards_failed=[],
            last_checkpoint_json="",
            last_journal_line=0,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert s.metadata == {}

    def test_custom_metadata(self):
        s = SessionState(
            session_id="s2",
            dialogue_number=2,
            current_layer=1,
            cards_completed=["TASK-001"],
            cards_failed=["TASK-002"],
            last_checkpoint_json="cp",
            last_journal_line=10,
            timestamp_utc="2026-01-01T00:00:00+00:00",
            metadata={"key": "value"},
        )
        assert s.metadata == {"key": "value"}
        assert s.cards_completed == ["TASK-001"]
        assert s.cards_failed == ["TASK-002"]


class TestContinuityContextDataclass:
    def test_fields(self):
        ctx = ContinuityContext(
            task_id="SESSION-s1",
            progress_summary="1 cards completed, 0 failed",
            remaining_cards=[],
            key_state={"layer": 0},
            next_action="Continue from checkpoint",
        )
        assert ctx.task_id == "SESSION-s1"
        assert ctx.remaining_cards == []


class TestSessionContinuity:
    def test_init_with_project_root(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        assert sc._project_root == tmp_path
        assert sc._sessions_dir == tmp_path / "session_logs"

    def test_init_default_root(self):
        sc = SessionContinuity()
        assert sc._project_root == Path.cwd()

    def test_save_session_state(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-100",
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
        assert data["session_id"] == "session-100"
        assert data["cards_completed"] == ["TASK-001"]
        assert data["metadata"] == {"env": "test"}

    def test_save_session_state_creates_dir(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-101",
            dialogue_number=1,
            current_layer=0,
            cards_completed=[],
            cards_failed=[],
            last_checkpoint_json="",
            last_journal_line=0,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        path = sc.save_session_state(state)
        assert (tmp_path / "session_logs").is_dir()
        assert path.exists()

    def test_load_session_state_existing(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-200",
            dialogue_number=3,
            current_layer=2,
            cards_completed=["TASK-001", "TASK-002"],
            cards_failed=["TASK-003"],
            last_checkpoint_json="cp2",
            last_journal_line=15,
            timestamp_utc="2026-01-01T00:00:00+00:00",
            metadata={"retry": True},
        )
        sc.save_session_state(state)
        loaded = sc.load_session_state("session-200")
        assert loaded is not None
        assert loaded.session_id == "session-200"
        assert loaded.dialogue_number == 3
        assert loaded.current_layer == 2
        assert loaded.cards_completed == ["TASK-001", "TASK-002"]
        assert loaded.cards_failed == ["TASK-003"]
        assert loaded.metadata == {"retry": True}

    def test_load_session_state_not_found(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        result = sc.load_session_state("nonexistent")
        assert result is None

    def test_load_session_state_corrupt_json(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        sessions_dir = tmp_path / "session_logs"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        corrupt = sessions_dir / "corrupt.json"
        corrupt.write_text("not valid json{{{", encoding="utf-8")
        result = sc.load_session_state("corrupt")
        assert result is None

    def test_load_session_state_missing_key(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        sessions_dir = tmp_path / "session_logs"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        bad = sessions_dir / "badkey.json"
        bad.write_text(json.dumps({"session_id": "badkey"}), encoding="utf-8")
        result = sc.load_session_state("badkey")
        assert result is None

    def test_generate_continuity_context_with_progress(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-300",
            dialogue_number=5,
            current_layer=2,
            cards_completed=["TASK-001", "TASK-002", "TASK-003"],
            cards_failed=["TASK-004", "TASK-005"],
            last_checkpoint_json="cp3",
            last_journal_line=20,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        ctx = sc.generate_continuity_context(state)
        assert ctx.task_id == "SESSION-session-300"
        assert "3 cards completed" in ctx.progress_summary
        assert "2 failed" in ctx.progress_summary
        assert ctx.remaining_cards == ["TASK-004", "TASK-005"]
        assert ctx.key_state["layer"] == 2
        assert ctx.key_state["last_journal_line"] == 20
        assert ctx.next_action == "Continue from checkpoint"

    def test_generate_continuity_context_no_progress(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-301",
            dialogue_number=1,
            current_layer=0,
            cards_completed=[],
            cards_failed=[],
            last_checkpoint_json="",
            last_journal_line=0,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        ctx = sc.generate_continuity_context(state)
        assert "0 cards completed" in ctx.progress_summary
        assert ctx.next_action == "Start fresh"
        assert ctx.remaining_cards == []

    def test_load_checkpoint_existing(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        journals_dir = tmp_path / "_journals"
        journals_dir.mkdir(parents=True, exist_ok=True)
        cp = journals_dir / "checkpoint_5.json"
        cp_data = {"step": 5, "status": "in_progress"}
        cp.write_text(json.dumps(cp_data), encoding="utf-8")
        result = sc.load_checkpoint(5)
        assert result == cp_data

    def test_load_checkpoint_not_found(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        result = sc.load_checkpoint(999)
        assert result is None

    def test_load_checkpoint_corrupt(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        journals_dir = tmp_path / "_journals"
        journals_dir.mkdir(parents=True, exist_ok=True)
        bad_cp = journals_dir / "checkpoint_1.json"
        bad_cp.write_text("bad json{{{", encoding="utf-8")
        result = sc.load_checkpoint(1)
        assert result is None

    def test_generate_and_save(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        path = sc.generate_and_save(
            session_id="session-400",
            cards_completed=["TASK-010"],
            cards_failed=["TASK-011"],
            metadata={"source": "auto"},
        )
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["session_id"] == "session-400"
        assert data["cards_completed"] == ["TASK-010"]
        assert data["cards_failed"] == ["TASK-011"]
        assert data["metadata"] == {"source": "auto"}

    def test_generate_and_save_defaults(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        path = sc.generate_and_save(session_id="session-401")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["cards_completed"] == []
        assert data["cards_failed"] == []
        assert data["metadata"] == {}

    def test_validate_sys_master_dispatch_missing_file(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        result = sc.validate_sys_master_dispatch()
        assert result["valid"] is False
        assert "missing" in result["error"]

    def test_validate_sys_master_dispatch_no_frontmatter(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        bp_dir = tmp_path / "docs" / "03_modules" / "_system_master"
        bp_dir.mkdir(parents=True, exist_ok=True)
        bp = bp_dir / "blueprint.md"
        bp.write_text("No frontmatter here", encoding="utf-8")
        result = sc.validate_sys_master_dispatch()
        assert result["valid"] is False
        assert "frontmatter" in result["error"]

    def test_validate_sys_master_dispatch_valid(self, tmp_path):
        sc = SessionContinuity(project_root=tmp_path)
        bp_dir = tmp_path / "docs" / "03_modules" / "_system_master"
        bp_dir.mkdir(parents=True, exist_ok=True)
        bp = bp_dir / "blueprint.md"
        bp_content = """---
version: "1.0.0"
ai_role_instruction: "Follow rules (1) (2) (3)"
depends_on:
  - MOD-INF-001
---

### 0.2 AI Agent 分派表

| 任务域 | 模块 |
|--------|------|
| Core | core |
| Infra | infra |
"""
        bp.write_text(bp_content, encoding="utf-8")
        result = sc.validate_sys_master_dispatch()
        assert result["valid"] is True
        assert result["version"] == "1.0.0"
        assert result["ai_rules_count"] == 3
        assert result["dispatch_domains"] >= 1

    def test_print_restore_summary_no_sessions(self, tmp_path, capsys):
        sc = SessionContinuity(project_root=tmp_path)
        sc.print_restore_summary()
        captured = capsys.readouterr()
        assert "冷启动" in captured.out or "没有发现" in captured.out

    def test_print_restore_summary_with_session(self, tmp_path, capsys):
        sc = SessionContinuity(project_root=tmp_path)
        state = SessionState(
            session_id="session-500",
            dialogue_number=2,
            current_layer=1,
            cards_completed=["TASK-001"],
            cards_failed=[],
            last_checkpoint_json="",
            last_journal_line=10,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        sc.save_session_state(state)
        sc.print_restore_summary()
        captured = capsys.readouterr()
        assert "session-500" in captured.out
