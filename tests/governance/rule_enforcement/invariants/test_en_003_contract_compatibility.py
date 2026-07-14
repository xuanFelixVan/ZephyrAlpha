# [A_test] module_id: SRC-TST-0833 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_en_003_contract_compatibility
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit code reflects pass/fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import dataclasses
from unittest.mock import patch

from zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility import (
    TYPE_ALIAS_MAP,
    CompatibilityResult,
    _get_dataclass_fields,
    _normalize_type,
    _strip_module_path,
    check,
    run_check,
)


class TestTypeAliasMap:
    def test_is_dict(self):
        assert isinstance(TYPE_ALIAS_MAP, dict)

    def test_basic_types_mapped(self):
        assert TYPE_ALIAS_MAP["str"] == "str"
        assert TYPE_ALIAS_MAP["int"] == "int"
        assert TYPE_ALIAS_MAP["float"] == "float"
        assert TYPE_ALIAS_MAP["bool"] == "bool"

    def test_optional_types_mapped(self):
        assert TYPE_ALIAS_MAP["Optional[str]"] == "Optional[str]"
        assert TYPE_ALIAS_MAP["Optional[int]"] == "Optional[int]"

    def test_dict_types_mapped(self):
        assert TYPE_ALIAS_MAP["Dict[str,float]"] == "Dict[str,float]"
        assert TYPE_ALIAS_MAP["Dict[str,str]"] == "Dict[str,str]"

    def test_special_types_mapped(self):
        assert TYPE_ALIAS_MAP["Decimal"] == "Decimal"
        assert TYPE_ALIAS_MAP["datetime"] == "datetime"
        assert TYPE_ALIAS_MAP["EnforcementMode"] == "EnforcementMode"


class TestCompatibilityResult:
    def test_passed_summary(self):
        cr = CompatibilityResult(passed=True, total=5, matched=5)
        assert cr.summary() == "[PASS] EN-003: 5/5 contracts field-compatible"

    def test_failed_summary(self):
        cr = CompatibilityResult(
            passed=False,
            total=3,
            matched=2,
            mismatches=["CTR-001/Foo: fields in spec but missing in code: ['x']"],
        )
        summary = cr.summary()
        assert "[FAIL] EN-003:" in summary
        assert "1 mismatch(es)" in summary

    def test_default_values(self):
        cr = CompatibilityResult(passed=True)
        assert cr.total == 0
        assert cr.matched == 0
        assert cr.mismatches == []
        assert cr.skipped == []

    def test_failed_with_multiple_mismatches(self):
        cr = CompatibilityResult(
            passed=False,
            total=2,
            matched=0,
            mismatches=["m1", "m2", "m3"],
        )
        summary = cr.summary()
        assert "3 mismatch(es)" in summary


class TestNormalizeType:
    def test_known_type(self):
        assert _normalize_type("str") == "str"

    def test_known_optional(self):
        assert _normalize_type("Optional[int]") == "Optional[int]"

    def test_unknown_type_passthrough(self):
        assert _normalize_type("CustomType") == "CustomType"

    def test_whitespace_stripped(self):
        assert _normalize_type("  str  ") == "str"

    def test_dict_type(self):
        assert _normalize_type("Dict[str,float]") == "Dict[str,float]"

    def test_empty_string(self):
        assert _normalize_type("") == ""


class TestStripModulePath:
    def test_standard_path(self):
        result = _strip_module_path("src/zephyr/shared/contracts/my_class.py")
        assert result is not None
        module_path, class_name = result
        assert module_path.startswith("zephyr.")
        assert class_name == "MyClass"

    def test_non_py_file(self):
        result = _strip_module_path("src/zephyr/shared/contracts/data.yaml")
        assert result is None

    def test_path_with_zephyr_parent(self):
        result = _strip_module_path("src/zephyr/l01-infrastructure/telemetry.py")
        assert result is not None
        module_path, class_name = result
        assert "zephyr.l01_infrastructure" in module_path
        assert class_name == "Telemetry"

    def test_underscore_to_camelcase(self):
        result = _strip_module_path("src/zephyr/shared/contracts/my_long_name.py")
        assert result is not None
        _, class_name = result
        assert class_name == "MyLongName"

    def test_single_word_filename(self):
        result = _strip_module_path("src/zephyr/shared/contracts/gateway.py")
        assert result is not None
        _, class_name = result
        assert class_name == "Gateway"


class TestGetDataclassFields:
    def test_real_dataclass(self):
        @dataclasses.dataclass
        class SampleDC:
            name: str
            value: int

        import sys

        sys.modules["_test_sample_dc"] = sys.modules[__name__]
        with patch(
            "zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility.importlib.import_module"
        ) as mock_import:
            mock_mod = type("mod", (), {"SampleDC": SampleDC})()
            mock_import.return_value = mock_mod
            result = _get_dataclass_fields("_test_sample_dc", "SampleDC")
            assert result is not None
            assert "name" in result
            assert "value" in result

    def test_nonexistent_module(self):
        result = _get_dataclass_fields("nonexistent.module.xyz", "Foo")
        assert result is None

    def test_nonexistent_class(self):
        result = _get_dataclass_fields("zephyr.integration.shared.schema.schemas", "NonexistentClass12345")
        assert result is None

    def test_non_dataclass(self):
        result = _get_dataclass_fields(
            "zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility", "TYPE_ALIAS_MAP"
        )
        assert result is None


