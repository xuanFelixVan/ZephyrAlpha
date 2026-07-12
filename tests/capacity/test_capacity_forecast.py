# [A_test] module_id: SRC-TST-0494 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_capacity_forecast
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_capacity_forecast.py
# [TTL] task_bound

from __future__ import annotations

import math

from zephyr.feedback_loop.detectors.capacity_forecast import CapacityForecast


class TestCapacityForecastInstantiation:
    def test_default_construction(self):
        cf = CapacityForecast()
        assert cf.days_until_full == float("inf")

    def test_custom_days(self):
        cf = CapacityForecast(days_until_full=7.5)
        assert cf.days_until_full == 7.5

    def test_zero_days(self):
        cf = CapacityForecast(days_until_full=0.0)
        assert cf.days_until_full == 0.0

    def test_negative_days(self):
        cf = CapacityForecast(days_until_full=-1.0)
        assert cf.days_until_full == -1.0


class TestDaysUntilFullAttribute:
    def test_mutation(self):
        cf = CapacityForecast()
        cf.days_until_full = 3.0
        assert cf.days_until_full == 3.0

    def test_infinity_default(self):
        cf = CapacityForecast()
        assert math.isinf(cf.days_until_full)

    def test_finite_value(self):
        cf = CapacityForecast(days_until_full=14.0)
        assert not math.isinf(cf.days_until_full)
        assert cf.days_until_full == 14.0

    def test_independent_instances(self):
        a = CapacityForecast(days_until_full=5.0)
        b = CapacityForecast()
        a.days_until_full = 10.0
        assert math.isinf(b.days_until_full)
