# [A_test] module_id: SRC-TST-1097 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_heisenbug_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_heisenbug_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.anomaly.heisenbug_detector import (
    HeisenbugDetector,
    ObservationMode,
)


class TestObservationMode:
    def test_passive_value(self):
        assert ObservationMode.PASSIVE.value == "PASSIVE"

    def test_active_value(self):
        assert ObservationMode.ACTIVE.value == "ACTIVE"


class TestHeisenbugDetector:
    def test_default_construction(self):
        det = HeisenbugDetector()
        assert det.passive_anomaly_rate == 0.0
        assert det.active_anomaly_rate == 0.0
        assert det.passive_samples == 0
        assert det.active_samples == 0
        assert det.heisenbug_threshold == 0.5
        assert det.observation_timeline == []

    def test_custom_construction(self):
        det = HeisenbugDetector(heisenbug_threshold=0.3)
        assert det.heisenbug_threshold == 0.3

    def test_record_passive_anomaly(self):
        det = HeisenbugDetector()
        entry = det.record(True, ObservationMode.PASSIVE)
        assert entry["mode"] == "PASSIVE"
        assert entry["anomaly"] is True
        assert det.passive_samples == 1
        assert det.passive_anomaly_rate == 1.0

    def test_record_active_no_anomaly(self):
        det = HeisenbugDetector()
        det.record(False, ObservationMode.ACTIVE)
        assert det.active_samples == 1
        assert det.active_anomaly_rate == 0.0

    def test_record_trims_timeline(self):
        det = HeisenbugDetector()
        for i in range(1100):
            det.record(i % 2 == 0, ObservationMode.PASSIVE)
        assert len(det.observation_timeline) <= 1000

    def test_detect_heisenbug_insufficient_samples(self):
        det = HeisenbugDetector()
        for _ in range(5):
            det.record(True, ObservationMode.PASSIVE)
        result = det.detect_heisenbug()
        assert result["heisenbug_detected"] is False
        assert result["confidence"] == 0.0
        assert result["reason"] == "insufficient passive samples"

    def test_detect_heisenbug_no_passive_anomalies(self):
        det = HeisenbugDetector()
        for _ in range(15):
            det.record(False, ObservationMode.PASSIVE)
        result = det.detect_heisenbug()
        assert result["heisenbug_detected"] is False
        assert result["reason"] == "no passive anomalies"

    def test_detect_heisenbug_detected(self):
        det = HeisenbugDetector()
        for _ in range(20):
            det.record(True, ObservationMode.PASSIVE)
        for _ in range(20):
            det.record(False, ObservationMode.ACTIVE)
        result = det.detect_heisenbug()
        assert result["heisenbug_detected"] is True
        assert result["confidence"] > 0.0
        assert result["recommendation"] == "shadow_replay_without_instrumentation"

    def test_detect_heisenbug_not_detected(self):
        det = HeisenbugDetector()
        for _ in range(20):
            det.record(True, ObservationMode.PASSIVE)
        for _ in range(20):
            det.record(True, ObservationMode.ACTIVE)
        result = det.detect_heisenbug()
        assert result["heisenbug_detected"] is False
        assert result["recommendation"] == "continue_monitoring"

    def test_detect_heisenbug_confidence_capped(self):
        det = HeisenbugDetector()
        for _ in range(50):
            det.record(True, ObservationMode.PASSIVE)
        for _ in range(50):
            det.record(False, ObservationMode.ACTIVE)
        result = det.detect_heisenbug()
        assert result["confidence"] <= 0.95

    def test_reset_observation_window(self):
        det = HeisenbugDetector()
        for _ in range(20):
            det.record(True, ObservationMode.PASSIVE)
        for _ in range(20):
            det.record(True, ObservationMode.ACTIVE)
        det.reset_observation_window()
        assert det.passive_anomaly_rate == 0.0
        assert det.active_anomaly_rate == 0.0
        assert det.passive_samples == 0
        assert det.active_samples == 0

    def test_detect_heisenbug_rate_ratio_computed(self):
        det = HeisenbugDetector()
        for _ in range(20):
            det.record(True, ObservationMode.PASSIVE)
        for _ in range(10):
            det.record(True, ObservationMode.ACTIVE)
        result = det.detect_heisenbug()
        assert "rate_ratio" in result
        assert "passive_rate" in result
        assert "active_rate" in result
