# [A_test] module_id: SRC-TST-1567 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_self_test_verifier
# [INVARIANTS] MIN_CHECKS=8;run_all_returns_VerifierResult;each_check_returns_status
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_self_test_verifier.py
# [TTL] task_bound

import os
import tempfile
import uuid

from zephyr.gov_drift.self_test_verifier import (
    SelfTestVerifier,
    VerifierResult,
)


class TestVerifierResult:
    def test_creation(self):
        r = VerifierResult(test_id=uuid.uuid4(), passed=True, checks=[], summary="0/0")
        assert r.passed is True
        assert r.checks == []
        assert r.summary == "0/0"

    def test_with_checks(self):
        checks = [{"check": "test_a", "status": "PASS", "detail": ""}]
        r = VerifierResult(test_id=uuid.uuid4(), passed=True, checks=checks, summary="1/1")
        assert len(r.checks) == 1
        assert r.checks[0]["status"] == "PASS"


class TestSelfTestVerifierInit:
    def test_default_base_dir(self):
        v = SelfTestVerifier()
        assert v._base_dir is not None
        assert os.path.isdir(v._base_dir)

    def test_custom_base_dir(self):
        v = SelfTestVerifier(base_dir=".")
        assert v._base_dir == "."

    def test_min_checks_constant(self):
        assert SelfTestVerifier.MIN_CHECKS == 8


class TestCheckCircularImport:
    def test_returns_dict_with_required_keys(self):
        v = SelfTestVerifier()
        result = v.check_circular_import()
        assert "check" in result
        assert "status" in result
        assert "detail" in result
        assert result["check"] == "circular_import"

    def test_status_is_pass_fail_or_error(self):
        v = SelfTestVerifier()
        result = v.check_circular_import()
        assert result["status"] in ("PASS", "FAIL", "ERROR")

    def test_empty_directory_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v = SelfTestVerifier(base_dir=tmpdir)
            result = v.check_circular_import()
            assert result["status"] == "PASS"


class TestCheckCascadeRecursion:
    def test_returns_dict_with_required_keys(self):
        v = SelfTestVerifier()
        result = v.check_cascade_recursion()
        assert result["check"] == "cascade_recursion"
        assert "status" in result

    def test_missing_state_machine(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v = SelfTestVerifier(base_dir=tmpdir)
            result = v.check_cascade_recursion()
            assert result["status"] == "FAIL"


class TestCheckLogicFragmentation:
    def test_returns_dict_with_required_keys(self):
        v = SelfTestVerifier()
        result = v.check_logic_fragmentation()
        assert result["check"] == "logic_fragmentation"
        assert "status" in result

    def test_empty_directory_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v = SelfTestVerifier(base_dir=tmpdir)
            result = v.check_logic_fragmentation()
            assert result["status"] == "PASS"


class TestCheckDataIntegrity:
    def test_missing_registry_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v = SelfTestVerifier(base_dir=tmpdir)
            result = v.check_data_integrity()
            assert result["status"] == "FAIL"
            assert "MISSING" in result["detail"]


class TestCheckFileCompleteness:
    def test_missing_files_in_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v = SelfTestVerifier(base_dir=tmpdir)
            result = v.check_file_completeness()
            assert result["status"] == "FAIL"


class TestCheckRaceCondition:
    def test_missing_mutex_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v = SelfTestVerifier(base_dir=tmpdir)
            result = v.check_race_condition()
            assert result["status"] == "FAIL"


class TestCheckTtlExpiry:
    def test_missing_state_machine_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v = SelfTestVerifier(base_dir=tmpdir)
            result = v.check_ttl_expiry()
            assert result["status"] == "FAIL"


class TestCheckDeadLetter:
    def test_missing_state_machine_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v = SelfTestVerifier(base_dir=tmpdir)
            result = v.check_dead_letter()
            assert result["status"] == "FAIL"


class TestRunAll:
    def test_returns_verifier_result(self):
        v = SelfTestVerifier()
        result = v.run_all()
        assert isinstance(result, VerifierResult)

    def test_has_at_least_min_checks(self):
        v = SelfTestVerifier()
        result = v.run_all()
        assert len(result.checks) >= SelfTestVerifier.MIN_CHECKS

    def test_each_check_has_required_fields(self):
        v = SelfTestVerifier()
        result = v.run_all()
        for check in result.checks:
            assert "check" in check
            assert "status" in check
            assert "detail" in check

    def test_summary_format(self):
        v = SelfTestVerifier()
        result = v.run_all()
        if result.passed:
            assert "/" in result.summary
