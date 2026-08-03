# [A_test] module_id: MOD-GOV_env_watcher | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §

# [MODULE] tests.test_env_watcher
# [DOMAIN] D_GOVERNANCE

# [INVARIANTS] EnvWatcher detects .env changes and produces EnvChangeAlert

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest raises on failure

# [TESTS] this file
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.rollback.env_watcher import EnvChangeAlert, EnvWatcher


class TestEnvWatcherInit:
    def test_default_project_root(self, tmp_path: Path):
        watcher = EnvWatcher(project_root=tmp_path)
        assert watcher.project_root == tmp_path
        assert watcher.sentinel_path == tmp_path / EnvWatcher.SENTINEL_FILE

    def test_sentinel_parent_created(self, tmp_path: Path):
        watcher = EnvWatcher(project_root=tmp_path)
        assert watcher.sentinel_path.parent.exists()

    def test_none_project_root_uses_cwd(self):
        watcher = EnvWatcher(project_root=None)
        assert watcher.project_root == Path.cwd()


class TestEnvWatcherCheckForChanges:
    def test_no_env_file_returns_none(self, tmp_path: Path):
        watcher = EnvWatcher(project_root=tmp_path)
        result = watcher.check_for_changes()
        assert result is None

    def test_detects_new_env_file(self, tmp_path: Path):
        env_path = tmp_path / ".env"
        env_path.write_text("KEY1=value1\nKEY2=value2\n", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        result = watcher.check_for_changes()
        assert isinstance(result, EnvChangeAlert)
        assert "KEY1" in result.changed_keys
        assert "KEY2" in result.changed_keys
        assert result.agent_action == "RELOAD_ENV_FROM_SENTINEL"

    def test_no_change_returns_none(self, tmp_path: Path):
        env_path = tmp_path / ".env"
        env_path.write_text("KEY1=value1\n", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        watcher.check_for_changes()
        result = watcher.check_for_changes()
        assert result is None

    def test_detects_modified_key(self, tmp_path: Path):
        env_path = tmp_path / ".env"
        env_path.write_text("KEY1=old_value\n", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        watcher.check_for_changes()
        env_path.write_text("KEY1=new_value\n", encoding="utf-8")
        result = watcher.check_for_changes()
        assert result is not None
        assert "KEY1" in result.changed_keys

    def test_detects_new_key_added(self, tmp_path: Path):
        env_path = tmp_path / ".env"
        env_path.write_text("KEY1=value1\n", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        watcher.check_for_changes()
        env_path.write_text("KEY1=value1\nKEY2=value2\n", encoding="utf-8")
        result = watcher.check_for_changes()
        assert result is not None
        assert "KEY2" in result.changed_keys

    def test_ignores_comments_and_empty_lines(self, tmp_path: Path):
        env_path = tmp_path / ".env"
        env_path.write_text("# comment\n\nKEY1=val1\n", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        result = watcher.check_for_changes()
        assert result is not None
        assert result.changed_keys == ["KEY1"]


class TestEnvWatcherNotifyAgent:
    def test_no_changes_no_reload(self, tmp_path: Path):
        watcher = EnvWatcher(project_root=tmp_path)
        result = watcher.notify_agent_reload_required()
        assert result["reload_required"] is False

    def test_changes_require_reload(self, tmp_path: Path):
        env_path = tmp_path / ".env"
        env_path.write_text("DB_HOST=localhost\n", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        result = watcher.notify_agent_reload_required()
        assert result["reload_required"] is True
        assert "DB_HOST" in result["changed_keys"]
        assert "sentinel_path" in result


class TestEnvWatcherBoundary:
    def test_env_file_with_equals_in_value(self, tmp_path: Path):
        env_path = tmp_path / ".env"
        env_path.write_text("CONN_STR=host=db port=5432\n", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        result = watcher.check_for_changes()
        assert result is not None
        assert "CONN_STR" in result.changed_keys

    def test_corrupted_sentinel_json(self, tmp_path: Path):
        env_path = tmp_path / ".env"
        env_path.write_text("KEY1=val1\n", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        watcher.sentinel_path.write_text("{invalid json", encoding="utf-8")
        result = watcher.check_for_changes()
        assert result is not None
        assert "KEY1" in result.changed_keys

    def test_empty_env_file(self, tmp_path: Path):
        env_path = tmp_path / ".env"
        env_path.write_text("", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        result = watcher.check_for_changes()
        assert result is None

    def test_env_local_also_read(self, tmp_path: Path):
        env_local = tmp_path / ".env.local"
        env_local.write_text("LOCAL_KEY=local_val\n", encoding="utf-8")
        watcher = EnvWatcher(project_root=tmp_path)
        result = watcher.check_for_changes()
        assert result is not None
        assert "LOCAL_KEY" in result.changed_keys
