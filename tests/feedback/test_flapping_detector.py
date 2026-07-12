# [A_test] module_id: SRC-TST-1009 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_flapping_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_flapping_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.flapping_detector import (
    AlertState,
    FlappingDetector,
    FlappingSeverity,
)


class TestAlertState:
    def test_enum_values(self):
        assert AlertState.ACTIVE.value == "ACTIVE"
        assert AlertState.CLEAR.value == "CLEAR"


class TestFlappingSeverity:
    def test_enum_values(self):
        assert FlappingSeverity.NONE.value == "NONE"
        assert FlappingSeverity.WARNING.value == "WARNING"
        assert FlappingSeverity.FLAPPING.value == "FLAPPING"
        assert FlappingSeverity.SUPPRESSED.value == "SUPPRESSED"


class TestFlappingDetectorInstantiation:
    def test_default_instantiation(self):
        detector = FlappingDetector()
        assert detector.max_state_changes_per_hour == 12
        assert detector.suppression_duration == 900.0
        assert detector.min_active_duration == 30.0
        assert detector.alert_states == {}
        assert detector.suppressed_alerts == {}
        assert detector.flapping_events == []

    def test_custom_parameters(self):
        detector = FlappingDetector(max_state_changes_per_hour=6, suppression_duration=600.0)
        assert detector.max_state_changes_per_hour == 6
        assert detector.suppression_duration == 600.0

    def test_is_dataclass(self):
        detector = FlappingDetector()
        assert hasattr(detector, "__dataclass_fields__")


class TestRecordStateChange:
    def test_first_state_change(self):
        detector = FlappingDetector()
        result = detector.record_state_change("alert_1", AlertState.ACTIVE)
        assert result["alert_id"] == "alert_1"
        assert result["severity"] == FlappingSeverity.NONE.value

    def test_single_toggle_no_flapping(self):
        detector = FlappingDetector()
        detector.record_state_change("alert_1", AlertState.ACTIVE)
        result = detector.record_state_change("alert_1", AlertState.CLEAR)
        assert result["flapping"] is False

    def test_returns_alert_id(self):
        detector = FlappingDetector()
        result = detector.record_state_change("my_alert", AlertState.ACTIVE)
        assert result["alert_id"] == "my_alert"

    def test_returns_changes_per_hour(self):
        detector = FlappingDetector()
        result = detector.record_state_change("alert_1", AlertState.ACTIVE)
        assert "changes_per_hour" in result


class TestIsSuppressed:
    def test_not_suppressed_initially(self):
        detector = FlappingDetector()
        assert detector.is_suppressed("alert_1") is False

    def test_suppressed_after_flapping(self):
        detector = FlappingDetector(max_state_changes_per_hour=4)
        for _ in range(6):
            detector.record_state_change("alert_1", AlertState.ACTIVE)
            detector.record_state_change("alert_1", AlertState.CLEAR)
        assert detector.is_suppressed("alert_1") is True


class TestGetFlappingStats:
    def test_empty_stats(self):
        detector = FlappingDetector()
        stats = detector.get_flapping_stats()
        assert stats["suppressed_count"] == 0
        assert stats["total_flapping_events"] == 0
        assert stats["recent_flapping"] == []

    def test_stats_after_flapping(self):
        detector = FlappingDetector(max_state_changes_per_hour=4)
        for _ in range(6):
            detector.record_state_change("alert_1", AlertState.ACTIVE)
            detector.record_state_change("alert_1", AlertState.CLEAR)
        stats = detector.get_flapping_stats()
        assert stats["total_flapping_events"] >= 1


class TestOverallAlertStability:
    def test_empty_returns_one(self):
        detector = FlappingDetector()
        assert detector.overall_alert_stability() == 1.0

    def test_stable_alerts_high_score(self):
        detector = FlappingDetector()
        detector.record_state_change("alert_1", AlertState.ACTIVE)
        stability = detector.overall_alert_stability()
        assert stability == 1.0

    def test_flapping_reduces_stability(self):
        detector = FlappingDetector(max_state_changes_per_hour=4)
        for _ in range(6):
            detector.record_state_change("alert_1", AlertState.ACTIVE)
            detector.record_state_change("alert_1", AlertState.CLEAR)
        stability = detector.overall_alert_stability()
        assert stability < 1.0
