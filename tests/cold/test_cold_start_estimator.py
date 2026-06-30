# [A_test] module_id: SRC-TST-0545 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_cold_start_estimator
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_cold_start_estimator.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip(
    "zephyr.trading.feedback_loop.capacity_assurance.cold_start_estimator", reason="cold_start_estimator not available"
)
ColdStartEstimator = mod.ColdStartEstimator


class TestColdStartEstimator:
    def test_instantiation(self):
        cse = ColdStartEstimator()
        assert cse.DAY0_BUDGET_PCT == 0.50

    def test_set_initial_budget_and_get_day0(self):
        cse = ColdStartEstimator()
        cse.set_initial_budget("module_a", 1000)
        assert cse.get_day0_budget("module_a") == 500.0

    def test_get_day0_unknown_module(self):
        cse = ColdStartEstimator()
        assert cse.get_day0_budget("unknown") == 0

    def test_record_cost_and_calibrate(self):
        cse = ColdStartEstimator()
        cse.record_cost("module_a", 100)
        cse.record_cost("module_a", 200)
        result = cse.calibrate("module_a")
        assert result == 150.0

    def test_calibrate_no_data(self):
        cse = ColdStartEstimator()
        result = cse.calibrate("unknown")
        assert result is None

    def test_calibrate_single_record(self):
        cse = ColdStartEstimator()
        cse.record_cost("module_b", 42)
        assert cse.calibrate("module_b") == 42.0
