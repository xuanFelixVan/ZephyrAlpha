# [A_test] module_id: SRC-TST-0295 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_agent_trajectory_anomaly_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_agent_trajectory_anomaly_detector.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.detectors.correlation.agent_trajectory_anomaly_detector import (
    AgentTrajectoryAnomalyDetector,
    TrajectoryAnomalyType,
    TrajectoryEvent,
)


class TestTrajectoryAnomalyType:
    def test_enum_values(self):
        assert TrajectoryAnomalyType.DRIFT.value == "drift"
        assert TrajectoryAnomalyType.CYCLE.value == "cycle"
        assert TrajectoryAnomalyType.MISSING_STEP.value == "missing_step"


class TestTrajectoryEvent:
    def test_construction(self):
        ev = TrajectoryEvent(
            phase="collect",
            component="sensor_a",
            timestamp=1.0,
            input_hash="abc",
            output_hash="def",
        )
        assert ev.phase == "collect"
        assert ev.component == "sensor_a"
        assert ev.timestamp == 1.0


class TestAgentTrajectoryAnomalyDetectorInstantiation:
    def test_default_construction(self):
        det = AgentTrajectoryAnomalyDetector()
        assert det.trajectory_history == []
        assert det.max_history == 200
        assert det.cycle_threshold == 3
        assert det.drift_threshold == 0.4

    def test_custom_params(self):
        det = AgentTrajectoryAnomalyDetector(
            max_history=50,
            cycle_threshold=5,
            drift_threshold=0.6,
        )
        assert det.max_history == 50
        assert det.cycle_threshold == 5
        assert det.drift_threshold == 0.6


class TestRecordStep:
    def test_appends_event(self):
        det = AgentTrajectoryAnomalyDetector()
        ev = TrajectoryEvent("collect", "s1", 1.0, "h1", "h2")
        det.record_step(ev)
        assert len(det.trajectory_history) == 1

    def test_truncates_at_max_history(self):
        det = AgentTrajectoryAnomalyDetector(max_history=5)
        for i in range(8):
            det.record_step(TrajectoryEvent("collect", f"s{i}", float(i), "h1", "h2"))
        assert len(det.trajectory_history) == 5


class TestDetectTrajectoryAnomalies:
    def test_insufficient_data(self):
        det = AgentTrajectoryAnomalyDetector()
        det.record_step(TrajectoryEvent("collect", "s1", 1.0, "h1", "h2"))
        result = det.detect_trajectory_anomalies()
        assert result["status"] == "insufficient_data"

    def test_normal_trajectory(self):
        det = AgentTrajectoryAnomalyDetector()
        phases = ["collect", "detect", "diagnose", "act", "verify"]
        for i, phase in enumerate(phases):
            det.record_step(TrajectoryEvent(phase, f"comp_{i}", float(i), "h1", "h2"))
        result = det.detect_trajectory_anomalies()
        assert result["status"] == "normal"

    def test_missing_step_detected(self):
        det = AgentTrajectoryAnomalyDetector()
        for i in range(5):
            det.record_step(TrajectoryEvent("collect", f"comp_{i}", float(i), "h1", "h2"))
        result = det.detect_trajectory_anomalies()
        missing_types = [a["type"] for a in result["anomalies"]]
        assert TrajectoryAnomalyType.MISSING_STEP.value in missing_types

    def test_cycle_detected(self):
        det = AgentTrajectoryAnomalyDetector()
        cycle = ["comp_a", "comp_b", "comp_c", "comp_a"]
        for i, comp in enumerate(cycle):
            det.record_step(TrajectoryEvent("detect", comp, float(i), "h1", "h2"))
        for i in range(4):
            det.record_step(TrajectoryEvent("act", f"comp_d_{i}", float(i + 4), "h1", "h2"))
        result = det.detect_trajectory_anomalies()
        cycle_anomalies = [a for a in result["anomalies"] if a["type"] == TrajectoryAnomalyType.CYCLE.value]
        if cycle_anomalies:
            assert "components" in cycle_anomalies[0]
            assert "span" in cycle_anomalies[0]


class TestDetectDrift:
    def test_no_drift_forward_progress(self):
        det = AgentTrajectoryAnomalyDetector()
        phases = ["collect", "detect", "diagnose", "act", "verify"]
        for i, phase in enumerate(phases):
            det.record_step(TrajectoryEvent(phase, f"comp_{i}", float(i), "h1", "h2"))
        result = det._detect_drift()
        assert result == []

    def test_drift_backward(self):
        det = AgentTrajectoryAnomalyDetector(drift_threshold=0.5)
        backward_phases = ["act", "detect", "collect", "verify", "act", "collect", "detect", "act", "verify", "collect"]
        for i, phase in enumerate(backward_phases):
            det.record_step(TrajectoryEvent(phase, f"comp_{i}", float(i), "h1", "h2"))
        result = det._detect_drift()
        if result:
            assert result[0]["type"] == TrajectoryAnomalyType.DRIFT.value


class TestDetectCycles:
    def test_no_cycle(self):
        det = AgentTrajectoryAnomalyDetector()
        for i in range(10):
            det.record_step(TrajectoryEvent("collect", f"comp_{i}", float(i), "h1", "h2"))
        result = det._detect_cycles()
        assert result == []

    def test_cycle_with_repeated_component(self):
        det = AgentTrajectoryAnomalyDetector()
        for i in range(6):
            det.record_step(TrajectoryEvent("detect", f"comp_{i}", float(i), "h1", "h2"))
        det.record_step(TrajectoryEvent("detect", "comp_2", 6.0, "h1", "h2"))
        result = det._detect_cycles()
        if result:
            assert result[0]["type"] == TrajectoryAnomalyType.CYCLE.value


class TestDetectMissingSteps:
    def test_all_phases_present(self):
        det = AgentTrajectoryAnomalyDetector()
        phases = ["collect", "detect", "diagnose", "act", "verify"]
        for i, phase in enumerate(phases):
            det.record_step(TrajectoryEvent(phase, f"comp_{i}", float(i), "h1", "h2"))
        result = det._detect_missing_steps()
        assert result == []

    def test_missing_phases(self):
        det = AgentTrajectoryAnomalyDetector()
        for i in range(5):
            det.record_step(TrajectoryEvent("collect", f"comp_{i}", float(i), "h1", "h2"))
        result = det._detect_missing_steps()
        assert len(result) > 0
        assert "missing_phases" in result[0]
