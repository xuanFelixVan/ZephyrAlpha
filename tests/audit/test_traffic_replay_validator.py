# [A_test] module_id: SRC-TST-1761 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_traffic_replay_validator
# [INVARIANTS] deviation_rate = (deviations+errors)/replay_count*100; should_abort when rate>threshold
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_traffic_replay_validator.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.traffic_replay_validator import (
    ReplaySession,
    ReplayVerdict,
    TrafficReplayValidator,
)


class TestReplayVerdict:
    def test_enum_values(self):
        assert ReplayVerdict.MATCH == "MATCH"
        assert ReplayVerdict.DEVIATION == "DEVIATION"
        assert ReplayVerdict.ERROR == "ERROR"


class TestReplaySession:
    def test_instantiation(self):
        session = ReplaySession(session_id="s1", source_endpoint="/api/v1")
        assert session.session_id == "s1"
        assert session.source_endpoint == "/api/v1"
        assert session.replay_count == 0
        assert session.matches == 0
        assert session.deviations == 0
        assert session.errors == 0

    def test_timestamp_auto_set(self):
        session = ReplaySession(session_id="s1", source_endpoint="/api")
        assert session.timestamp > 0


class TestTrafficReplayValidatorInstantiation:
    def test_default_params(self):
        obj = TrafficReplayValidator()
        assert obj.sessions == []
        assert obj.deviation_threshold_pct == 5.0

    def test_custom_threshold(self):
        obj = TrafficReplayValidator(deviation_threshold_pct=10.0)
        assert obj.deviation_threshold_pct == 10.0


class TestTrafficReplayValidatorStartSession:
    def test_start_session_returns_session(self):
        obj = TrafficReplayValidator()
        session = obj.start_session("s1", "/api/v1")
        assert isinstance(session, ReplaySession)
        assert session.session_id == "s1"
        assert session.source_endpoint == "/api/v1"

    def test_start_session_appends_to_sessions(self):
        obj = TrafficReplayValidator()
        obj.start_session("s1", "/api/v1")
        assert len(obj.sessions) == 1

    def test_start_multiple_sessions(self):
        obj = TrafficReplayValidator()
        obj.start_session("s1", "/api/v1")
        obj.start_session("s2", "/api/v2")
        assert len(obj.sessions) == 2


class TestTrafficReplayValidatorRecordResult:
    def test_record_match(self):
        obj = TrafficReplayValidator()
        obj.start_session("s1", "/api")
        obj.record_result("s1", ReplayVerdict.MATCH)
        assert obj.sessions[0].matches == 1
        assert obj.sessions[0].replay_count == 1

    def test_record_deviation(self):
        obj = TrafficReplayValidator()
        obj.start_session("s1", "/api")
        obj.record_result("s1", ReplayVerdict.DEVIATION)
        assert obj.sessions[0].deviations == 1

    def test_record_error(self):
        obj = TrafficReplayValidator()
        obj.start_session("s1", "/api")
        obj.record_result("s1", ReplayVerdict.ERROR)
        assert obj.sessions[0].errors == 1

    def test_record_multiple_results(self):
        obj = TrafficReplayValidator()
        obj.start_session("s1", "/api")
        obj.record_result("s1", ReplayVerdict.MATCH)
        obj.record_result("s1", ReplayVerdict.MATCH)
        obj.record_result("s1", ReplayVerdict.DEVIATION)
        assert obj.sessions[0].replay_count == 3
        assert obj.sessions[0].matches == 2
        assert obj.sessions[0].deviations == 1

    def test_record_nonexistent_session_no_error(self):
        obj = TrafficReplayValidator()
        obj.record_result("nonexistent", ReplayVerdict.MATCH)


class TestTrafficReplayValidatorDeviationRate:
    def test_no_replays_zero_rate(self):
        obj = TrafficReplayValidator()
        obj.start_session("s1", "/api")
        assert obj.deviation_rate("s1") == 0.0

    def test_all_matches_zero_rate(self):
        obj = TrafficReplayValidator()
        obj.start_session("s1", "/api")
        obj.record_result("s1", ReplayVerdict.MATCH)
        obj.record_result("s1", ReplayVerdict.MATCH)
        assert obj.deviation_rate("s1") == 0.0

    def test_mixed_results(self):
        obj = TrafficReplayValidator()
        obj.start_session("s1", "/api")
        for _ in range(8):
            obj.record_result("s1", ReplayVerdict.MATCH)
        obj.record_result("s1", ReplayVerdict.DEVIATION)
        obj.record_result("s1", ReplayVerdict.ERROR)
        rate = obj.deviation_rate("s1")
        assert rate == 20.0

    def test_nonexistent_session_zero_rate(self):
        obj = TrafficReplayValidator()
        assert obj.deviation_rate("nonexistent") == 0.0


class TestTrafficReplayValidatorShouldAbort:
    def test_should_not_abort_low_deviation(self):
        obj = TrafficReplayValidator(deviation_threshold_pct=5.0)
        obj.start_session("s1", "/api")
        for _ in range(100):
            obj.record_result("s1", ReplayVerdict.MATCH)
        assert obj.should_abort("s1") is False

    def test_should_abort_high_deviation(self):
        obj = TrafficReplayValidator(deviation_threshold_pct=5.0)
        obj.start_session("s1", "/api")
        for _ in range(90):
            obj.record_result("s1", ReplayVerdict.MATCH)
        for _ in range(10):
            obj.record_result("s1", ReplayVerdict.DEVIATION)
        assert obj.should_abort("s1") is True

    def test_should_not_abort_at_threshold_boundary(self):
        obj = TrafficReplayValidator(deviation_threshold_pct=10.0)
        obj.start_session("s1", "/api")
        for _ in range(9):
            obj.record_result("s1", ReplayVerdict.MATCH)
        obj.record_result("s1", ReplayVerdict.DEVIATION)
        assert obj.should_abort("s1") is False

    def test_nonexistent_session_no_abort(self):
        obj = TrafficReplayValidator()
        assert obj.should_abort("nonexistent") is False
