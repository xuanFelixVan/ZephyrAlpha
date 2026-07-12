# [A_test] module_id: SRC-TST-0477 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_burnout_alarm
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.burnout_alarm
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_burnout_alarm.py
# [TTL] task_bound

from zephyr.feedback_loop.diagnosers.burnout_alarm import BurnoutAlarm


class TestBurnoutAlarm:
    def test_instantiation_default(self):
        alarm = BurnoutAlarm()
        assert alarm.response_latency_avg == 0.0
        assert alarm.skip_rate == 0.0

    def test_instantiation_custom(self):
        alarm = BurnoutAlarm(response_latency_avg=100.0, skip_rate=0.1)
        assert alarm.response_latency_avg == 100.0
        assert alarm.skip_rate == 0.1

    def test_alarm_default_no_alarm(self):
        alarm = BurnoutAlarm()
        assert alarm.alarm is False

    def test_alarm_triggered_by_high_latency(self):
        alarm = BurnoutAlarm(response_latency_avg=4000.0)
        assert alarm.alarm is True

    def test_alarm_triggered_by_high_skip_rate(self):
        alarm = BurnoutAlarm(skip_rate=0.5)
        assert alarm.alarm is True

    def test_alarm_not_triggered_by_low_latency(self):
        alarm = BurnoutAlarm(response_latency_avg=100.0)
        assert alarm.alarm is False

    def test_alarm_not_triggered_by_low_skip_rate(self):
        alarm = BurnoutAlarm(skip_rate=0.1)
        assert alarm.alarm is False

    def test_alarm_latency_exact_threshold(self):
        alarm = BurnoutAlarm(response_latency_avg=3600.0)
        assert alarm.alarm is False

    def test_alarm_skip_rate_exact_threshold(self):
        alarm = BurnoutAlarm(skip_rate=0.3)
        assert alarm.alarm is False

    def test_alarm_latency_just_above_threshold(self):
        alarm = BurnoutAlarm(response_latency_avg=3600.1)
        assert alarm.alarm is True

    def test_alarm_skip_rate_just_above_threshold(self):
        alarm = BurnoutAlarm(skip_rate=0.31)
        assert alarm.alarm is True

    def test_alarm_both_triggers(self):
        alarm = BurnoutAlarm(response_latency_avg=5000.0, skip_rate=0.6)
        assert alarm.alarm is True

    def test_alarm_zero_values(self):
        alarm = BurnoutAlarm(response_latency_avg=0.0, skip_rate=0.0)
        assert alarm.alarm is False

    def test_alarm_negative_latency(self):
        alarm = BurnoutAlarm(response_latency_avg=-10.0)
        assert alarm.alarm is False

    def test_alarm_negative_skip_rate(self):
        alarm = BurnoutAlarm(skip_rate=-0.1)
        assert alarm.alarm is False

    def test_alarm_very_high_latency(self):
        alarm = BurnoutAlarm(response_latency_avg=100000.0)
        assert alarm.alarm is True

    def test_alarm_skip_rate_at_one(self):
        alarm = BurnoutAlarm(skip_rate=1.0)
        assert alarm.alarm is True
