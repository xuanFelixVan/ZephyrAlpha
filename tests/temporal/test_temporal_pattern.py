# [A_test] module_id: SRC-TST-1736 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_temporal_pattern
# [INVARIANTS] TemporalPattern.hourly_patterns is dict[int,float]; learn sets key=value
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_temporal_pattern.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.anomaly.temporal_pattern import TemporalPattern


class TestTemporalPatternInstantiation:
    def test_default_hourly_patterns_empty(self):
        obj = TemporalPattern()
        assert obj.hourly_patterns == {}

    def test_custom_hourly_patterns(self):
        initial = {0: 10.0, 12: 50.0}
        obj = TemporalPattern(hourly_patterns=initial)
        assert obj.hourly_patterns == initial

    def test_hourly_patterns_is_dict_type(self):
        obj = TemporalPattern()
        assert isinstance(obj.hourly_patterns, dict)


class TestTemporalPatternLearn:
    def test_learn_new_hour(self):
        obj = TemporalPattern()
        obj.learn(3, 10.5)
        assert obj.hourly_patterns[3] == 10.5

    def test_learn_overwrites_existing_hour(self):
        obj = TemporalPattern()
        obj.learn(3, 10.5)
        obj.learn(3, 20.0)
        assert obj.hourly_patterns[3] == 20.0

    def test_learn_multiple_hours(self):
        obj = TemporalPattern()
        obj.learn(0, 5.0)
        obj.learn(12, 50.0)
        obj.learn(23, 8.0)
        assert len(obj.hourly_patterns) == 3
        assert obj.hourly_patterns[12] == 50.0

    def test_learn_hour_zero(self):
        obj = TemporalPattern()
        obj.learn(0, 1.0)
        assert obj.hourly_patterns[0] == 1.0

    def test_learn_hour_23(self):
        obj = TemporalPattern()
        obj.learn(23, 99.0)
        assert obj.hourly_patterns[23] == 99.0

    def test_learn_negative_baseline(self):
        obj = TemporalPattern()
        obj.learn(5, -1.0)
        assert obj.hourly_patterns[5] == -1.0

    def test_learn_zero_baseline(self):
        obj = TemporalPattern()
        obj.learn(10, 0.0)
        assert obj.hourly_patterns[10] == 0.0
