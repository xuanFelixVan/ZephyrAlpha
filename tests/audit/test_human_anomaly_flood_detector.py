# [A_test] module_id: SRC-TST-1104 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_human_anomaly_flood_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.human_anomaly_flood_detector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_human_anomaly_flood_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.human_anomaly_flood_detector import (
    FloodLevel,
    HumanAnomalyFloodDetector,
)


class TestHumanAnomalyFloodDetectorInstantiation:
    def test_default_instantiation(self):
        det = HumanAnomalyFloodDetector()
        assert det.max_anomalies_per_human_per_hour == 10
        assert det.auto_triage_threshold == 20
        assert det.flood_suppression_duration == 1800.0
        assert det.human_exposure == {}
        assert det.flood_events == []
        assert det.auto_triage_active is False

    def test_custom_parameters(self):
        det = HumanAnomalyFloodDetector(
            max_anomalies_per_human_per_hour=5,
            auto_triage_threshold=15,
            flood_suppression_duration=900.0,
        )
        assert det.max_anomalies_per_human_per_hour == 5
        assert det.auto_triage_threshold == 15
        assert det.flood_suppression_duration == 900.0


class TestFloodLevel:
    def test_enum_values(self):
        assert FloodLevel.NORMAL.value == "NORMAL"
        assert FloodLevel.ELEVATED.value == "ELEVATED"
        assert FloodLevel.FLOOD.value == "FLOOD"
        assert FloodLevel.DROWNING.value == "DROWNING"

    def test_enum_is_str(self):
        assert isinstance(FloodLevel.NORMAL, str)


class TestRecordAnomalyExposure:
    def test_single_anomaly_normal_level(self):
        det = HumanAnomalyFloodDetector()
        result = det.record_anomaly_exposure("human1", "anom1", "P2")
        assert result["flood_level"] == "NORMAL"
        assert result["anomalies_per_hour"] == 1
        assert result["auto_triage_active"] is False

    def test_elevated_level(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=10)
        for i in range(6):
            result = det.record_anomaly_exposure("human1", f"anom{i}", "P2")
        assert result["flood_level"] == "ELEVATED"

    def test_flood_level(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=10)
        for i in range(11):
            result = det.record_anomaly_exposure("human1", f"anom{i}", "P2")
        assert result["flood_level"] == "FLOOD"
        assert result["auto_triage_active"] is True

    def test_drowning_level(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=10, auto_triage_threshold=15)
        for i in range(16):
            result = det.record_anomaly_exposure("human1", f"anom{i}", "P2")
        assert result["flood_level"] == "DROWNING"
        assert result["auto_triage_active"] is True

    def test_critical_buried_flag(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=10)
        det.record_anomaly_exposure("human1", "anom0", "P0")
        for i in range(1, 12):
            det.record_anomaly_exposure("human1", f"anom{i}", "P3")
        result = det.record_anomaly_exposure("human1", "anom_last", "P3")
        assert result["critical_buried"] is True

    def test_dismissed_count_tracked(self):
        det = HumanAnomalyFloodDetector()
        det.record_anomaly_exposure("human1", "a1", "P2", dismissed=True)
        det.record_anomaly_exposure("human1", "a2", "P2", dismissed=False)
        result = det.record_anomaly_exposure("human1", "a3", "P2", dismissed=True)
        assert result["dismissed_count"] == 2

    def test_recommendation_per_level(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=10, auto_triage_threshold=15)
        result = det.record_anomaly_exposure("human1", "a0", "P2")
        assert result["recommendation"] == "continue"

    def test_empty_human_id(self):
        det = HumanAnomalyFloodDetector()
        result = det.record_anomaly_exposure("", "anom1", "P2")
        assert result["human_id"] == ""

    def test_flood_events_recorded(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=5)
        for i in range(7):
            det.record_anomaly_exposure("human1", f"anom{i}", "P2")
        assert len(det.flood_events) > 0


class TestGetAutoTriagePlan:
    def test_no_exposure_returns_not_needed(self):
        det = HumanAnomalyFloodDetector()
        result = det.get_auto_triage_plan("human_unknown")
        assert result["triage_needed"] is False

    def test_triage_plan_severity_split(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=5)
        det.record_anomaly_exposure("human1", "a0", "P0")
        det.record_anomaly_exposure("human1", "a1", "P1")
        det.record_anomaly_exposure("human1", "a2", "P2")
        det.record_anomaly_exposure("human1", "a3", "P3")
        result = det.get_auto_triage_plan("human1")
        assert result["total_anomalies"] == 4
        assert len(result["plan"]["surface_directly"]) == 2
        assert len(result["plan"]["aggregate_into_digest"]) == 1
        assert len(result["plan"]["auto_resolve"]) == 1


class TestGetAllHumanStatus:
    def test_no_humans(self):
        det = HumanAnomalyFloodDetector()
        result = det.get_all_human_status()
        assert result == {}

    def test_single_human_status(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=10)
        for i in range(3):
            det.record_anomaly_exposure("human1", f"a{i}", "P2")
        status = det.get_all_human_status()
        assert "human1" in status
        assert status["human1"]["hourly_rate"] == 3
        assert status["human1"]["flooded"] is False


class TestOverallHumanAttentionHealth:
    def test_no_humans_returns_one(self):
        det = HumanAnomalyFloodDetector()
        assert det.overall_human_attention_health() == 1.0

    def test_all_healthy(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=10)
        for i in range(3):
            det.record_anomaly_exposure("human1", f"a{i}", "P2")
        health = det.overall_human_attention_health()
        assert health == 1.0

    def test_flooded_human_reduces_health(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=5)
        for i in range(7):
            det.record_anomaly_exposure("human1", f"a{i}", "P2")
        health = det.overall_human_attention_health()
        assert health < 1.0


class TestResetAutoTriage:
    def test_reset_clears_flag(self):
        det = HumanAnomalyFloodDetector(max_anomalies_per_human_per_hour=5)
        for i in range(7):
            det.record_anomaly_exposure("human1", f"a{i}", "P2")
        assert det.auto_triage_active is True
        det.reset_auto_triage()
        assert det.auto_triage_active is False
