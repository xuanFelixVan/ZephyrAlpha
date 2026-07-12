# [A_test] module_id: SRC-TST-0786 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_dynamic_threshold
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.dynamic_threshold
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_dynamic_threshold.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.dynamic_threshold import DynamicThreshold


class TestDynamicThresholdInstantiation:
    def test_default_instantiation(self):
        obj = DynamicThreshold()
        assert obj.base == pytest.approx(2.5)
        assert obj.current == pytest.approx(2.5)

    def test_custom_values(self):
        obj = DynamicThreshold(base=5.0, current=3.0)
        assert obj.base == pytest.approx(5.0)
        assert obj.current == pytest.approx(3.0)

    def test_is_dataclass(self):
        obj = DynamicThreshold()
        assert hasattr(obj, "__dataclass_fields__")


class TestDynamicThresholdAttributes:
    def test_base_and_current_independent(self):
        dt = DynamicThreshold(base=10.0, current=2.0)
        assert dt.base != dt.current

    def test_base_modification(self):
        dt = DynamicThreshold()
        dt.base = 7.5
        assert dt.base == pytest.approx(7.5)

    def test_current_modification(self):
        dt = DynamicThreshold()
        dt.current = 1.0
        assert dt.current == pytest.approx(1.0)

    def test_zero_threshold(self):
        dt = DynamicThreshold(base=0.0, current=0.0)
        assert dt.base == pytest.approx(0.0)
        assert dt.current == pytest.approx(0.0)


class TestDynamicThresholdBoundaries:
    def test_negative_threshold(self):
        dt = DynamicThreshold(base=-1.0, current=-1.0)
        assert dt.base == pytest.approx(-1.0)

    def test_very_large_threshold(self):
        dt = DynamicThreshold(base=1e6, current=1e6)
        assert dt.base == pytest.approx(1e6)

    def test_float_precision(self):
        dt = DynamicThreshold(base=0.1 + 0.2, current=0.3)
        assert isinstance(dt.base, float)
        assert isinstance(dt.current, float)
