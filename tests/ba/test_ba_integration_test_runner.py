# [A_test] module_id: SRC-TST-0401 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ba_integration_test_runner
# [INVARIANTS] 集成测试不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_ba_integration_test_runner.py
# [TTL] task_bound

from __future__ import annotations

import json
import os
import uuid

from zephyr.gov_enforcement.rule_enforcement.integration_test_runner import (
    IntegrationTestRunner,
    SelfTestResult,
)


class TestSelfTestResult:
    def test_defaults(self):
        test_id = uuid.uuid4()
        result = SelfTestResult(test_id=test_id, passed=True)
        assert result.test_id == test_id
        assert result.passed is True
        assert result.tests_run == 0
        assert result.failures == 0
        assert result.errors == 0
        assert result.checks == []
        assert result.run_at == ""

    def test_with_values(self):
        test_id = uuid.uuid4()
        result = SelfTestResult(
            test_id=test_id,
            passed=False,
            tests_run=3,
            failures=1,
            errors=1,
            checks=[{"check": "pip_check", "status": "FAIL", "detail": "broken"}],
            run_at="2026-01-01T00:00:00+00:00",
        )
        assert result.passed is False
        assert result.tests_run == 3
        assert result.failures == 1
        assert result.errors == 1
        assert len(result.checks) == 1


class TestIntegrationTestRunner:
    def test_instantiation_with_root(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        assert runner._project_root == str(tmp_path)
        assert os.path.isdir(runner._result_dir)

    def test_instantiation_default_root(self):
        runner = IntegrationTestRunner()
        assert runner._project_root is not None

    def test_pip_check_returns_result(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        result = runner.pip_check()
        assert isinstance(result, SelfTestResult)
        assert isinstance(result.test_id, uuid.UUID)
        assert len(result.checks) >= 1
        assert result.checks[0]["check"] == "pip_check"

    def test_import_check_returns_result(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        result = runner.import_check()
        assert isinstance(result, SelfTestResult)
        assert result.tests_run >= 1

    def test_type_check_returns_result(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        result = runner.type_check()
        assert isinstance(result, SelfTestResult)
        assert result.tests_run >= 1

    def test_run_all_aggregates(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        result = runner.run_all()
        assert isinstance(result, SelfTestResult)
        assert result.tests_run >= 3
        assert len(result.checks) >= 3
        assert result.run_at != ""

    def test_finalize_writes_json(self, tmp_path):
        runner = IntegrationTestRunner(project_root=str(tmp_path))
        result = runner.pip_check()
        result_file = os.path.join(runner._result_dir, f"{result.test_id}_test.json")
        assert os.path.exists(result_file)
        with open(result_file, encoding="utf-8") as fh:
            data = json.load(fh)
        assert "test_id" in data
        assert "passed" in data
        assert "tests_run" in data
