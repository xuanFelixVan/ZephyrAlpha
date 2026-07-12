# [A_test] module_id: SRC-TST-0939 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_calendar_adapter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.calendar_adapter
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_calendar_adapter.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.collectors.calendar_adapter import CalendarAdapter


class TestCalendarAdapterInstantiation:
    def test_creates_with_defaults(self):
        adapter = CalendarAdapter()
        assert adapter.is_weekend is False

    def test_creates_with_weekend(self):
        adapter = CalendarAdapter(is_weekend=True)
        assert adapter.is_weekend is True


class TestCalendarAdapterAttributes:
    def test_is_weekend_false(self):
        adapter = CalendarAdapter(is_weekend=False)
        assert adapter.is_weekend is False

    def test_is_weekend_true(self):
        adapter = CalendarAdapter(is_weekend=True)
        assert adapter.is_weekend is True

    def test_is_weekend_toggle(self):
        adapter = CalendarAdapter(is_weekend=False)
        adapter.is_weekend = True
        assert adapter.is_weekend is True
