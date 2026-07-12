# [A_test] module_id: SRC-TST-1135 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_integration_test_runner
# [INVARIANTS] 集成测试不可跳过;测试必须覆盖空输入/None/异常边界
# [MODIFY-GUARD] integration_test_runner.py变更时同步更新
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception;AssertionError
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
import os
import uuid
from unittest.mock import MagicMock, patch

from zephyr.gov_enforcement.rule_enforcement.integration_test_runner import (
    IntegrationTestRunner,
    SelfTestResult,
)


class TestSelfTestResult:
    def test_default_values(self):
        test_id = uuid.uuid4()
        result = SelfTestResult(test_id=test_id, passed=True)
        assert result.test_id == test_id
        assert result.passed is True
        assert result.tests_run == 0
        assert result.failures == 0
        assert result.errors == 0
        assert result.checks == []
        assert result.run_at == ""

    def test_passed_false(self):
        result = SelfTestResult(test_id=uuid.uuid4(), passed=False)
        assert result.passed is False

    def test_custom_values(self):
        test_id = uuid.uuid4()
        checks = [{"check": "a", "status": "PASS", "detail": ""}]
        result = SelfTestResult(
            test_id=test_id,
            passed=True,
            tests_run=3,
            failures=1,
            errors=0,
            checks=checks,
            run_at="2026-01-01T00:00:00+00:00",
        )
        assert result.tests_run == 3
        assert result.failures == 1
        assert result.checks == checks
        assert result.run_at == "2026-01-01T00:00:00+00:00"

    def test_checks_independent_between_instances(self):
        r1 = SelfTestResult(test_id=uuid.uuid4(), passed=True)
        r2 = SelfTestResult(test_id=uuid.uuid4(), passed=True)
        r1.checks.append({"check": "x", "status": "PASS", "detail": ""})
        assert len(r2.checks) == 0


