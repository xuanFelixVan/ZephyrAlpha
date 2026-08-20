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
            "[: not valid yaml :]\n}}}\n",
            encoding="utf-8",
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
            "pre_commit:\n  timeout_sec: 45\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.pre_commit_timeout_sec == 45
        assert cfg.fail_on_severity == "extract"  # 默认
        assert cfg.echo_guard_enabled is True  # 默认


class TestEnvConfig:
    """env 字段测试——#ARCH-FORCE-MERGE-DEDUP-001 Phase A 闭合（HF_HUB_OFFLINE 离线优先）。"""

    def test_default_env_is_empty_dict(self):
        """默认 env 为空 dict。"""
        cfg = CloneGuardConfig()
        assert cfg.env == {}

    def test_env_loaded_from_yaml(self, tmp_path: Path):
        """env 段从 YAML 正确加载。"""
        (tmp_path / "clone_guard.yml").write_text(
            'env:\n  HF_HUB_OFFLINE: "1"\n  TRANSFORMERS_OFFLINE: "1"\n',
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.env == {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}

    def test_env_values_stringified(self, tmp_path: Path):
        """env 值被转为 string（即使 YAML 写成数字）。"""
        (tmp_path / "clone_guard.yml").write_text(
            "env:\n  HF_HUB_OFFLINE: 1\n",  # int, not string
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.env == {"HF_HUB_OFFLINE": "1"}
        assert isinstance(cfg.env["HF_HUB_OFFLINE"], str)

    def test_env_missing_returns_empty(self, tmp_path: Path):
        """无 env 段时返回空 dict。"""
        (tmp_path / "clone_guard.yml").write_text(
            "version: 1\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.env == {}

    def test_env_non_dict_returns_empty(self, tmp_path: Path):
        """env 段非 dict 时返回空 dict（安全降级）。"""
        (tmp_path / "clone_guard.yml").write_text(
            'env: ["not", "a", "dict"]\n',
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.env == {}

    def test_malformed_yaml_env_returns_empty(self, tmp_path: Path):
        """YAML 解析失败时 env 为空 dict（安全降级）。"""
        (tmp_path / "clone_guard.yml").write_text(
            "[: not valid :]\n}}}\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.env == {}


class TestPhaseBConfigFields:
    """Phase B 补齐字段默认值测试（ast-grep 显式 + reDUP）。"""

    def test_default_ast_grep_enabled(self):
        cfg = CloneGuardConfig()
        assert cfg.ast_grep_enabled is True

    def test_default_redup_enabled(self):
        """reDUP 默认启用（L1 第3引擎）。"""
        cfg = CloneGuardConfig()
        assert cfg.redup_enabled is True

    def test_default_redup_min_sim(self):
        cfg = CloneGuardConfig()
        assert cfg.redup_min_sim == 0.85

    def test_default_redup_mode_changed_only(self):
        """reDUP 默认 L1 changed-only 增量模式。"""
        cfg = CloneGuardConfig()
        assert cfg.redup_mode == "changed-only"

    def test_default_redup_max_groups_unlimited(self):
        """redup_max_groups 默认 0（不限组数）。"""
        cfg = CloneGuardConfig()
        assert cfg.redup_max_groups == 0


class TestPhaseCConfigFields:
    """Phase C 字段默认值测试（mcrit/vendetect/relate + audit/compare 超时）。"""

    def test_default_mcrit_disabled(self):
        """mcrit 默认禁用（L2 审计才启用）。"""
        cfg = CloneGuardConfig()
        assert cfg.mcrit_enabled is False

    def test_default_mcrit_index_path(self):
        cfg = CloneGuardConfig()
        assert cfg.mcrit_index_path == ".mcrit/index.db"

    def test_default_vendetect_disabled(self):
        cfg = CloneGuardConfig()
        assert cfg.vendetect_enabled is False

    def test_default_vendetect_remote_url_none(self):
        cfg = CloneGuardConfig()
        assert cfg.vendetect_remote_url is None

    def test_default_relate_disabled(self):
        cfg = CloneGuardConfig()
        assert cfg.relate_enabled is False

    def test_default_relate_index_path(self):
        cfg = CloneGuardConfig()
        assert cfg.relate_index_path == ".relate/index"

    def test_default_audit_timeout(self):
        cfg = CloneGuardConfig()
        assert cfg.audit_timeout_sec == 300

    def test_default_compare_timeout(self):
        cfg = CloneGuardConfig()
        assert cfg.compare_timeout_sec == 600

    def test_default_filter_minority_false(self):
        """filter_minority 默认 False——保留少数派但标记 consensus。"""
        cfg = CloneGuardConfig()
        assert cfg.filter_minority is False


class TestNestedEngineConfig:
    """嵌套引擎配置加载测试（蓝图 §6.1 pre_commit.engines.* / audit.engines.* / compare.*）。"""

    def test_pre_commit_engines_redup_loaded(self, tmp_path: Path):
        """pre_commit.engines.redup 嵌套配置正确加载。"""
        (tmp_path / "clone_guard.yml").write_text(
            "pre_commit:\n"
            "  engines:\n"
            "    redup:\n"
            "      enabled: false\n"
            "      min_sim: 0.9\n"
            "      mode: semantic\n"
            "      max_groups: 10\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.redup_enabled is False
        assert cfg.redup_min_sim == 0.9
        assert cfg.redup_mode == "semantic"
        assert cfg.redup_max_groups == 10

    def test_pre_commit_engines_ast_grep_loaded(self, tmp_path: Path):
        """pre_commit.engines.ast_grep 嵌套配置正确加载。"""
        (tmp_path / "clone_guard.yml").write_text(
            "pre_commit:\n  engines:\n    ast_grep:\n      enabled: false\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.ast_grep_enabled is False

    def test_pre_commit_engines_echo_guard_loaded(self, tmp_path: Path):
        """pre_commit.engines.echo_guard 嵌套配置正确加载。"""
        (tmp_path / "clone_guard.yml").write_text(
            "pre_commit:\n  engines:\n    echo_guard:\n      enabled: false\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.echo_guard_enabled is False

    def test_audit_engines_mcrit_loaded(self, tmp_path: Path):
        """audit.engines.mcrit 嵌套配置正确加载。"""
        (tmp_path / "clone_guard.yml").write_text(
            "audit:\n"
            "  timeout_sec: 600\n"
            "  engines:\n"
            "    mcrit:\n"
            "      enabled: true\n"
            "      index_path: /custom/mcrit.db\n"
            "      query_threshold: 0.8\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.mcrit_enabled is True
        assert cfg.mcrit_index_path == "/custom/mcrit.db"
        assert cfg.mcrit_query_threshold == 0.8
        assert cfg.audit_timeout_sec == 600

    def test_compare_vendetect_relate_loaded(self, tmp_path: Path):
        """compare 段 vendetect/relate 配置正确加载。"""
        (tmp_path / "clone_guard.yml").write_text(
            "compare:\n"
            "  timeout_sec: 900\n"
            "  vendetect_cross_repo: true\n"
            "  vendetect_remote_url: https://github.com/x/y\n"
            "  relate_prescreen: true\n"
            "  relate_index_path: /custom/relate\n"
            "  relate_top_k: 20\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.vendetect_enabled is True
        assert cfg.vendetect_remote_url == "https://github.com/x/y"
        assert cfg.relate_enabled is True
        assert cfg.relate_index_path == "/custom/relate"
        assert cfg.relate_top_k == 20
        assert cfg.compare_timeout_sec == 900

    def test_nested_config_backward_compatible(self, tmp_path: Path):
        """旧式扁平配置（无 engines 嵌套）仍向后兼容。"""
        (tmp_path / "clone_guard.yml").write_text(
            "pre_commit:\n  timeout_sec: 45\n  echo_guard_enabled: false\n  fail_closed: true\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.pre_commit_timeout_sec == 45
        assert cfg.echo_guard_enabled is False
        assert cfg.fail_closed is True
        # 新字段用默认值
        assert cfg.redup_enabled is True
        assert cfg.ast_grep_enabled is True

    def test_aggregation_filter_minority_loaded(self, tmp_path: Path):
        """aggregation.filter_minority 配置正确加载。"""
        (tmp_path / "clone_guard.yml").write_text(
            "aggregation:\n  filter_minority: true\n",
            encoding="utf-8",
        )
        cfg = load_config(tmp_path)
        assert cfg.filter_minority is True