class TestRunCheck:
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._load_contracts")
    def test_empty_contracts_passes(self, mock_load):
        mock_load.return_value = {"contracts": []}
        result = run_check()
        assert result.passed is True
        assert result.total == 0

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._load_contracts")
    def test_contract_no_physical_path_skipped(self, mock_load):
        mock_load.return_value = {
            "contracts": [
                {"id": "CTR-001", "fields": [{"name": "x"}]},
            ]
        }
        result = run_check()
        assert result.passed is True
        assert len(result.skipped) >= 1

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._load_contracts")
    def test_contract_no_fields_skipped(self, mock_load):
        mock_load.return_value = {
            "contracts": [
                {"id": "CTR-002", "physical_path": "src/zephyr/shared/contracts/foo.py"},
            ]
        }
        result = run_check()
        assert result.passed is True
        assert len(result.skipped) >= 1

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._load_contracts")
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._get_dataclass_fields")
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._strip_module_path")
    def test_matching_fields_passes(self, mock_strip, mock_fields, mock_load):
        mock_strip.return_value = ("zephyr.shared.contracts.foo", "Foo")
        mock_fields.return_value = {"name": "str", "value": "int"}
        mock_load.return_value = {
            "contracts": [
                {
                    "id": "CTR-003",
                    "physical_path": "src/zephyr/shared/contracts/foo.py",
                    "fields": [
                        {"name": "name", "type": "str"},
                        {"name": "value", "type": "int"},
                    ],
                },
            ]
        }
        result = run_check()
        assert result.passed is True
        assert result.matched == 1

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._load_contracts")
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._get_dataclass_fields")
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._strip_module_path")
    def test_missing_field_in_code_fails(self, mock_strip, mock_fields, mock_load):
        mock_strip.return_value = ("zephyr.shared.contracts.foo", "Foo")
        mock_fields.return_value = {"name": "str"}
        mock_load.return_value = {
            "contracts": [
                {
                    "id": "CTR-004",
                    "physical_path": "src/zephyr/shared/contracts/foo.py",
                    "fields": [
                        {"name": "name", "type": "str"},
                        {"name": "value", "type": "int"},
                    ],
                },
            ]
        }
        result = run_check()
        assert result.passed is False
        assert len(result.mismatches) >= 1

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._load_contracts")
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._get_dataclass_fields")
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._strip_module_path")
    def test_extra_field_in_code_fails(self, mock_strip, mock_fields, mock_load):
        mock_strip.return_value = ("zephyr.shared.contracts.foo", "Foo")
        mock_fields.return_value = {"name": "str", "value": "int", "extra": "float"}
        mock_load.return_value = {
            "contracts": [
                {
                    "id": "CTR-005",
                    "physical_path": "src/zephyr/shared/contracts/foo.py",
                    "fields": [
                        {"name": "name", "type": "str"},
                        {"name": "value", "type": "int"},
                    ],
                },
            ]
        }
        result = run_check()
        assert result.passed is False

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._load_contracts")
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._strip_module_path")
    def test_unresolvable_module_skipped(self, mock_strip, mock_load):
        mock_strip.return_value = None
        mock_load.return_value = {
            "contracts": [
                {
                    "id": "CTR-006",
                    "physical_path": "some/weird/path.py",
                    "fields": [{"name": "x"}],
                },
            ]
        }
        result = run_check()
        assert len(result.skipped) >= 1

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._load_contracts")
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._get_dataclass_fields")
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility._strip_module_path")
    def test_type_mismatch_fails(self, mock_strip, mock_fields, mock_load):
        mock_strip.return_value = ("zephyr.shared.contracts.foo", "Foo")
        mock_fields.return_value = {"name": "int"}
        mock_load.return_value = {
            "contracts": [
                {
                    "id": "CTR-007",
                    "physical_path": "src/zephyr/shared/contracts/foo.py",
                    "fields": [
                        {"name": "name", "type": "str"},
                    ],
                },
            ]
        }
        result = run_check()
        assert result.passed is False


class TestCheck:
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility.run_check")
    def test_returns_tuple(self, mock_run):
        mock_run.return_value = CompatibilityResult(passed=True, total=3, matched=3)
        passed, msg = check()
        assert isinstance(passed, bool)
        assert isinstance(msg, str)

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility.run_check")
    def test_pass(self, mock_run):
        mock_run.return_value = CompatibilityResult(passed=True, total=5, matched=5)
        passed, msg = check()
        assert passed is True
        assert "[PASS]" in msg

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility.run_check")
    def test_fail(self, mock_run):
        mock_run.return_value = CompatibilityResult(passed=False, total=2, matched=1, mismatches=["m1"])
        passed, msg = check()
        assert passed is False
        assert "[FAIL]" in msg
