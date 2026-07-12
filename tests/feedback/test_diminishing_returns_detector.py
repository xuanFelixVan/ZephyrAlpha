# [A_test] module_id: SRC-TST-0753 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_diminishing_returns_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_diminishing_returns_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.diminishing_returns_detector import (
    DiminishingReturnsDetector,
    GuardValueRecord,
)


class TestGuardValueRecord:
    def test_instantiation(self):
        rec = GuardValueRecord(
            guard_id="g1",
            mttr_improvement=0.5,
            reliability_improvement=0.3,
            false_positive_rate=0.1,
            added_at=1000.0,
        )
        assert rec.guard_id == "g1"
        assert rec.mttr_improvement == 0.5


class TestDiminishingReturnsDetectorInstantiation:
    def test_default_instantiation(self):
        detector = DiminishingReturnsDetector()
        assert detector.guard_records == []
        assert detector.marginal_value_threshold == 0.01
        assert detector.recent_window == 8
        assert detector.inflation_warning_guard_count == 100

    def test_custom_parameters(self):
        detector = DiminishingReturnsDetector(
            marginal_value_threshold=0.05,
            recent_window=5,
            inflation_warning_guard_count=50,
        )
        assert detector.marginal_value_threshold == 0.05


class TestRegisterGuardValue:
    def test_register_appends_record(self):
        detector = DiminishingReturnsDetector()
        detector.register_guard_value("g1", 0.5, 0.3, 0.1, 1000.0)
        assert len(detector.guard_records) == 1
        assert detector.guard_records[0].guard_id == "g1"

    def test_register_multiple_records(self):
        detector = DiminishingReturnsDetector()
        detector.register_guard_value("g1", 0.5, 0.3, 0.1, 1000.0)
        detector.register_guard_value("g2", 0.4, 0.2, 0.05, 2000.0)
        assert len(detector.guard_records) == 2


class TestAnalyzeDiminishingReturns:
    def test_insufficient_data(self):
        detector = DiminishingReturnsDetector(recent_window=8)
        for i in range(5):
            detector.register_guard_value(f"g{i}", 0.5, 0.3, 0.1, float(i))
        result = detector.analyze_diminishing_returns()
        assert result["status"] == "insufficient_data"
        assert result["total_guards"] == 5

    def test_healthy_returns(self):
        detector = DiminishingReturnsDetector(recent_window=3, marginal_value_threshold=0.01)
        for i in range(12):
            detector.register_guard_value(f"g{i}", 0.5, 0.3, 0.1, float(i))
        result = detector.analyze_diminishing_returns()
        assert result["is_diminishing"] is False
        assert result["recommendation"] == "CONTINUE_monitor"

    def test_diminishing_returns(self):
        detector = DiminishingReturnsDetector(recent_window=3, marginal_value_threshold=0.01)
        for i in range(9):
            detector.register_guard_value(f"g{i}", 0.5, 0.3, 0.1, float(i))
        for i in range(3):
            detector.register_guard_value(f"late_g{i}", 0.001, 0.001, 0.9, float(9 + i))
        result = detector.analyze_diminishing_returns()
        assert result["is_diminishing"] is True
        assert result["recommendation"] == "STOP_ADDING_GUARDS"

    def test_inflation_risk(self):
        detector = DiminishingReturnsDetector(
            recent_window=3,
            inflation_warning_guard_count=10,
            marginal_value_threshold=0.01,
        )
        for i in range(15):
            detector.register_guard_value(f"g{i}", 0.5, 0.3, 0.1, float(i))
        result = detector.analyze_diminishing_returns()
        assert result["inflation_risk"] is True

    def test_no_inflation_risk(self):
        detector = DiminishingReturnsDetector(
            recent_window=3,
            inflation_warning_guard_count=100,
            marginal_value_threshold=0.01,
        )
        for i in range(12):
            detector.register_guard_value(f"g{i}", 0.5, 0.3, 0.1, float(i))
        result = detector.analyze_diminishing_returns()
        assert result["inflation_risk"] is False

    def test_caution_diminishing(self):
        detector = DiminishingReturnsDetector(recent_window=3, marginal_value_threshold=0.01)
        for i in range(9):
            detector.register_guard_value(f"g{i}", 1.0, 1.0, 0.1, float(i))
        for i in range(3):
            detector.register_guard_value(f"late_g{i}", 0.2, 0.2, 0.1, float(9 + i))
        result = detector.analyze_diminishing_returns()
        assert result["recommendation"] in ("CAUTION_diminishing", "CONTINUE_monitor", "STOP_ADDING_GUARDS")
