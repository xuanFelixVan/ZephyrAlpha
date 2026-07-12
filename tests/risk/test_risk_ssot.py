# [A_test] module_id: SRC-TST-1469 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §

# [MODULE] tests.test_risk_ssot

# [INVARIANTS] load_risk_params_ssot returns dict; never raises; returns {} on missing/invalid input

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] no exceptions raised from tests; all assertions use == or is

# [TESTS] tests/test_risk_ssot.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import yaml

from zephyr.gov_enforcement.rule_enforcement.risk_ssot import load_risk_params_ssot
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class TestLoadRiskParamsSsotReturnsDict:
    def test_returns_dict_when_valid_yaml(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "risk_params.yaml").write_text(
            "schema_version: '1.0'\nmax_gross_leverage: 1.0\n",
            encoding="utf-8",
        )
        result = load_risk_params_ssot(tmp_path)
        assert isinstance(result, dict)
        assert result["schema_version"] == "1.0"
        assert result["max_gross_leverage"] == 1.0

    def test_returns_nested_dict(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        content = yaml.dump({"limits": {"max_single": 0.05, "max_sector": 0.30}}, encoding=None)
        (config_dir / "risk_params.yaml").write_text(content, encoding="utf-8")
        result = load_risk_params_ssot(tmp_path)
        assert isinstance(result, dict)
        assert result["limits"]["max_single"] == 0.05
        assert result["limits"]["max_sector"] == 0.30

    def test_returns_real_project_config(self):
        project_root = REPO_ROOT  # alias 真源
        result = load_risk_params_ssot(project_root)
        assert isinstance(result, dict)
        assert "schema_version" in result
        assert result.get("canonical_source") is True


class TestLoadRiskParamsSsotMissingFile:
    def test_returns_empty_dict_when_no_config_dir(self, tmp_path: Path):
        result = load_risk_params_ssot(tmp_path)
        assert result == {}

    def test_returns_empty_dict_when_no_yaml_file(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        result = load_risk_params_ssot(tmp_path)
        assert result == {}

    def test_returns_empty_dict_when_path_is_file_not_dir(self, tmp_path: Path):
        fake_root = tmp_path / "not_a_dir"
        fake_root.write_text("hello", encoding="utf-8")
        result = load_risk_params_ssot(fake_root)
        assert result == {}


class TestLoadRiskParamsSsotInvalidContent:
    def test_returns_empty_dict_on_malformed_yaml(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "risk_params.yaml").write_text(
            "key: [unclosed\n  bad: {{\n",
            encoding="utf-8",
        )
        result = load_risk_params_ssot(tmp_path)
        assert result == {}

    def test_returns_empty_dict_on_empty_file(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "risk_params.yaml").write_text("", encoding="utf-8")
        result = load_risk_params_ssot(tmp_path)
        assert result == {}

    def test_returns_empty_dict_on_yaml_null_document(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "risk_params.yaml").write_text("---\n...\n", encoding="utf-8")
        result = load_risk_params_ssot(tmp_path)
        assert result == {}

    def test_returns_empty_dict_on_non_utf8_binary(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "risk_params.yaml").write_bytes(b"\x80\x81\x82\xff\xfe")
        result = load_risk_params_ssot(tmp_path)
        assert result == {}


class TestLoadRiskParamsSsotEdgeCases:
    def test_preserves_null_values(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "risk_params.yaml").write_text(
            "daily_loss_limit_nav_ratio: null\nschema_version: '1.0'\n",
            encoding="utf-8",
        )
        result = load_risk_params_ssot(tmp_path)
        assert isinstance(result, dict)
        assert result["daily_loss_limit_nav_ratio"] is None
        assert result["schema_version"] == "1.0"

    def test_preserves_string_and_numeric_types(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "risk_params.yaml").write_text(
            "ratio: 0.05\ncount: 10\nname: test\nflag: true\n",
            encoding="utf-8",
        )
        result = load_risk_params_ssot(tmp_path)
        assert isinstance(result["ratio"], float)
        assert isinstance(result["count"], int)
        assert isinstance(result["name"], str)
        assert isinstance(result["flag"], bool)

    def test_callable_multiple_times_same_root(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "risk_params.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")
        result1 = load_risk_params_ssot(tmp_path)
        result2 = load_risk_params_ssot(tmp_path)
        assert result1 == result2
