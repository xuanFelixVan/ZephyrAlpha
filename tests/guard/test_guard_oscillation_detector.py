# [A_test] module_id: SRC-TST-1086 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_guard_oscillation_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_guard_oscillation_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.guard.guard_oscillation_detector import (
    GuardOscillationDetector,
    GuardStateChange,
)


class TestGuardStateChange:
    def test_creation(self):
        sc = GuardStateChange(guard_id="G1", from_state="OFF", to_state="ON", timestamp=0.0)
        assert sc.guard_id == "G1"
        assert sc.from_state == "OFF"
        assert sc.to_state == "ON"
        assert sc.timestamp == 0.0


class TestGuardOscillationDetector:
    def test_default_construction(self):
        det = GuardOscillationDetector()
        assert det.state_changes == []
        assert det.max_changes == 200
        assert det.oscillation_threshold == 6.0
        assert det.analysis_window == 3600.0

    def test_custom_construction(self):
        det = GuardOscillationDetector(
            max_changes=50,
            oscillation_threshold=3.0,
            analysis_window=1800.0,
        )
        assert det.max_changes == 50
        assert det.oscillation_threshold == 3.0
        assert det.analysis_window == 1800.0

    def test_record_state_change_appends(self):
        det = GuardOscillationDetector()
        det.record_state_change("G1", "OFF", "ON")
        assert len(det.state_changes) == 1
        assert det.state_changes[0].guard_id == "G1"
        assert det.state_changes[0].from_state == "OFF"
        assert det.state_changes[0].to_state == "ON"

    def test_record_state_change_trims_history(self):
        det = GuardOscillationDetector(max_changes=5)
        for i in range(10):
            det.record_state_change("G1", "OFF", "ON")
        assert len(det.state_changes) == 5

    def test_detect_oscillations_no_oscillation(self):
        det = GuardOscillationDetector(oscillation_threshold=6.0, analysis_window=3600.0)
        for _ in range(3):
            det.record_state_change("G1", "OFF", "ON")
        result = det.detect_oscillations()
        assert result["oscillating_guards"] == []
        assert "G1" not in result["details"]

    def test_detect_oscillations_with_oscillation(self):
        det = GuardOscillationDetector(oscillation_threshold=6.0, analysis_window=3600.0)
        for _ in range(7):
            det.record_state_change("G1", "OFF", "ON")
            det.record_state_change("G1", "ON", "OFF")
        result = det.detect_oscillations()
        assert "G1" in result["oscillating_guards"]
        assert result["details"]["G1"]["total_swings"] >= 6
        assert result["details"]["G1"]["pattern"] in ("OFF <-> ON", "ON <-> OFF")

    def test_detect_oscillations_severity_critical(self):
        det = GuardOscillationDetector(oscillation_threshold=6.0, analysis_window=3600.0)
        for _ in range(21):
            det.record_state_change("G1", "OFF", "ON")
            det.record_state_change("G1", "ON", "OFF")
        result = det.detect_oscillations()
        assert result["details"]["G1"]["severity"] == "critical"

    def test_detect_oscillations_severity_high(self):
        det = GuardOscillationDetector(oscillation_threshold=6.0, analysis_window=3600.0)
        for _ in range(13):
            det.record_state_change("G1", "OFF", "ON")
            det.record_state_change("G1", "ON", "OFF")
        result = det.detect_oscillations()
        assert result["details"]["G1"]["severity"] == "high"

    def test_detect_oscillations_severity_medium(self):
        det = GuardOscillationDetector(oscillation_threshold=6.0, analysis_window=3600.0)
        for _ in range(7):
            det.record_state_change("G1", "OFF", "ON")
            det.record_state_change("G1", "ON", "OFF")
        result = det.detect_oscillations()
        assert result["details"]["G1"]["severity"] == "medium"

    def test_detect_oscillations_empty(self):
        det = GuardOscillationDetector()
        result = det.detect_oscillations()
        assert result["oscillating_guards"] == []
        assert result["total_guards_monitored"] == 0

    def test_detect_oscillations_multiple_guards(self):
        det = GuardOscillationDetector(oscillation_threshold=6.0, analysis_window=3600.0)
        for _ in range(7):
            det.record_state_change("G1", "OFF", "ON")
            det.record_state_change("G1", "ON", "OFF")
        det.record_state_change("G2", "OFF", "ON")
        result = det.detect_oscillations()
        assert "G1" in result["oscillating_guards"]
        assert "G2" not in result["oscillating_guards"]
        assert result["total_guards_monitored"] == 2

    def test_detect_oscillations_frequency_per_hour(self):
        det = GuardOscillationDetector(oscillation_threshold=6.0, analysis_window=3600.0)
        for _ in range(7):
            det.record_state_change("G1", "OFF", "ON")
            det.record_state_change("G1", "ON", "OFF")
        result = det.detect_oscillations()
        assert result["details"]["G1"]["frequency_per_hour"] >= 6.0
