"""
test_session_continuity.py — SessionContinuity 单元测试
========================================================
依据：MOD-INF-006 v0.3.2 + B30 测试覆盖要求

覆盖率目标：
  - Handoff 自动生成（含空 repo）
  - Handoff 恢复（含无历史时）
  - print_restore_summary 不抛异常
  - 不同 TaskStatus 的汇总正确性
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.core.session_continuity import SessionContinuity


class MockTask:
    def __init__(self, task_id, title, status, priority=None, waiting_for=None, depends_on=None):
        self.task_id = task_id
        self.title = title
        self.status = status
        self.priority = priority or MagicMock(value="P2")
        self.waiting_for = waiting_for
        self.depends_on = depends_on or []


def _make_repo(status_map):
    """构造一个 mock TaskRepository，按状态返回 MockTask 列表"""
    repo = MagicMock()

    def list_by_status(st):
        if isinstance(st, str):
            return status_map.get(st, [])
        return status_map.get(st.value if hasattr(st, "value") else st, [])

    repo.list_by_status = MagicMock(side_effect=list_by_status)
    return repo


class TestSessionContinuityInit:
    def test_init_creates_handoffs_table(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        try:
            sc = SessionContinuity(db_path=db_path)
            conn = sqlite3.connect(db_path)
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='handoffs'"
            ).fetchall()
            conn.close()
            assert len(tables) == 1
        finally:
            Path(db_path).unlink(missing_ok=True)


class TestGenerateAndSave:
    def test_generates_summary_from_repo(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        try:
            sc = SessionContinuity(db_path=db_path)
            repo = _make_repo({
                "COMPLETED": [
                    MockTask("CP-1", "Fix MCP", "COMPLETED"),
                    MockTask("CP-2", "Fix Pipeline", "COMPLETED"),
                ],
                "IN_PROGRESS": [
                    MockTask("CP-3", "Session Continuity", "IN_PROGRESS"),
                ],
                "BLOCKED": [
                    MockTask("OPS-001", "Wait upstream", "BLOCKED", waiting_for="depends on SRC-042"),
                ],
                "READY": [
                    MockTask("CP-4", "Next task", "READY"),
                ],
            })

            handoff = sc.generate_and_save(session_id="test-001", task_repo=repo)

            assert handoff["session_id"] == "test-001"
            assert len(handoff["completed_tasks"]) == 2
            assert "CP-1" in handoff["completed_tasks"]
            assert "CP-2" in handoff["completed_tasks"]
            assert len(handoff["in_progress_tasks"]) == 1
            in_prog = handoff["in_progress_tasks"][0]
            assert isinstance(in_prog, dict), f"expected dict, got {type(in_prog)}"
            assert in_prog["task_id"] == "CP-3"
            assert in_prog["step"] is not None
            assert len(handoff["blocked_items"]) == 1
            assert handoff["blocked_items"][0]["task_id"] == "OPS-001"
            assert "depends on SRC-042" in handoff["blocked_items"][0]["reason"]
            assert len(handoff["next_actions"]) >= 1
            assert handoff["context_summary"] != ""
            assert "2" in handoff["context_summary"]
            assert len(handoff["open_questions"]) >= 1
            assert any("OPS-001" in q for q in handoff["open_questions"])
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_empty_repo_generates_empty_handoff(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        try:
            sc = SessionContinuity(db_path=db_path)
            repo = _make_repo({})

            handoff = sc.generate_and_save(session_id="empty", task_repo=repo)

            assert handoff["session_id"] == "empty"
            assert len(handoff["completed_tasks"]) == 0
            assert len(handoff["in_progress_tasks"]) == 0
            assert len(handoff["blocked_items"]) == 0
            assert handoff["context_summary"] != ""
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_repo_exceptions_are_handled(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        try:
            sc = SessionContinuity(db_path=db_path)
            repo = MagicMock()
            repo.list_by_status = MagicMock(side_effect=RuntimeError("db down"))

            handoff = sc.generate_and_save(session_id="crash", task_repo=repo)

            assert handoff["session_id"] == "crash"
            assert len(handoff["completed_tasks"]) == 0
        finally:
            Path(db_path).unlink(missing_ok=True)


class TestRestoreSession:
    def test_restore_returns_none_when_no_handoffs(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        try:
            sc = SessionContinuity(db_path=db_path)
            result = sc.restore_session()
            assert result is None
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_restore_returns_latest_handoff(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        try:
            sc = SessionContinuity(db_path=db_path)
            repo = _make_repo({
                "COMPLETED": [MockTask("CP-1", "Done", "COMPLETED")],
            })

            sc.generate_and_save(session_id="first", task_repo=repo)
            sc.generate_and_save(session_id="second", task_repo=repo)

            result = sc.restore_session()
            assert result is not None
            assert result["session_id"] == "second"
        finally:
            Path(db_path).unlink(missing_ok=True)


class TestPrintRestoreSummary:
    def test_print_on_empty_db_does_not_crash(self, capsys):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        try:
            sc = SessionContinuity(db_path=db_path)
            sc.print_restore_summary()
            captured = capsys.readouterr()
            assert "第一次 session" in captured.out
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_print_restore_after_generate(self, capsys):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        try:
            sc = SessionContinuity(db_path=db_path)
            repo = _make_repo({
                "COMPLETED": [MockTask("CP-1", "Fixed MCP", "COMPLETED")],
                "IN_PROGRESS": [MockTask("CP-2", "Bridge", "IN_PROGRESS")],
                "BLOCKED": [MockTask("OPS-001", "Blocked", "BLOCKED", waiting_for="missing dep")],
                "READY": [MockTask("CP-3", "Next", "READY")],
            })
            sc.generate_and_save(session_id="print-test", task_repo=repo)
            sc.print_restore_summary()
            captured = capsys.readouterr()
            assert "欢迎回来" in captured.out
            assert "CP-1" in captured.out
            assert "CP-2" in captured.out
            assert "OPS-001" in captured.out
        finally:
            Path(db_path).unlink(missing_ok=True)
