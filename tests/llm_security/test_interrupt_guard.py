# [A_test] module_id: MOD-GOV_interrupt_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_interrupt_guard
# [INVARIANTS] SIGINT/SIGTERM MUST触发WAL恢复;零"半修复"状态
# [MODIFY-GUARD] blueprint.md §3;auto_fix_config.yaml engine.wal_enabled
# [CONSUMERS] CI/CD;pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_interrupt_guard.py
# [TTL] task_bound

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from zephyr.infrastructure.auto_fix_engine.interrupt_guard import InterruptGuard


class TestInterruptGuardInstantiation:
    def test_default_wal_dir(self):
        guard = InterruptGuard()
        assert guard.wal_dir == Path("data/auto_fix/wal")

    def test_custom_wal_dir(self):
        guard = InterruptGuard(wal_dir="/tmp/custom_wal")
        assert guard.wal_dir == Path("/tmp/custom_wal")

    def test_default_db_path(self):
        from zephyr.shared.io.paths import DB_PATH

        guard = InterruptGuard()
        assert guard.db_path == DB_PATH

    def test_active_fixes_starts_empty(self):
        guard = InterruptGuard()
        assert guard.active_fixes == {}

    def test_handlers_not_installed_initially(self):
        guard = InterruptGuard()
        assert guard.handlers_installed is False


class TestInterruptGuardBeginFix:
    def test_begin_fix_adds_to_active_fixes(self):
        guard = InterruptGuard()
        guard.begin_fix("action-001", "target.py", "original content")
        assert "action-001" in guard.active_fixes
        assert guard.active_fixes["action-001"]["target"] == "target.py"

    def test_begin_fix_writes_wal_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = InterruptGuard(wal_dir=os.path.join(tmpdir, "wal"))
            guard.begin_fix("action-002", "target.py", "original")
            wal_file = Path(tmpdir) / "wal" / "action-002.wal"
            assert wal_file.exists()
            data = json.loads(wal_file.read_text(encoding="utf-8"))
            assert data["phase"] == "started"
            assert data["target"] == "target.py"

    def test_begin_fix_stores_before_content(self):
        guard = InterruptGuard()
        guard.begin_fix("action-003", "target.py", "before_content")
        assert guard.active_fixes["action-003"]["before_content"] == "before_content"

    def test_begin_fix_with_empty_before_content(self):
        guard = InterruptGuard()
        guard.begin_fix("action-004", "target.py")
        assert guard.active_fixes["action-004"]["before_content"] == ""


class TestInterruptGuardUpdatePhase:
    def test_update_phase_changes_phase(self):
        guard = InterruptGuard()
        guard.begin_fix("action-005", "target.py", "original")
        guard.update_phase("action-005", "fixing")
        assert guard.active_fixes["action-005"]["phase"] == "fixing"

    def test_update_phase_writes_wal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = InterruptGuard(wal_dir=os.path.join(tmpdir, "wal"))
            guard.begin_fix("action-006", "target.py", "original")
            guard.update_phase("action-006", "writing")
            wal_file = Path(tmpdir) / "wal" / "action-006.wal"
            data = json.loads(wal_file.read_text(encoding="utf-8"))
            assert data["phase"] == "writing"

    def test_update_phase_ignores_unknown_action_id(self):
        guard = InterruptGuard()
        guard.update_phase("nonexistent", "fixing")
        assert "nonexistent" not in guard.active_fixes


class TestInterruptGuardCompleteFix:
    def test_complete_fix_removes_from_active(self):
        guard = InterruptGuard()
        guard.begin_fix("action-007", "target.py", "original")
        guard.complete_fix("action-007")
        assert "action-007" not in guard.active_fixes

    def test_complete_fix_removes_wal_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = InterruptGuard(wal_dir=os.path.join(tmpdir, "wal"))
            guard.begin_fix("action-008", "target.py", "original")
            wal_file = Path(tmpdir) / "wal" / "action-008.wal"
            assert wal_file.exists()
            guard.complete_fix("action-008")
            assert not wal_file.exists()

    def test_complete_fix_handles_unknown_action_id(self):
        guard = InterruptGuard()
        guard.complete_fix("nonexistent")


class TestInterruptGuardRecover:
    def test_recover_returns_empty_when_no_wal_dir(self):
        guard = InterruptGuard(wal_dir="/nonexistent/wal/dir")
        result = guard.recover()
        assert result == []

    def test_recover_returns_empty_when_no_wal_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wal_dir = Path(tmpdir) / "wal"
            wal_dir.mkdir()
            guard = InterruptGuard(wal_dir=str(wal_dir))
            result = guard.recover()
            assert result == []

    def test_recover_recovers_interrupted_fix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wal_dir = Path(tmpdir) / "wal"
            wal_dir.mkdir()
            wal_file = wal_dir / "action-009.wal"
            wal_data = {
                "phase": "fixing",
                "target": "",
                "before_content": "",
                "timestamp": "2026-01-01T00:00:00Z",
            }
            wal_file.write_text(json.dumps(wal_data), encoding="utf-8")
            guard = InterruptGuard(wal_dir=str(wal_dir))
            result = guard.recover()
            assert len(result) == 1
            assert result[0]["action_id"] == "action-009"
            assert result[0]["recovery_action"] == "rollback"

    def test_recover_cleans_up_wal_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wal_dir = Path(tmpdir) / "wal"
            wal_dir.mkdir()
            wal_file = wal_dir / "action-010.wal"
            wal_data = {"phase": "started", "target": "", "before_content": ""}
            wal_file.write_text(json.dumps(wal_data), encoding="utf-8")
            guard = InterruptGuard(wal_dir=str(wal_dir))
            guard.recover()
            assert not wal_file.exists()

    def test_recover_handles_corrupt_wal_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wal_dir = Path(tmpdir) / "wal"
            wal_dir.mkdir()
            wal_file = wal_dir / "action-011.wal"
            wal_file.write_text("not valid json{{{", encoding="utf-8")
            guard = InterruptGuard(wal_dir=str(wal_dir))
            result = guard.recover()
            assert isinstance(result, list)


class TestInterruptGuardInstallHandlers:
    def test_install_handlers_sets_flag(self):
        guard = InterruptGuard()
        try:
            guard.install_handlers()
            assert guard.handlers_installed is True
        finally:
            guard.remove_handlers()

    def test_install_handlers_idempotent(self):
        guard = InterruptGuard()
        try:
            guard.install_handlers()
            guard.install_handlers()
            assert guard.handlers_installed is True
        finally:
            guard.remove_handlers()

    def test_remove_handlers_clears_flag(self):
        guard = InterruptGuard()
        try:
            guard.install_handlers()
        finally:
            guard.remove_handlers()
        assert guard.handlers_installed is False

    def test_remove_handlers_when_not_installed(self):
        guard = InterruptGuard()
        guard.remove_handlers()
        assert guard.handlers_installed is False
