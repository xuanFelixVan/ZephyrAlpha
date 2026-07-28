# [A_test] module_id: MOD-GOV_ide_watcher | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_ide_watcher
# [INVARIANTS] scan must return dict with changes_detected and files keys
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OSError on inaccessible skills_dir
# [TESTS] tests/test_ide_watcher.py
# [TTL] task_bound

import os
import time
from pathlib import Path
from unittest.mock import MagicMock

from zephyr.autonomy_core.ide_watcher import IDEWatcher
from zephyr.shared.io.paths import REPO_ROOT


class TestIDEWatcherInit:
    def test_default_skills_dir(self):
        watcher = IDEWatcher()
        expected = REPO_ROOT / "src" / "zephyr" / "agent-spec" / "skills"
        assert watcher.skills_dir == expected or isinstance(watcher.skills_dir, Path)

    def test_custom_skills_dir(self, tmp_path):
        watcher = IDEWatcher(skills_dir=tmp_path)
        assert watcher.skills_dir == tmp_path

    def test_none_skills_dir_resolves_default(self):
        watcher = IDEWatcher(skills_dir=None)
        assert watcher.skills_dir is not None
        assert isinstance(watcher.skills_dir, Path)

    def test_initial_mtimes_empty(self, tmp_path):
        watcher = IDEWatcher(skills_dir=tmp_path)
        assert watcher.last_mtimes == {}

    def test_initial_callbacks_empty(self, tmp_path):
        watcher = IDEWatcher(skills_dir=tmp_path)
        assert watcher.callbacks == []


class TestIDEWatcherScan:
    def test_scan_empty_dir(self, tmp_path):
        watcher = IDEWatcher(skills_dir=tmp_path)
        result = watcher.scan()
        assert result["changes_detected"] == 0
        assert result["files"] == []

    def test_scan_new_file_no_change(self, tmp_path):
        (tmp_path / "skill.md").write_text("hello", encoding="utf-8")
        watcher = IDEWatcher(skills_dir=tmp_path)
        result = watcher.scan()
        assert result["changes_detected"] == 0

    def test_scan_detects_modified_file(self, tmp_path):
        f = tmp_path / "skill.md"
        f.write_text("v1", encoding="utf-8")
        watcher = IDEWatcher(skills_dir=tmp_path)
        watcher.scan()
        time.sleep(0.05)
        f.write_text("v2", encoding="utf-8")
        os.utime(str(f), (time.time() + 1, time.time() + 1))
        result = watcher.scan()
        assert result["changes_detected"] >= 1
        assert str(f) in result["files"]

    def test_scan_ignores_non_tracked_extensions(self, tmp_path):
        (tmp_path / "code.py").write_text("print('hi')", encoding="utf-8")
        watcher = IDEWatcher(skills_dir=tmp_path)
        result = watcher.scan()
        assert result["changes_detected"] == 0

    def test_scan_tracks_yaml_files(self, tmp_path):
        (tmp_path / "config.yaml").write_text("key: val", encoding="utf-8")
        watcher = IDEWatcher(skills_dir=tmp_path)
        watcher.scan()
        time.sleep(0.05)
        f = tmp_path / "config.yaml"
        f.write_text("key: val2", encoding="utf-8")
        os.utime(str(f), (time.time() + 1, time.time() + 1))
        result = watcher.scan()
        assert result["changes_detected"] >= 1

    def test_scan_tracks_yml_files(self, tmp_path):
        (tmp_path / "config.yml").write_text("x: 1", encoding="utf-8")
        watcher = IDEWatcher(skills_dir=tmp_path)
        watcher.scan()
        time.sleep(0.05)
        f = tmp_path / "config.yml"
        f.write_text("x: 2", encoding="utf-8")
        os.utime(str(f), (time.time() + 1, time.time() + 1))
        result = watcher.scan()
        assert result["changes_detected"] >= 1

    def test_scan_subdirectory(self, tmp_path):
        sub = tmp_path / "domain"
        sub.mkdir()
        (sub / "skill.md").write_text("content", encoding="utf-8")
        watcher = IDEWatcher(skills_dir=tmp_path)
        watcher.scan()
        time.sleep(0.05)
        f = sub / "skill.md"
        f.write_text("updated", encoding="utf-8")
        os.utime(str(f), (time.time() + 1, time.time() + 1))
        result = watcher.scan()
        assert result["changes_detected"] >= 1


class TestIDEWatcherOnChange:
    def test_on_change_callback_registered(self, tmp_path):
        watcher = IDEWatcher(skills_dir=tmp_path)
        cb = MagicMock()
        watcher.on_change(cb)
        assert cb in watcher.callbacks

    def test_on_change_callback_fired_on_change(self, tmp_path):
        f = tmp_path / "skill.md"
        f.write_text("v1", encoding="utf-8")
        watcher = IDEWatcher(skills_dir=tmp_path)
        watcher.scan()
        cb = MagicMock()
        watcher.on_change(cb)
        time.sleep(0.05)
        f.write_text("v2", encoding="utf-8")
        os.utime(str(f), (time.time() + 1, time.time() + 1))
        watcher.scan()
        cb.assert_called_once()

    def test_on_change_multiple_callbacks(self, tmp_path):
        f = tmp_path / "skill.md"
        f.write_text("v1", encoding="utf-8")
        watcher = IDEWatcher(skills_dir=tmp_path)
        watcher.scan()
        cb1 = MagicMock()
        cb2 = MagicMock()
        watcher.on_change(cb1)
        watcher.on_change(cb2)
        time.sleep(0.05)
        f.write_text("v2", encoding="utf-8")
        os.utime(str(f), (time.time() + 1, time.time() + 1))
        watcher.scan()
        cb1.assert_called_once()
        cb2.assert_called_once()

    def test_no_callback_when_no_changes(self, tmp_path):
        watcher = IDEWatcher(skills_dir=tmp_path)
        cb = MagicMock()
        watcher.on_change(cb)
        watcher.scan()
        cb.assert_not_called()


class TestIDEWatcherBoundary:
    def test_scan_nonexistent_dir(self, tmp_path):
        missing = tmp_path / "no_such_dir"
        watcher = IDEWatcher(skills_dir=missing)
        result = watcher.scan()
        assert result["changes_detected"] == 0
        assert result["files"] == []

    def test_scan_dir_with_no_relevant_files(self, tmp_path):
        (tmp_path / "readme.txt").write_text("hi", encoding="utf-8")
        (tmp_path / "main.py").write_text("pass", encoding="utf-8")
        watcher = IDEWatcher(skills_dir=tmp_path)
        result = watcher.scan()
        assert result["changes_detected"] == 0
