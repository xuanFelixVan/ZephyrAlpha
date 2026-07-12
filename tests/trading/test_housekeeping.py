# [A_test] module_id: SRC-TST-1103 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_housekeeping
# [INVARIANTS] TEMP_PATTERNS is class-level list; should_clean returns bool
# [MODIFY-GUARD] src/zephyr/orchestrator/housekeeping.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] scan_temp_files/should_clean never raise
# [TESTS] tests/test_housekeeping.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.lifecycle.housekeeping import HousekeepingManager


class TestHousekeepingManagerInstantiation:
    def test_create_instance(self):
        mgr = HousekeepingManager()
        assert mgr is not None

    def test_temp_patterns_is_list(self):
        assert isinstance(HousekeepingManager.TEMP_PATTERNS, list)

    def test_temp_patterns_not_empty(self):
        assert len(HousekeepingManager.TEMP_PATTERNS) > 0


class TestScanTempFiles:
    def test_returns_list(self):
        mgr = HousekeepingManager()
        result = mgr.scan_temp_files()
        assert isinstance(result, list)

    def test_default_empty(self):
        mgr = HousekeepingManager()
        result = mgr.scan_temp_files()
        assert result == []


class TestShouldClean:
    def test_temp_prefix_match(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("_temp_data.py") is True

    def test_check_prefix_match(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("_check_result.py") is True

    def test_phase_prefix_match(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("_phase_1_report.py") is True

    def test_tmp_extension_not_matched_by_startswith(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("file.tmp") is False

    def test_bak_extension_not_matched_by_startswith(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("file.bak") is False

    def test_normal_file_no_match(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("script_runner.py") is False

    def test_empty_string(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("") is False

    def test_regular_yaml(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("blueprint.yaml") is False


class TestBoundary:
    def test_temp_patterns_shared_across_instances(self):
        mgr1 = HousekeepingManager()
        mgr2 = HousekeepingManager()
        assert mgr1.TEMP_PATTERNS is mgr2.TEMP_PATTERNS

    def test_should_clean_case_sensitive(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("_TEMP_data.py") is False

    def test_partial_prefix_no_underscore(self):
        mgr = HousekeepingManager()
        assert mgr.should_clean("temp_file.py") is False
