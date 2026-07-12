# [A_test] module_id: SRC-TST-0378 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_auto_reward
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.auto_reward
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_auto_reward.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.auto_reward import AutoReward


class TestAutoRewardInstantiation:
    def test_default_instantiation(self):
        obj = AutoReward()
        assert obj is not None

    def test_is_dataclass(self):
        obj = AutoReward()
        assert hasattr(obj, "__dataclass_fields__")


class TestAutoRewardCompute:
    def test_positive_reward(self):
        ar = AutoReward()
        result = ar.compute(pre_state=0.3, post_state=0.8)
        assert result == pytest.approx(0.5)

    def test_negative_reward(self):
        ar = AutoReward()
        result = ar.compute(pre_state=0.9, post_state=0.2)
        assert result == pytest.approx(-0.7)

    def test_zero_reward(self):
        ar = AutoReward()
        result = ar.compute(pre_state=0.5, post_state=0.5)
        assert result == pytest.approx(0.0)

    def test_large_values(self):
        ar = AutoReward()
        result = ar.compute(pre_state=-100.0, post_state=100.0)
        assert result == pytest.approx(200.0)

    def test_negative_states(self):
        ar = AutoReward()
        result = ar.compute(pre_state=-5.0, post_state=-2.0)
        assert result == pytest.approx(3.0)


class TestAutoRewardBoundaries:
    def test_both_zero(self):
        ar = AutoReward()
        result = ar.compute(pre_state=0.0, post_state=0.0)
        assert result == pytest.approx(0.0)

    def test_float_precision(self):
        ar = AutoReward()
        result = ar.compute(pre_state=0.1, post_state=0.2)
        assert isinstance(result, float)

    def test_very_small_difference(self):
        ar = AutoReward()
        result = ar.compute(pre_state=1.0, post_state=1.0 + 1e-15)
        assert result >= 0.0
