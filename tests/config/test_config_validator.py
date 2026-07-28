# [A_test] module_id: MOD-GOV_config_validator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §config_validator
# [MODULE] tests.test_config_validator
# [INVARIANTS] ConfigValidator.validate必须返回ValidationResult; ValidationResult.valid反映errors存在
# [MODIFY-GUARD] 仅当config_validator公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_config_validator.py -q
# [TTL] task_bound

import json
from pathlib import Path

import yaml

from zephyr.infrastructure.config_validator import (
    ConfigValidator,
    ValidationResult,
    ValidationSeverity,
)


class TestValidationSeverity:
    def test_values(self):
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.INFO.value == "info"


class TestValidationResult:
    def test_default_valid(self):
        result = ValidationResult(file_path="test.yaml")
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.infos == []
        assert result.checked_fields == 0

    def test_total_issues(self):
        result = ValidationResult(
            file_path="test.yaml",
            errors=["e1"],
            warnings=["w1", "w2"],
        )
        assert result.total_issues == 3


class TestConfigValidator:
    def test_instantiation(self):
        validator = ConfigValidator()
        assert validator is not None

    def test_instantiation_with_schema_path(self):
        validator = ConfigValidator(schema_path="/some/path")
        assert validator.schema_path == Path("/some/path")

    def test_validate_nonexistent_file(self):
        validator = ConfigValidator()
        result = validator.validate("/nonexistent/file.yaml")
        assert result.valid is False
        assert len(result.errors) > 0

    def test_validate_valid_yaml(self, tmp_path):
        cfg = tmp_path / "thresholds.yaml"
        cfg.write_text(
            yaml.dump(
                {
                    "version": "1.0",
                    "thresholds": {"latency": 100},
                    "error_budget": 0.1,
                }
            ),
            encoding="utf-8",
        )
        validator = ConfigValidator()
        result = validator.validate(str(cfg))
        assert result.valid is True
        assert result.checked_fields > 0

    def test_validate_missing_required_fields(self, tmp_path):
        cfg = tmp_path / "thresholds.yaml"
        cfg.write_text(yaml.dump({"version": "1.0"}), encoding="utf-8")
        validator = ConfigValidator()
        result = validator.validate(str(cfg))
        assert result.valid is False
        assert any("缺少必需字段" in e for e in result.errors)

    def test_validate_numeric_out_of_range(self, tmp_path):
        cfg = tmp_path / "test.yaml"
        cfg.write_text(
            yaml.dump({"error_budget": 5.0, "timeout": 99999}),
            encoding="utf-8",
        )
        validator = ConfigValidator()
        result = validator.validate(str(cfg))
        assert len(result.warnings) > 0

    def test_validate_null_values(self, tmp_path):
        cfg = tmp_path / "test.yaml"
        cfg.write_text(yaml.dump({"key1": None, "key2": ""}), encoding="utf-8")
        validator = ConfigValidator()
        result = validator.validate(str(cfg))
        assert any("null" in w for w in result.warnings)
        assert any("空字符串" in w for w in result.warnings)

    def test_validate_empty_list(self, tmp_path):
        cfg = tmp_path / "test.yaml"
        cfg.write_text(yaml.dump({"items": []}), encoding="utf-8")
        validator = ConfigValidator()
        result = validator.validate(str(cfg))
        assert any("空列表" in i for i in result.infos)

    def test_validate_json_file(self, tmp_path):
        cfg = tmp_path / "test.json"
        cfg.write_text(json.dumps({"version": "1.0", "enabled": True}), encoding="utf-8")
        validator = ConfigValidator()
        result = validator.validate(str(cfg))
        assert isinstance(result, ValidationResult)

    def test_validate_strict_mode_warnings_fail(self, tmp_path):
        cfg = tmp_path / "test.yaml"
        cfg.write_text(yaml.dump({"error_budget": 5.0}), encoding="utf-8")
        validator = ConfigValidator()
        result = validator.validate(str(cfg), strict=True)
        assert result.valid is False

    def test_validate_non_yaml_non_json(self, tmp_path):
        cfg = tmp_path / "test.txt"
        cfg.write_text("some text content", encoding="utf-8")
        validator = ConfigValidator()
        result = validator.validate(str(cfg))
        assert isinstance(result, ValidationResult)

    def test_validate_malformed_yaml(self, tmp_path):
        cfg = tmp_path / "bad.yaml"
        cfg.write_text(":\n  :\n    - invalid: [", encoding="utf-8")
        validator = ConfigValidator()
        result = validator.validate(str(cfg))
        assert isinstance(result, ValidationResult)
