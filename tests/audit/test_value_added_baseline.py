# [A_test] module_id: SRC-TST-1779 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_value_added_baseline
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.value_added_baseline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_value_added_baseline.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.value_added_baseline import ValueAddedBaseline


class TestValueAddedBaselineInstantiation:
    def test_default_params(self):
        vab = ValueAddedBaseline()
        assert vab.cost_baseline == 0.0
        assert vab.cost_fle == 0.0

    def test_custom_params(self):
        vab = ValueAddedBaseline(cost_baseline=100.0, cost_fle=60.0)
        assert vab.cost_baseline == 100.0
        assert vab.cost_fle == 60.0

    def test_is_dataclass(self):
        vab = ValueAddedBaseline()
        assert hasattr(vab, "__dataclass_fields__")


class TestRoi:
    def test_positive_roi(self):
        vab = ValueAddedBaseline(cost_baseline=100.0, cost_fle=60.0)
        assert vab.roi > 0.0

    def test_negative_roi(self):
        vab = ValueAddedBaseline(cost_baseline=50.0, cost_fle=100.0)
        assert vab.roi < 0.0

    def test_zero_fle_cost_positive_roi(self):
        vab = ValueAddedBaseline(cost_baseline=100.0, cost_fle=0.0)
        assert vab.roi > 0.0

    def test_equal_costs_zero_roi(self):
        vab = ValueAddedBaseline(cost_baseline=100.0, cost_fle=100.0)
        assert vab.roi == 0.0

    def test_roi_calculation_accuracy(self):
        vab = ValueAddedBaseline(cost_baseline=200.0, cost_fle=100.0)
        expected = (200.0 - 100.0) / 100.0
        assert abs(vab.roi - expected) < 0.001

    def test_roi_returns_float(self):
        vab = ValueAddedBaseline(cost_baseline=50.0, cost_fle=25.0)
        assert isinstance(vab.roi, float)

    def test_both_zero_costs(self):
        vab = ValueAddedBaseline(cost_baseline=0.0, cost_fle=0.0)
        assert vab.roi == 0.0

    def test_very_small_fle_cost(self):
        vab = ValueAddedBaseline(cost_baseline=100.0, cost_fle=0.5)
        assert vab.roi > 0.0
