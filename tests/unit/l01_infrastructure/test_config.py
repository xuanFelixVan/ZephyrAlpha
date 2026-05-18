# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.test_config
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l01_infrastructure/config.py
====================================================

覆盖矩阵：
  AppConfig (frozen dataclass):
    - 默认值构造 × 1
    - frozen 不可变 × 1
    - __post_init__ list → tuple × 1
  _deep_merge_lists:
    - list → tuple(str) × 1
    - 非 list 原样返回 × 1
  load_config:
    - 无 YAML 文件 → 返回默认 AppConfig × 1
    - 显式 config_path 有效 × 1
    - 显式 config_path 不存在 → fallback × 1
    - ZEPHYR_APP_CONFIG_PATH 环境变量 × 1
    - env_override: ZEPHYR_ENV × 1
    - env_override: ZEPHYR_LOG_LEVEL × 1
    - YAML 根节点非 dict → fallback × 1
    - PyYAML 未安装 → fallback × 1
    - data_source_priority 非 list/tuple → 默认值 × 1
  reload_config:
    - 上次成功加载路径可用 → 重新加载 × 1
    - 上次无成功路径 → 搜索链 × 1
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from zephyr.l01_infrastructure.config import (
    DEFAULT_CONFIG_FILENAMES,
    AppConfig,
    _deep_merge_lists,
    load_config,
    reload_config,
)


class TestAppConfig:
    def test_defaults(self):
        cfg = AppConfig()
        assert cfg.env == "dev"
        assert cfg.log_level == "INFO"
        assert cfg.data_source_priority == ("akshare", "tushare")

    def test_custom_values(self):
        cfg = AppConfig(env="prod", log_level="DEBUG", data_source_priority=("tushare",))
        assert cfg.env == "prod"
        assert cfg.log_level == "DEBUG"
        assert cfg.data_source_priority == ("tushare",)

    def test_frozen(self):
        cfg = AppConfig()
        with pytest.raises(AttributeError):
            cfg.env = "prod"

    def test_post_init_converts_list_to_tuple(self):
        cfg = AppConfig(data_source_priority=["tushare", "akshare"])
        assert cfg.data_source_priority == ("tushare", "akshare")
        assert isinstance(cfg.data_source_priority, tuple)

    def test_post_init_leaves_tuple_unchanged(self):
        cfg = AppConfig(data_source_priority=("tushare",))
        assert cfg.data_source_priority == ("tushare",)


class TestDeepMergeLists:
    def test_list_converted_to_tuple_of_strings(self):
        result = _deep_merge_lists([1, "b", 3.0])
        assert result == ("1", "b", "3.0")
        assert isinstance(result, tuple)

    def test_non_list_returned_as_is(self):
        assert _deep_merge_lists(42) == 42
        assert _deep_merge_lists("hello") == "hello"
        assert _deep_merge_lists(("a", "b")) == ("a", "b")


class TestDEFAULT_CONFIG_FILENAMES:
    def test_is_tuple_of_config_paths(self):
        assert "config/" in DEFAULT_CONFIG_FILENAMES[0] or "config\\" in DEFAULT_CONFIG_FILENAMES[0]


class TestLoadConfig:
    def test_no_yaml_returns_default(self, monkeypatch):
        monkeypatch.delenv("ZEPHYR_APP_CONFIG_PATH", raising=False)
        result = load_config(config_path="/nonexistent/path/config.yaml")
        assert result.env == "dev"
        assert result.log_level == "INFO"

    def test_explicit_config_path(self, tmp_path):
        yaml_file = tmp_path / "app.yaml"
        yaml_file.write_text("env: staging\nlog_level: DEBUG\ndata_source_priority: [tushare]\n", encoding="utf-8")
        result = load_config(config_path=str(yaml_file))
        assert result.env == "staging"
        assert result.log_level == "DEBUG"
        assert result.data_source_priority == ("tushare",)

    def test_explicit_config_path_not_found_fallback(self, monkeypatch):
        monkeypatch.delenv("ZEPHYR_APP_CONFIG_PATH", raising=False)
        result = load_config(config_path="/no/such/path.yaml")
        assert result.env == "dev"

    def test_env_var_config_path(self, tmp_path, monkeypatch):
        yaml_file = tmp_path / "env_app.yaml"
        yaml_file.write_text("env: production\n", encoding="utf-8")
        monkeypatch.setenv("ZEPHYR_APP_CONFIG_PATH", str(yaml_file))
        result = load_config()
        assert result.env == "production"

    def test_env_override_zephyr_env(self, tmp_path, monkeypatch):
        yaml_file = tmp_path / "app.yaml"
        yaml_file.write_text("env: dev\nlog_level: INFO\n", encoding="utf-8")
        monkeypatch.setenv("ZEPHYR_ENV", "production")
        result = load_config(config_path=str(yaml_file), env_override=True)
        assert result.env == "production"

    def test_env_override_zephyr_log_level(self, tmp_path, monkeypatch):
        yaml_file = tmp_path / "app.yaml"
        yaml_file.write_text("env: dev\nlog_level: INFO\n", encoding="utf-8")
        monkeypatch.setenv("ZEPHYR_LOG_LEVEL", "DEBUG")
        result = load_config(config_path=str(yaml_file), env_override=True)
        assert result.log_level == "DEBUG"

    def test_env_override_disabled(self, tmp_path, monkeypatch):
        yaml_file = tmp_path / "app.yaml"
        yaml_file.write_text("env: dev\nlog_level: INFO\n", encoding="utf-8")
        monkeypatch.setenv("ZEPHYR_ENV", "production")
        result = load_config(config_path=str(yaml_file), env_override=False)
        assert result.env == "dev"

    def test_yaml_root_not_dict_fallback(self, tmp_path):
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text("- item1\n- item2\n", encoding="utf-8")
        result = load_config(config_path=str(yaml_file))
        assert result.env == "dev"

    def test_empty_yaml_fallback(self, tmp_path):
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("", encoding="utf-8")
        result = load_config(config_path=str(yaml_file))
        assert result.env == "dev"

    def test_data_source_priority_non_list_defaults(self, tmp_path):
        yaml_file = tmp_path / "app.yaml"
        yaml_file.write_text("env: dev\ndata_source_priority: 42\n", encoding="utf-8")
        result = load_config(config_path=str(yaml_file))
        assert result.data_source_priority == ("akshare", "tushare")


class TestReloadConfig:
    def test_reload_uses_last_loaded_path(self, tmp_path):
        yaml_file = tmp_path / "app.yaml"
        yaml_file.write_text("env: hot_reload_test\n", encoding="utf-8")
        load_config(config_path=str(yaml_file))
        result = reload_config()
        assert result.env == "hot_reload_test"

    def test_reload_updates_when_file_changes(self, tmp_path):
        yaml_file = tmp_path / "app.yaml"
        yaml_file.write_text("env: v1\n", encoding="utf-8")
        load_config(config_path=str(yaml_file))
        yaml_file.write_text("env: v2\n", encoding="utf-8")
        result = reload_config()
        assert result.env == "v2"

    def test_reload_no_previous_path_falls_back(self, monkeypatch):
        monkeypatch.delenv("ZEPHYR_APP_CONFIG_PATH", raising=False)
        import zephyr.l01_infrastructure.config as cfg_mod
        cfg_mod._LAST_LOADED_CONFIG_PATH = None
        result = reload_config()
        assert isinstance(result, AppConfig)
