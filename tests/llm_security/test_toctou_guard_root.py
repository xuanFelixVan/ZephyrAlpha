# [A_test] module_id: SRC-TST-1746 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.toctou_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound
import sys

sys.path.insert(0, "src")

import os
import tempfile
import time

import pytest

try:
    from zephyr.security.access_control.guards.toctou_guard import FileIntegrityCheck, TOCTOUGuard
except Exception as _exc:
    pytest.skip(f"Cannot import toctou_guard: {_exc}", allow_module_level=True)


class TestFileIntegrityCheck:
    def test_creation(self):
        fic = FileIntegrityCheck(path="/tmp/a.py", checksum="abc", size=10, mtime=1.0)
        assert fic.path == "/tmp/a.py"
        assert fic.checksum == "abc"
        assert fic.size == 10
        assert fic.mtime == 1.0

    def test_checked_at_auto(self):
        fic = FileIntegrityCheck(path="/tmp/a.py", checksum="abc", size=10, mtime=1.0)
        assert fic.checked_at > 0


class TestTOCTOUGuard:
    def test_snapshot_real_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(b"test content")
            path = f.name
        try:
            guard = TOCTOUGuard()
            check = guard.snapshot(path)
            assert check.path == path
            assert check.checksum != "GONE"
            assert check.size > 0
        finally:
            os.unlink(path)

    def test_snapshot_nonexistent_file(self):
        guard = TOCTOUGuard()
        check = guard.snapshot("/nonexistent/file.py")
        assert check.checksum == "GONE"
        assert check.size == 0

    def test_verify_unchanged_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(b"unchanged")
            path = f.name
        try:
            guard = TOCTOUGuard()
            guard.snapshot(path)
            ok, msg = guard.verify(path)
            assert ok is True
            assert msg == "OK"
        finally:
            os.unlink(path)

    def test_verify_no_snapshot(self):
        guard = TOCTOUGuard()
        ok, msg = guard.verify("/tmp/never_snapshotted.py")
        assert ok is False
        assert "No pre-state snapshot" in msg

    def test_verify_changed_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(b"original")
            path = f.name
        try:
            guard = TOCTOUGuard()
            guard.snapshot(path)
            with open(path, "w", encoding="utf-8") as f2:
                f2.write("modified content")
            ok, msg = guard.verify(path)
            assert ok is False
            assert "TOCTOU detected" in msg
        finally:
            os.unlink(path)

    def test_verify_deleted_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(b"will be deleted")
            path = f.name
        guard = TOCTOUGuard()
        guard.snapshot(path)
        os.unlink(path)
        ok, msg = guard.verify(path)
        assert ok is False
        assert "disappeared" in msg

    def test_verify_window_expired(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(b"content")
            path = f.name
        try:
            guard = TOCTOUGuard(max_window_seconds=0.0)
            guard.snapshot(path)
            time.sleep(0.1)
            ok, msg = guard.verify(path)
            assert ok is False
            assert "expired" in msg
        finally:
            os.unlink(path)

    def test_clear(self):
        guard = TOCTOUGuard()
        guard._pre_state["/tmp/a.py"] = FileIntegrityCheck(path="/tmp/a.py", checksum="x", size=1, mtime=1.0)
        guard.clear()
        assert len(guard._pre_state) == 0
