# [A_test] module_id: SRC-TST-0570 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_config_manager
# [INVARIANTS] ConfigManager.load returns dict; get_system_config returns dict for any key
# [MODIFY-GUARD] src/zephyr/orchestrator/config_manager.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] load/validate_on_startup never raise
# [TESTS] tests/test_config_manager.py

from __future__ import annotations

from zephyr.trading.orchestrator.config_manager import ConfigManager


class TestConfigManagerInstantiation:
    def test_default_config_path(self):
        cm = ConfigManager()
        assert cm._config_path == "config/system_config.yaml"

    def test_custom_config_path(self):
        cm = ConfigManager(config_path="custom/path.yaml")
        assert cm._config_path == "custom/path.yaml"

    def test_empty_config_on_init(self):
        cm = ConfigManager()
        assert cm._config == {}


class TestLoad:
    def test_load_returns_dict(self):
        cm = ConfigManager()
        result = cm.load()
        assert isinstance(result, dict)

    def test_load_empty_config(self):
        cm = ConfigManager()
        assert cm.load() == {}


class TestValidateOnStartup:
    def test_validate_returns_bool(self):
        cm = ConfigManager()
        result = cm.validate_on_startup()
        assert isinstance(result, bool)

    def test_validate_default_true(self):
        cm = ConfigManager()
        assert cm.validate_on_startup() is True


class TestGetSystemConfig:
    def test_missing_system_returns_empty_dict(self):
        cm = ConfigManager()
        result = cm.get_system_config("nonexistent")
        assert result == {}

    def test_empty_string_system_returns_empty_dict(self):
        cm = ConfigManager()
        result = cm.get_system_config("")
        assert result == {}


class TestBoundary:
    def test_load_is_idempotent(self):
        cm = ConfigManager()
        first = cm.load()
        second = cm.load()
        assert first == second

    def test_get_system_config_returns_empty_for_none_like_key(self):
        cm = ConfigManager()
        result = cm.get_system_config("None")
        assert isinstance(result, dict)
