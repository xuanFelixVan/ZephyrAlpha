# [A_test] module_id: SRC-TST-0314 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_amplification_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.amplification_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_amplification_guard.py
# [TTL] task_bound

from zephyr.feedback_loop.diagnosers.amplification_guard import AmplificationGuard


class TestAmplificationGuard:
    def test_instantiation_default(self):
        guard = AmplificationGuard()
        assert guard.max_amplification == 5.0

    def test_instantiation_custom_max(self):
        guard = AmplificationGuard(max_amplification=3.0)
        assert guard.max_amplification == 3.0

    def test_check_within_limit(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=0.1, output_bias=0.3)
        assert result is True

    def test_check_exceeds_limit(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=0.01, output_bias=0.1)
        assert result is False

    def test_check_exact_limit(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=0.1, output_bias=0.5)
        assert result is True

    def test_check_zero_input_bias(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=0.0, output_bias=0.001)
        assert result is True

    def test_check_zero_input_bias_large_output(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=0.0, output_bias=1.0)
        assert result is False

    def test_check_negative_input_bias(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=-0.1, output_bias=0.3)
        assert isinstance(result, bool)

    def test_check_negative_output_bias(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=0.1, output_bias=-0.3)
        assert isinstance(result, bool)

    def test_check_both_zero(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=0.0, output_bias=0.0)
        assert result is True

    def test_check_very_small_input_bias(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=0.0001, output_bias=0.0004)
        assert result is True

    def test_check_very_small_input_exceeds(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=0.0001, output_bias=0.01)
        assert result is False

    def test_check_large_values_within_limit(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=10.0, output_bias=30.0)
        assert result is True

    def test_check_large_values_exceeds_limit(self):
        guard = AmplificationGuard(max_amplification=5.0)
        result = guard.check(input_bias=1.0, output_bias=10.0)
        assert result is False

    def test_check_custom_max_amplification(self):
        guard = AmplificationGuard(max_amplification=2.0)
        result = guard.check(input_bias=0.1, output_bias=0.25)
        assert result is False

    def test_check_custom_max_amplification_pass(self):
        guard = AmplificationGuard(max_amplification=2.0)
        result = guard.check(input_bias=0.1, output_bias=0.15)
        assert result is True
