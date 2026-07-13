# [A_test] module_id: SRC-TST-1236 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_llm_quality_regression
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.llm_quality_regression
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_llm_quality_regression.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.reliability.llm_quality_regression import LLMQualityRegression


class TestLLMQualityRegressionInstantiation:
    def test_default_instantiation(self):
        qr = LLMQualityRegression()
        assert qr.previous_accuracy == 0.0
        assert qr.current_accuracy == 0.0

    def test_custom_accuracies(self):
        qr = LLMQualityRegression(previous_accuracy=0.85, current_accuracy=0.82)
        assert qr.previous_accuracy == 0.85
        assert qr.current_accuracy == 0.82

    def test_is_dataclass(self):
        qr = LLMQualityRegression()
        assert hasattr(qr, "__dataclass_fields__")


class TestRegressed:
    def test_no_regression_when_equal(self):
        qr = LLMQualityRegression(previous_accuracy=0.80, current_accuracy=0.80)
        assert qr.regressed is False

    def test_no_regression_within_threshold(self):
        qr = LLMQualityRegression(previous_accuracy=0.80, current_accuracy=0.76)
        assert qr.regressed is False

    def test_regression_detected(self):
        qr = LLMQualityRegression(previous_accuracy=0.80, current_accuracy=0.70)
        assert qr.regressed is True

    def test_regression_at_exact_threshold(self):
        qr = LLMQualityRegression(previous_accuracy=0.80, current_accuracy=0.75)
        assert qr.regressed is False

    def test_regression_just_below_threshold(self):
        qr = LLMQualityRegression(previous_accuracy=0.80, current_accuracy=0.749)
        assert qr.regressed is True

    def test_improvement_not_regression(self):
        qr = LLMQualityRegression(previous_accuracy=0.80, current_accuracy=0.90)
        assert qr.regressed is False

    def test_zero_previous_accuracy(self):
        qr = LLMQualityRegression(previous_accuracy=0.0, current_accuracy=0.0)
        assert qr.regressed is False

    def test_both_zero(self):
        qr = LLMQualityRegression(previous_accuracy=0.0, current_accuracy=0.0)
        assert qr.regressed is False

    def test_large_regression(self):
        qr = LLMQualityRegression(previous_accuracy=0.95, current_accuracy=0.30)
        assert qr.regressed is True

    def test_negative_accuracy_values(self):
        qr = LLMQualityRegression(previous_accuracy=-0.1, current_accuracy=-0.2)
        assert qr.regressed is True
