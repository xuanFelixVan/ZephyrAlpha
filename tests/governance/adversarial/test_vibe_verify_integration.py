# [A_test] module_id: SRC-TST-1794 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_vibe_verify_integration
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_vibe_verify_integration.py -q
# [TTL] task_bound

from zephyr.governance.security_governance.vibe_verify_integration import VibeVerifyIntegration


class TestVibeVerifyIntegrationInstantiation:
    def test_default_scan_count_is_zero(self):
        obj = VibeVerifyIntegration()
        assert obj.scan_count == 0

    def test_default_violations_patched_is_zero(self):
        obj = VibeVerifyIntegration()
        assert obj.violations_patched == 0

    def test_patch_count_property_initial_zero(self):
        obj = VibeVerifyIntegration()
        assert obj.patch_count == 0


class TestScanAndPatch:
    def test_clean_code_returns_true_zero(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("x = 1 + 2")
        assert result == (True, 0)

    def test_eval_violation_detected(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("eval('2+2')")
        assert result == (False, 1)

    def test_exec_violation_detected(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("exec('print(1)')")
        assert result == (False, 1)

    def test_both_violations_detected(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("eval('1'); exec('2')")
        assert result == (False, 2)

    def test_scan_count_increments_each_call(self):
        obj = VibeVerifyIntegration()
        obj.scan_and_patch("x=1")
        obj.scan_and_patch("eval('1')")
        obj.scan_and_patch("x=2")
        assert obj.scan_count == 3

    def test_patch_count_accumulates_across_scans(self):
        obj = VibeVerifyIntegration()
        obj.scan_and_patch("eval('1')")
        obj.scan_and_patch("exec('2')")
        assert obj.patch_count == 2

    def test_empty_string_is_clean(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("")
        assert result == (True, 0)

    def test_partial_match_not_flagged(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("evaluate(x)")
        assert result == (True, 0)

    def test_execute_partial_not_flagged(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("executor.run()")
        assert result == (True, 0)


class TestScanAndPatchBoundary:
    def test_eval_with_spaces_not_detected(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("eval ('1')")
        assert result == (True, 0)

    def test_exec_with_spaces_not_detected(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("exec ('1')")
        assert result == (True, 0)

    def test_multiple_scans_accumulate_violations(self):
        obj = VibeVerifyIntegration()
        obj.scan_and_patch("eval('1')")
        obj.scan_and_patch("eval('2'); exec('3')")
        assert obj.patch_count == 3

    def test_scan_returns_tuple(self):
        obj = VibeVerifyIntegration()
        result = obj.scan_and_patch("x=1")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], int)
