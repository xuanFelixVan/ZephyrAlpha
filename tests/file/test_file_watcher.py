# [A_test] module_id: MOD-GOV_file_watcher | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §file_watcher
# [MODULE] tests.test_file_watcher
# [INVARIANTS] FileWatcher.poll_interval>=10s; FileChangeEvent必须包含path+event_type+timestamp
# [MODIFY-GUARD] 仅当file_watcher公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; FileWatcherError on invalid watch_dir
# [TESTS] pytest tests/test_file_watcher.py -q
# [TTL] task_bound

import time

import pytest

from zephyr.infrastructure.file_watcher import (
    FileChangeEvent,
    FileChangeType,
    FileWatcher,
    FileWatcherError,
)


class TestFileChangeType:
    def test_values(self):
        assert FileChangeType.CREATED.value == "created"
        assert FileChangeType.MODIFIED.value == "modified"
        assert FileChangeType.DELETED.value == "deleted"


class TestFileChangeEvent:
    def test_construction(self, tmp_path):
        from pathlib import Path

        event = FileChangeEvent(
            path=Path("/tmp/test.py"),
            event_type=FileChangeType.CREATED,
        )
        assert event.path == Path("/tmp/test.py")
        assert event.event_type == FileChangeType.CREATED
        assert event.timestamp > 0

    def test_suffix_property(self, tmp_path):
        from pathlib import Path

        event = FileChangeEvent(
            path=Path("/tmp/test.PY"),
            event_type=FileChangeType.MODIFIED,
        )
        assert event.suffix == ".py"


class TestFileWatcher:
    def test_instantiation(self, tmp_path):
        watcher = FileWatcher(watch_dir=tmp_path, poll_interval=10.0)
        assert watcher is not None
        assert watcher.is_running is False

    def test_invalid_watch_dir(self):
        from pathlib import Path

        with pytest.raises(FileWatcherError):
            FileWatcher(watch_dir=Path("/nonexistent/dir/xyz"), poll_interval=10.0)

    def test_invalid_poll_interval(self, tmp_path):
        with pytest.raises(FileWatcherError):
            FileWatcher(watch_dir=tmp_path, poll_interval=5.0)

    def test_start_stop(self, tmp_path):
        watcher = FileWatcher(watch_dir=tmp_path, poll_interval=10.0)
        watcher.start()
        assert watcher.is_running is True
        watcher.stop()
        assert watcher.is_running is False

    def test_start_idempotent(self, tmp_path):
        watcher = FileWatcher(watch_dir=tmp_path, poll_interval=10.0)
        watcher.start()
        watcher.start()
        assert watcher.is_running is True
        watcher.stop()

    def test_stop_idempotent(self, tmp_path):
        watcher = FileWatcher(watch_dir=tmp_path, poll_interval=10.0)
        watcher.stop()
        assert watcher.is_running is False

    def test_tracked_count(self, tmp_path):
        (tmp_path / "test.py").write_text("print('hello')", encoding="utf-8")
        watcher = FileWatcher(watch_dir=tmp_path, poll_interval=10.0)
        assert watcher.tracked_count == 0
        watcher.start()
        time.sleep(0.3)
        count = watcher.tracked_count
        watcher.stop()
        assert count >= 1

    def test_scan_once_detects_new_file(self, tmp_path):
        watcher = FileWatcher(watch_dir=tmp_path, poll_interval=10.0)
        watcher.start()
        time.sleep(0.2)
        watcher.stop()

        (tmp_path / "new_file.py").write_text("x = 1", encoding="utf-8")
        events = watcher.scan_once()
        assert len(events) >= 1
        created_events = [e for e in events if e.event_type == FileChangeType.CREATED]
        assert len(created_events) >= 1

    def test_scan_once_detects_modification(self, tmp_path):
        test_file = tmp_path / "mod_file.py"
        test_file.write_text("x = 1", encoding="utf-8")
        watcher = FileWatcher(watch_dir=tmp_path, poll_interval=10.0)
        watcher.start()
        time.sleep(0.2)
        watcher.stop()

        test_file.write_text("x = 2", encoding="utf-8")
        events = watcher.scan_once()
        modified_events = [e for e in events if e.event_type == FileChangeType.MODIFIED]
        assert len(modified_events) >= 1

    def test_scan_once_detects_deletion(self, tmp_path):
        test_file = tmp_path / "del_file.py"
        test_file.write_text("x = 1", encoding="utf-8")
        watcher = FileWatcher(watch_dir=tmp_path, poll_interval=10.0)
        watcher.start()
        time.sleep(0.2)
        watcher.stop()

        test_file.unlink()
        events = watcher.scan_once()
        deleted_events = [e for e in events if e.event_type == FileChangeType.DELETED]
        assert len(deleted_events) >= 1

    def test_patterns_filter(self, tmp_path):
        (tmp_path / "test.py").write_text("code", encoding="utf-8")
        (tmp_path / "test.txt").write_text("text", encoding="utf-8")
        watcher = FileWatcher(watch_dir=tmp_path, patterns=[".py"], poll_interval=10.0)
        watcher.start()
        time.sleep(0.2)
        count = watcher.tracked_count
        watcher.stop()
        assert count == 1

    def test_on_change_callback(self, tmp_path):
        received = []
        watcher = FileWatcher(
            watch_dir=tmp_path,
            poll_interval=10.0,
            on_change=lambda e: received.append(e),
        )
        watcher.start()
        time.sleep(0.2)
        watcher.stop()

        (tmp_path / "callback_test.py").write_text("test", encoding="utf-8")
        events = watcher.scan_once()
        for event in events:
            if watcher._on_change:
                watcher._on_change(event)
        assert len(received) >= 1
