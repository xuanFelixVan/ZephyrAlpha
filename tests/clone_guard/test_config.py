# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §6
# [MODULE] tests.clone_guard.test_config
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_config.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""CloneGuard 配置加载器单元测试。"""

from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig, load_config


class TestCloneGuardConfigDefaults:
    """CloneGuardConfig 安全默认值测试。"""

    def test_default_pre_commit_timeout(self):
        cfg = CloneGuardConfig()
        assert cfg.pre_commit_timeout_sec == 30

    def test_default_fail_on_severity_extract(self):
        cfg = CloneGuardConfig()
        assert cfg.fail_on_severity == "extract"

    def test_default_echo_guard_enabled(self):
        cfg = CloneGuardConfig()
        assert cfg.echo_guard_enabled is True

    def test_default_fail_closed_false(self):
        """fail_closed 默认 False——降级时 warn-only 不阻断（守 blueprint §5.2）。"""
        cfg = CloneGuardConfig()
        assert cfg.fail_closed is False

    def test_block_severities_extract(self):
        """fail_on=extract 时 block_severities 仅含 extract。"""
        cfg = CloneGuardConfig(fail_on_severity="extract")
        assert cfg.block_severities == {"extract"}

    def test_block_severities_review(self):
        """fail_on=review 时 block_severities 含 extract + review。"""
        cfg = CloneGuardConfig(fail_on_severity="review")
        assert cfg.block_severities == {"extract", "review"}

    def test_block_severities_none(self):
        """fail_on=none 时 block_severities 为空集（不阻断）。"""
        cfg = CloneGuardConfig(fail_on_severity="none")
        assert cfg.block_severities == set()

    def test_default_ignore_paths_includes_tests(self):
        cfg = CloneGuardConfig()
        assert "tests/" in cfg.ignore_paths
        assert "docs/" in cfg.ignore_paths


class TestLoadConfig:
    """load_config 从 YAML 加载测试。"""

    def test_missing_file_returns_defaults(self, tmp_path: Path):
        """clone_guard.yml 不存在时返回安全默认值。"""
        cfg = load_config(tmp_path)
        assert cfg.pre_commit_timeout_sec == 30
        assert cfg.fail_on_severity == "extract"
        assert cfg.echo_guard_enabled is True

    def test_valid_yaml_loaded(self, tmp_path: Path):
        """合法 YAML 正确加载。"""
        (tmp_path / "clone_guard.yml").write_text(
            "version: 1\n"
            "pre_commit:\n"
            "  timeout_sec: 60\n"
            "  fail_on: review\n"
            "  echo_guard_enabled: false\n"
            "  fail_closed: true\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.pre_commit_timeout_sec == 60
        assert cfg.fail_on_severity == "review"
        assert cfg.echo_guard_enabled is False
        assert cfg.fail_closed is True

    def test_malformed_yaml_returns_defaults(self, tmp_path: Path):
        """YAML 解析失败时返回安全默认值（不抛异常）。"""
        (tmp_path / "clone_guard.yml").write_text(
            "[: not valid yaml :]\n}}}\n", encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.pre_commit_timeout_sec == 30
        assert cfg.fail_on_severity == "extract"

    def test_non_dict_top_level_returns_defaults(self, tmp_path: Path):
        """YAML 顶层非 dict 时返回安全默认值。"""
        (tmp_path / "clone_guard.yml").write_text("- just\n- a\n- list\n", encoding="utf-8")
        cfg = load_config(tmp_path)
        assert cfg.pre_commit_timeout_sec == 30

    def test_partial_config_uses_defaults_for_missing_keys(self, tmp_path: Path):
        """部分配置缺失时缺失字段使用默认值。"""
        (tmp_path / "clone_guard.yml").write_text(
            "pre_commit:\n  timeout_sec: 45\n", encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.pre_commit_timeout_sec == 45
        assert cfg.fail_on_severity == "extract"  # 默认
        assert cfg.echo_guard_enabled is True     # 默认
