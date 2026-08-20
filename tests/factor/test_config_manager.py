# [A_test] module_id: MOD-GOV_config_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_config_manager
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_config_manager.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D_FACTOR core config_manager 测试——loader.py。

覆盖：
- load_core_config: 默认配置加载 / 文件存在性
- get_section: 取已有子节 / 取不存在的子节返回 {} / 取非 dict 子节返回 {}
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

loader = pytest.importorskip("zephyr.factor.core.config_manager.loader")

load_core_config = loader.load_core_config
get_section = loader.get_section


class TestLoadCoreConfig:
    def test_loads_default_config(self) -> None:
        """默认 _config.yaml 应能加载并包含所有 5 个子节。"""
        config = load_core_config()
        assert isinstance(config, dict)
        expected_sections = {
            "factor_dag",
            "backpressure",
            "batch_output",
            "dag_manager",
            "dist_feature_eng",
        }
        assert expected_sections.issubset(config.keys())

    def test_factor_dag_section(self) -> None:
        config = load_core_config()
        assert config["factor_dag"]["max_layers"] == 20

    def test_backpressure_section(self) -> None:
        config = load_core_config()
        bp = config["backpressure"]
        assert bp["max_inflight"] == 8
        assert bp["high_watermark"] == 0.8
        assert bp["low_watermark"] == 0.5

    def test_batch_output_section(self) -> None:
        config = load_core_config()
        bo = config["batch_output"]
        assert bo["batch_size"] == 500
        assert bo["flush_interval_s"] == 5.0
        assert bo["target_table"] == "c1_market.factor_signal"


class TestGetSection:
    def test_existing_section(self) -> None:
        """取已有子节应返回非空 dict。"""
        bp = get_section("backpressure")
        assert bp == {
            "max_inflight": 8,
            "acquire_timeout_s": 30,
            "high_watermark": 0.8,
            "low_watermark": 0.5,
        }

    def test_missing_section_returns_empty(self) -> None:
        """取不存在的子节应返回 {}，不抛异常。"""
        assert get_section("nonexistent_section") == {}

    def test_non_dict_section_returns_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """子节值为非 dict（如标量）时返回 {}。"""
        # 构造一个 scalar_section: 42 的临时 YAML
        bad_config = tmp_path / "_config.yaml"
        bad_config.write_text("scalar_section: 42\n", encoding="utf-8")
        monkeypatch.setattr(loader, "_CONFIG_PATH", bad_config)
        assert get_section("scalar_section") == {}

    def test_all_five_sections_accessible(self) -> None:
        """5 个子节都能通过 get_section 取到。"""
        for name in ["factor_dag", "backpressure", "batch_output", "dag_manager", "dist_feature_eng"]:
            section = get_section(name)
            assert isinstance(section, dict), f"{name} 应为 dict"
            assert len(section) > 0, f"{name} 不应为空"


class TestConfigFileIntegrity:
    def test_config_file_is_valid_yaml(self) -> None:
        """_config.yaml 应是合法 YAML（能被 yaml.safe_load 解析）。"""
        config_path = Path(loader.__file__).resolve().parent.parent / "_config.yaml"
        assert config_path.exists(), f"配置文件应存在: {config_path}"
        with open(config_path, encoding="utf-8") as f:
            data: Any = yaml.safe_load(f)
        assert isinstance(data, dict)
