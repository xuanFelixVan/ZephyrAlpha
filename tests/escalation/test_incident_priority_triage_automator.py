# [A_test] module_id: SRC-TST-1115 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_incident_priority_triage_automator
# [INVARIANTS] classify score→Severity mapping; triage auto-pages at/below threshold
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.incident_priority_triage_automator import (
    IncidentPriorityTriageAutomator,
    Severity,
)


class TestSeverity:
    def test_enum_values(self):
        assert Severity.P0 == "P0"
        assert Severity.P1 == "P1"
        assert Severity.P2 == "P2"
        assert Severity.P3 == "P3"
        assert Severity.P4 == "P4"


class TestIncidentPriorityTriageAutomatorInstantiation:
    def test_default_construction(self):
        ipta = IncidentPriorityTriageAutomator()
        assert ipta.auto_page_threshold == Severity.P1
        assert ipta.batch_window == 600.0
        assert ipta.incidents == []
        assert all(v == 0 for v in ipta.triage_count.values())

    def test_custom_threshold(self):
        ipta = IncidentPriorityTriageAutomator(auto_page_threshold=Severity.P0)
        assert ipta.auto_page_threshold == Severity.P0


class TestClassify:
    def test_p0_high_score(self):
        ipta = IncidentPriorityTriageAutomator()
        incident = {"data_sensitive": True, "user_facing": True, "system_critical": True, "blast_radius": 4}
        assert ipta.classify(incident) == Severity.P0

    def test_p1_medium_high_score(self):
        ipta = IncidentPriorityTriageAutomator()
        incident = {"data_sensitive": True, "user_facing": True, "system_critical": False, "blast_radius": 1}
        assert ipta.classify(incident) == Severity.P1

    def test_p2_medium_score(self):
        ipta = IncidentPriorityTriageAutomator()
        incident = {"data_sensitive": False, "user_facing": True, "system_critical": False, "blast_radius": 1}
        assert ipta.classify(incident) == Severity.P2

    def test_p3_low_score(self):
        ipta = IncidentPriorityTriageAutomator()
        incident = {"data_sensitive": False, "user_facing": False, "system_critical": False, "blast_radius": 1}
        assert ipta.classify(incident) == Severity.P3

    def test_p4_zero_score(self):
        ipta = IncidentPriorityTriageAutomator()
        incident = {"data_sensitive": False, "user_facing": False, "system_critical": False, "blast_radius": 0}
        assert ipta.classify(incident) == Severity.P4

    def test_empty_incident(self):
        ipta = IncidentPriorityTriageAutomator()
        assert ipta.classify({}) == Severity.P4

    def test_blast_radius_capped_at_4(self):
        ipta = IncidentPriorityTriageAutomator()
        incident = {"blast_radius": 100}
        assert ipta.classify(incident) == Severity.P2


class TestTriage:
    def test_pages_p0_incident(self):
        ipta = IncidentPriorityTriageAutomator()
        incident = {"data_sensitive": True, "user_facing": True, "system_critical": True, "blast_radius": 4}
        result = ipta.triage(incident)
        assert result["action"] == "PAGE"
        assert result["severity"] == "P0"

    def test_batches_p4_incident(self):
        ipta = IncidentPriorityTriageAutomator()
        result = ipta.triage({})
        assert result["action"] == "BATCH"
        assert result["severity"] == "P4"

    def test_increments_triage_count(self):
        ipta = IncidentPriorityTriageAutomator()
        ipta.triage({"data_sensitive": True, "user_facing": True, "system_critical": True, "blast_radius": 4})
        assert ipta.triage_count["P0"] == 1

    def test_appends_to_incidents(self):
        ipta = IncidentPriorityTriageAutomator()
        ipta.triage({})
        assert len(ipta.incidents) == 1


class TestGetCounts:
    def test_returns_dict(self):
        ipta = IncidentPriorityTriageAutomator()
        counts = ipta.get_counts()
        assert isinstance(counts, dict)
        assert all(v == 0 for v in counts.values())

    def test_counts_after_triage(self):
        ipta = IncidentPriorityTriageAutomator()
        ipta.triage({})
        counts = ipta.get_counts()
        assert counts["P4"] == 1
