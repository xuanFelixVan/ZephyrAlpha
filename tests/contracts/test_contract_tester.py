# [A_test] module_id: MOD-GOV_contract_tester | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §contract_tester
# [MODULE] tests.test_contract_tester
# [INVARIANTS] ContractTester.test_contract必须返回ContractTestResult; ContractStatus为str Enum
# [MODIFY-GUARD] 仅当contract_tester公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_contract_tester.py -q
# [TTL] task_bound

import json

import yaml

from zephyr.infrastructure.contract_tester import (
    ContractStatus,
    ContractTester,
    ContractTestResult,
)


class TestContractStatus:
    def test_values(self):
        assert ContractStatus.PASS.value == "pass"
        assert ContractStatus.FAIL.value == "fail"
        assert ContractStatus.DRIFT.value == "drift"
        assert ContractStatus.NOT_FOUND.value == "not_found"

    def test_is_str_enum(self):
        assert isinstance(ContractStatus.PASS, str)


class TestContractTestResult:
    def test_default_construction(self):
        result = ContractTestResult(
            contract_path="test.yaml",
            status=ContractStatus.PASS,
        )
        assert result.passed is True
        assert result.failure_count == 0
        assert result.checks == []
        assert result.failures == []

    def test_passed_property(self):
        result = ContractTestResult(
            contract_path="test.yaml",
            status=ContractStatus.FAIL,
        )
        assert result.passed is False

    def test_failure_count(self):
        result = ContractTestResult(
            contract_path="test.yaml",
            status=ContractStatus.FAIL,
            failures=["err1", "err2"],
        )
        assert result.failure_count == 2


class TestContractTester:
    def test_instantiation(self):
        tester = ContractTester()
        assert tester is not None
        assert tester.strict is True

    def test_instantiation_non_strict(self):
        tester = ContractTester(strict=False)
        assert tester.strict is False

    def test_test_contract_nonexistent_file(self):
        tester = ContractTester()
        result = tester.test_contract("/nonexistent/contract.yaml")
        assert result.status == ContractStatus.NOT_FOUND
        assert len(result.failures) > 0

    def test_test_contract_valid_yaml(self, tmp_path):
        contract = tmp_path / "contract.yaml"
        contract.write_text(
            yaml.dump(
                {
                    "version": "1.0",
                    "module_id": "MOD-001",
                    "priority": "P0",
                    "status": "active",
                    "phase": 1,
                    "enabled": True,
                }
            ),
            encoding="utf-8",
        )
        tester = ContractTester()
        result = tester.test_contract(str(contract))
        assert result.status == ContractStatus.PASS

    def test_test_contract_missing_required_fields(self, tmp_path):
        contract = tmp_path / "contract.yaml"
        contract.write_text(
            yaml.dump({"version": ""}),
            encoding="utf-8",
        )
        tester = ContractTester()
        result = tester.test_contract(str(contract))
        assert result.status == ContractStatus.FAIL
        assert result.failure_count > 0

    def test_test_contract_type_mismatch_strict(self, tmp_path):
        contract = tmp_path / "contract.yaml"
        contract.write_text(
            yaml.dump({"version": 123, "enabled": "yes"}),
            encoding="utf-8",
        )
        tester = ContractTester(strict=True)
        result = tester.test_contract(str(contract))
        assert result.status == ContractStatus.FAIL

    def test_test_contract_type_mismatch_non_strict(self, tmp_path):
        contract = tmp_path / "contract.yaml"
        contract.write_text(
            yaml.dump({"version": 123}),
            encoding="utf-8",
        )
        tester = ContractTester(strict=False)
        result = tester.test_contract(str(contract))
        assert result.status == ContractStatus.DRIFT

    def test_test_contract_json(self, tmp_path):
        contract = tmp_path / "contract.json"
        contract.write_text(
            json.dumps({"version": "2.0", "module_id": "MOD-002"}),
            encoding="utf-8",
        )
        tester = ContractTester()
        result = tester.test_contract(str(contract))
        assert isinstance(result, ContractTestResult)

    def test_test_directory(self, tmp_path):
        subdir = tmp_path / "contracts"
        subdir.mkdir()
        (subdir / "a.yaml").write_text(yaml.dump({"version": "1.0"}), encoding="utf-8")
        (subdir / "b.yaml").write_text(yaml.dump({"version": "2.0"}), encoding="utf-8")
        tester = ContractTester()
        results = tester.test_directory(str(subdir))
        assert len(results) == 2

    def test_test_directory_nonexistent(self):
        tester = ContractTester()
        results = tester.test_directory("/nonexistent/dir")
        assert results == []

    def test_tests_run_counter(self, tmp_path):
        contract = tmp_path / "c.yaml"
        contract.write_text(yaml.dump({"version": "1.0"}), encoding="utf-8")
        tester = ContractTester()
        tester.test_contract(str(contract))
        tester.test_contract(str(contract))
        assert tester.tests_run == 2

    def test_test_contract_skip_validation(self, tmp_path):
        contract = tmp_path / "c.yaml"
        contract.write_text(yaml.dump({"version": ""}), encoding="utf-8")
        tester = ContractTester()
        result = tester.test_contract(str(contract), validate_required=False, validate_types=False)
        assert result.status == ContractStatus.PASS

    def test_test_contract_malformed_yaml(self, tmp_path):
        contract = tmp_path / "bad.yaml"
        contract.write_text(":\n  :\n    - invalid: [", encoding="utf-8")
        tester = ContractTester()
        result = tester.test_contract(str(contract))
        assert result.status == ContractStatus.FAIL
