# [A_test] module_id: SRC-TST-0967 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_incident_priority_triage_automator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.actors.incident_priority_triage_automator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_incident_priority_triage_automator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.incident_priority_triage_automator import (
    IncidentPriorityTriageAutomator,
    Severity,
)


class TestIncidentPriorityTriageAutomatorInstantiation:
    def test_creates_with_defaults(self):
        automator = IncidentPriorityTriageAutomator()
        assert automator.auto_page_threshold == Severity.P1
        assert automator.incidents == []


class TestClassify:
    def test_p0_critical_incident(self):
        automator = IncidentPriorityTriageAutomator()
        incident = {"data_sensitive": True, "user_facing": True, "system_critical": True, "blast_radius": 4}
        result = automator.classify(incident)
        assert result == Severity.P0

    def test_p4_low_incident(self):
        automator = IncidentPriorityTriageAutomator()
        incident = {}
        result = automator.classify(incident)
        assert result == Severity.P4

    def test_p2_medium_incident(self):
        automator = IncidentPriorityTriageAutomator()
        incident = {"user_facing": True, "blast_radius": 1}
        result = automator.classify(incident)
        assert result == Severity.P2


class TestTriage:
    def test_triage_returns_action(self):
        automator = IncidentPriorityTriageAutomator()
        result = automator.triage({"data_sensitive": True, "system_critical": True, "blast_radius": 4})
        assert "action" in result
        assert "severity" in result

    def test_triage_pages_critical(self):
        automator = IncidentPriorityTriageAutomator()
        result = automator.triage({"data_sensitive": True, "system_critical": True, "blast_radius": 4})
        assert result["action"] == "PAGE"

    def test_triage_batches_low(self):
        automator = IncidentPriorityTriageAutomator()
        result = automator.triage({})
        assert result["action"] == "BATCH"

    def test_get_counts(self):
        automator = IncidentPriorityTriageAutomator()
        automator.triage({"data_sensitive": True, "system_critical": True, "blast_radius": 4})
        automator.triage({})
        counts = automator.get_counts()
        assert sum(counts.values()) == 2
