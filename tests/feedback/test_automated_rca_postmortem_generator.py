# [A_test] module_id: SRC-TST-0385 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_automated_rca_postmortem_generator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.automated_rca_postmortem_generator
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_automated_rca_postmortem_generator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.automated_rca_postmortem_generator import (
    AutomatedRCAPostmortemGenerator,
    IncidentSeverity,
)


class TestIncidentSeverity:
    def test_enum_values(self):
        assert IncidentSeverity.P0_CRITICAL.value == "P0"
        assert IncidentSeverity.P1_HIGH.value == "P1"
        assert IncidentSeverity.P2_MEDIUM.value == "P2"
        assert IncidentSeverity.P3_LOW.value == "P3"


class TestAutomatedRCAPostmortemGenerator:
    def test_instantiation_defaults(self):
        gen = AutomatedRCAPostmortemGenerator()
        assert gen.max_timeline_events == 100
        assert gen.root_cause_depth == 5
        assert gen.incident_timelines == {}
        assert gen.generated_postmortems == []

    def test_start_incident(self):
        gen = AutomatedRCAPostmortemGenerator()
        gen.start_incident("INC-001", IncidentSeverity.P1_HIGH, "DB outage", ["db-primary"])
        assert "INC-001" in gen.incident_timelines
        assert len(gen.incident_timelines["INC-001"]) == 1
        assert gen.incident_timelines["INC-001"][0]["event"] == "INCIDENT_START"
        assert gen.incident_timelines["INC-001"][0]["severity"] == "P1"

    def test_record_event(self):
        gen = AutomatedRCAPostmortemGenerator()
        gen.start_incident("INC-001", IncidentSeverity.P0_CRITICAL, "Crash", ["core"])
        gen.record_event("INC-001", "ANOMALY_DETECTED", "CPU spike detected")
        assert len(gen.incident_timelines["INC-001"]) == 2
        assert gen.incident_timelines["INC-001"][1]["event"] == "ANOMALY_DETECTED"

    def test_record_event_unknown_incident(self):
        gen = AutomatedRCAPostmortemGenerator()
        gen.record_event("INC-999", "ANOMALY_DETECTED", "Should be ignored")
        assert "INC-999" not in gen.incident_timelines

    def test_close_incident_full_flow(self):
        gen = AutomatedRCAPostmortemGenerator()
        gen.start_incident("INC-001", IncidentSeverity.P1_HIGH, "DB latency", ["db-primary"])
        gen.record_event("INC-001", "ANOMALY_DETECTED", "High latency")
        gen.record_event("INC-001", "DIAGNOSIS_COMPLETE", "Connection pool exhausted")
        gen.record_event("INC-001", "MITIGATION_APPLIED", "Restarted pool")
        result = gen.close_incident("INC-001", "Pool restarted", 120.0)
        assert result is not None
        assert result["incident_id"] == "INC-001"
        assert result["resolution"] == "Pool restarted"
        assert result["total_recovery_time_s"] == 120.0
        assert len(result["root_cause_chain"]) > 0
        assert len(result["action_items"]) > 0
        assert result["detection_latency_s"] >= 0

    def test_close_incident_unknown_returns_none(self):
        gen = AutomatedRCAPostmortemGenerator()
        result = gen.close_incident("INC-404", "N/A", 0.0)
        assert result is None

    def test_get_postmortem_summary(self):
        gen = AutomatedRCAPostmortemGenerator()
        gen.start_incident("INC-001", IncidentSeverity.P2_MEDIUM, "Slow query", ["api"])
        gen.record_event("INC-001", "ANOMALY_DETECTED", "Latency spike")
        gen.close_incident("INC-001", "Index added", 60.0)
        summary = gen.get_postmortem_summary("INC-001")
        assert summary is not None
        assert summary["title"] == "Slow query"
        assert summary["severity"] == "P2"
        assert summary["action_items_count"] > 0

    def test_get_postmortem_summary_not_found(self):
        gen = AutomatedRCAPostmortemGenerator()
        assert gen.get_postmortem_summary("INC-404") is None

    def test_recurring_pattern_analysis(self):
        gen = AutomatedRCAPostmortemGenerator()
        for i in range(3):
            gen.start_incident(f"INC-{i:03d}", IncidentSeverity.P1_HIGH, "DB timeout", ["db"])
            gen.record_event(f"INC-{i:03d}", "ANOMALY_DETECTED", "Timeout")
            gen.close_incident(f"INC-{i:03d}", "Restarted", 30.0)
        patterns = gen.recurring_pattern_analysis()
        assert len(patterns) == 1
        assert patterns[0]["occurrence_count"] == 3
        assert patterns[0]["recurring"] is True

    def test_recurring_pattern_no_recurring(self):
        gen = AutomatedRCAPostmortemGenerator()
        gen.start_incident("INC-001", IncidentSeverity.P1_HIGH, "DB timeout", ["db"])
        gen.close_incident("INC-001", "Fixed", 10.0)
        gen.start_incident("INC-002", IncidentSeverity.P2_MEDIUM, "API error", ["api"])
        gen.close_incident("INC-002", "Fixed", 5.0)
        patterns = gen.recurring_pattern_analysis()
        assert len(patterns) == 0

    def test_max_timeline_events_truncation(self):
        gen = AutomatedRCAPostmortemGenerator(max_timeline_events=5)
        gen.start_incident("INC-001", IncidentSeverity.P0_CRITICAL, "Overflow", ["sys"])
        for i in range(10):
            gen.record_event("INC-001", f"EVENT_{i}", f"Event {i}")
        assert len(gen.incident_timelines["INC-001"]) <= 5

    def test_close_incident_without_detection_events(self):
        gen = AutomatedRCAPostmortemGenerator()
        gen.start_incident("INC-001", IncidentSeverity.P3_LOW, "Minor", ["test"])
        gen.record_event("INC-001", "DIAGNOSIS_COMPLETE", "Found issue")
        result = gen.close_incident("INC-001", "Fixed", 5.0)
        assert result is not None
        assert result["detection_latency_s"] == 0
        has_improve_action = any("Improve anomaly detection" in a["action"] for a in result["action_items"])
        assert has_improve_action
