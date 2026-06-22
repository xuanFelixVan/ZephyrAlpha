# [A_test] module_id: SRC-TST-1139 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.integrity_self_check
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.integrity_self_check import EXPECTED_MODULES, IntegrityCheck, IntegritySelfCheck

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as e:
    _IMPORT_OK = False
    _IMPORT_REASON = str(e)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestIntegrityCheck:
    def test_default_values(self):
        ic = IntegrityCheck(module_name="test_mod")
        assert ic.module_name == "test_mod"
        assert ic.importable is False
        assert ic.has_public_api is False
        assert ic.passed is False
        assert ic.error == ""

    def test_passed_check(self):
        ic = IntegrityCheck(module_name="mod", importable=True, has_public_api=True, passed=True)
        assert ic.passed is True
        assert ic.importable is True


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestExpectedModules:
    def test_expected_modules_not_empty(self):
        assert len(EXPECTED_MODULES) > 0

    def test_expected_modules_are_strings(self):
        for mod in EXPECTED_MODULES:
            assert isinstance(mod, str)
            assert len(mod) > 0


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestIntegritySelfCheck:
    def test_check_all_returns_list(self):
        checker = IntegritySelfCheck()
        results = checker.check_all()
        assert isinstance(results, list)
        assert len(results) == len(EXPECTED_MODULES)

    def test_check_all_results_have_module_names(self):
        checker = IntegritySelfCheck()
        results = checker.check_all()
        result_names = [r.module_name for r in results]
        for mod in EXPECTED_MODULES:
            assert mod in result_names

    def test_summary_after_check_all(self):
        checker = IntegritySelfCheck()
        checker.check_all()
        s = checker.summary()
        assert "total_modules" in s
        assert "passed" in s
        assert "failed" in s
        assert "integrity_pct" in s
        assert "all_ok" in s
        assert s["total_modules"] == len(EXPECTED_MODULES)
        assert s["passed"] + s["failed"] == s["total_modules"]

    def test_summary_auto_runs_check_all(self):
        checker = IntegritySelfCheck()
        s = checker.summary()
        assert s["total_modules"] == len(EXPECTED_MODULES)

    def test_check_all_clears_previous_results(self):
        checker = IntegritySelfCheck()
        checker.check_all()
        first_count = len(checker._results)
        checker.check_all()
        assert len(checker._results) == first_count

    def test_integrity_pct_range(self):
        checker = IntegritySelfCheck()
        s = checker.summary()
        assert 0.0 <= s["integrity_pct"] <= 100.0