class TestIntegrationTestRunnerInit:
    def test_init_with_explicit_root(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        assert runner._project_root == str(tmp_path)
        assert runner._result_dir == str(tmp_path / "data" / "drift_audit")
        assert os.path.isdir(runner._result_dir)

    def test_init_with_none_uses_default(self):
        runner = IntegrationTestRunner(project_root=None)
        assert os.path.isdir(runner._result_dir)
        assert runner._project_root != ""

    def test_result_dir_created_on_init(self, tmp_path):
        result_dir = tmp_path / "data" / "drift_audit"
        assert not result_dir.exists()
        IntegrationTestRunner(project_root=str(tmp_path))
        assert result_dir.is_dir()


class TestPipCheck:
    def test_pip_check_success(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "No broken requirements found."
        with patch(
            "zephyr.governance.rule_enforcement.integration_test_runner.subprocess.run", return_value=mock_result
        ):
            result = runner.pip_check()
        assert isinstance(result, SelfTestResult)
        assert result.tests_run == 1
        assert any(c["check"] == "pip_check" for c in result.checks)
        pip_entry = next(c for c in result.checks if c["check"] == "pip_check")
        assert pip_entry["status"] == "PASS"

    def test_pip_check_failure(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "some-package 1.0 requires missing-dep"
        with patch(
            "zephyr.governance.rule_enforcement.integration_test_runner.subprocess.run", return_value=mock_result
        ):
            result = runner.pip_check()
        assert result.passed is False
        assert result.failures == 1
        pip_entry = next(c for c in result.checks if c["check"] == "pip_check")
        assert pip_entry["status"] == "FAIL"

    def test_pip_check_timeout(self, tmp_path):
        import subprocess as sp

        runner = IntegrationTestRunner(project_root=str(tmp_path))
        with patch(
            "zephyr.governance.rule_enforcement.integration_test_runner.subprocess.run",
            side_effect=sp.TimeoutExpired(cmd="pip check", timeout=60),
        ):
            result = runner.pip_check()
        assert result.passed is False
        assert result.errors == 1
        pip_entry = next(c for c in result.checks if c["check"] == "pip_check")
        assert pip_entry["status"] == "ERROR"

    def test_pip_check_file_not_found(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        with patch(
            "zephyr.governance.rule_enforcement.integration_test_runner.subprocess.run",
            side_effect=FileNotFoundError("pip not found"),
        ):
            result = runner.pip_check()
        assert result.passed is False
        assert result.errors == 1


class TestImportCheck:
    def test_import_check_returns_self_test_result(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        result = runner.import_check()
        assert isinstance(result, SelfTestResult)
        assert result.tests_run > 0
        assert len(result.checks) == result.tests_run

    def test_import_check_each_entry_has_required_keys(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        result = runner.import_check()
        for check in result.checks:
            assert "check" in check
            assert "status" in check
            assert check["status"] in ("PASS", "FAIL")
            assert "detail" in check

    def test_import_check_with_mock_all_pass(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        with patch("builtins.__import__", return_value=MagicMock()):
            result = runner.import_check()
        assert result.passed is True
        assert result.failures == 0

    def test_import_check_with_mock_import_error(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        original_import = __import__

        def fake_import(name, *args, **kwargs):
            if "behavioral-auditor" in name:
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            result = runner.import_check()
        assert result.passed is False
        assert result.failures > 0


class TestTypeCheck:
    def test_type_check_file_exists(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        check_dir = tmp_path / "src" / "zephyr" / "behavioral-auditor"
        check_dir.mkdir(parents=True, exist_ok=True)
        (check_dir / "self_check.py").write_text("# stub", encoding="utf-8")
        result = runner.type_check()
        assert isinstance(result, SelfTestResult)
        assert result.tests_run == 1
        assert result.passed is True
        sc_entry = next(c for c in result.checks if c["check"] == "self_check")
        assert sc_entry["status"] == "EXISTS"

    def test_type_check_file_missing(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        result = runner.type_check()
        assert result.passed is False
        assert result.failures == 1
        sc_entry = next(c for c in result.checks if c["check"] == "self_check")
        assert sc_entry["status"] == "MISSING"


class TestRunAll:
    def test_run_all_aggregates_results(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        mock_pip = SelfTestResult(
            test_id=uuid.uuid4(), passed=True, tests_run=1, checks=[{"check": "pip", "status": "PASS", "detail": ""}]
        )
        mock_import = SelfTestResult(
            test_id=uuid.uuid4(), passed=True, tests_run=2, checks=[{"check": "imp", "status": "PASS", "detail": ""}]
        )
        mock_type = SelfTestResult(
            test_id=uuid.uuid4(), passed=True, tests_run=1, checks=[{"check": "type", "status": "PASS", "detail": ""}]
        )
        with (
            patch.object(runner, "pip_check", return_value=mock_pip),
            patch.object(runner, "import_check", return_value=mock_import),
            patch.object(runner, "type_check", return_value=mock_type),
        ):
            result = runner.run_all()
        assert result.tests_run == 4
        assert len(result.checks) == 3
        assert result.passed is True

    def test_run_all_propagates_failure(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        mock_pip = SelfTestResult(
            test_id=uuid.uuid4(),
            passed=False,
            tests_run=1,
            failures=1,
            checks=[{"check": "pip", "status": "FAIL", "detail": "err"}],
        )
        mock_import = SelfTestResult(
            test_id=uuid.uuid4(), passed=True, tests_run=2, checks=[{"check": "imp", "status": "PASS", "detail": ""}]
        )
        mock_type = SelfTestResult(
            test_id=uuid.uuid4(), passed=True, tests_run=1, checks=[{"check": "type", "status": "PASS", "detail": ""}]
        )
        with (
            patch.object(runner, "pip_check", return_value=mock_pip),
            patch.object(runner, "import_check", return_value=mock_import),
            patch.object(runner, "type_check", return_value=mock_type),
        ):
            result = runner.run_all()
        assert result.passed is False
        assert result.failures == 1

    def test_run_all_accumulates_errors(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        mock_pip = SelfTestResult(test_id=uuid.uuid4(), passed=True, tests_run=1, errors=0, checks=[])
        mock_import = SelfTestResult(test_id=uuid.uuid4(), passed=True, tests_run=2, errors=1, checks=[])
        mock_type = SelfTestResult(test_id=uuid.uuid4(), passed=True, tests_run=1, errors=0, checks=[])
        with (
            patch.object(runner, "pip_check", return_value=mock_pip),
            patch.object(runner, "import_check", return_value=mock_import),
            patch.object(runner, "type_check", return_value=mock_type),
        ):
            result = runner.run_all()
        assert result.errors == 1


class TestFinalize:
    def test_finalize_writes_json(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        test_id = uuid.uuid4()
        result = SelfTestResult(test_id=test_id, passed=True, tests_run=2, failures=0, errors=0, checks=[])
        returned = runner._finalize(result)
        assert returned.run_at != ""
        json_path = os.path.join(runner._result_dir, f"{test_id}_test.json")
        assert os.path.isfile(json_path)
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["test_id"] == str(test_id)
        assert data["passed"] is True
        assert data["tests_run"] == 2

    def test_finalize_sets_run_at(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        result = SelfTestResult(test_id=uuid.uuid4(), passed=True)
        assert result.run_at == ""
        runner._finalize(result)
        assert result.run_at != ""

    def test_finalize_json_contains_all_fields(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        test_id = uuid.uuid4()
        checks = [{"check": "a", "status": "PASS", "detail": "ok"}]
        result = SelfTestResult(test_id=test_id, passed=False, tests_run=5, failures=2, errors=1, checks=checks)
        runner._finalize(result)
        json_path = os.path.join(runner._result_dir, f"{test_id}_test.json")
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["passed"] is False
        assert data["tests_run"] == 5
        assert data["failures"] == 2
        assert data["errors"] == 1
        assert len(data["checks"]) == 1
        assert data["run_at"] != ""
