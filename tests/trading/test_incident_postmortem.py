# [A_test] module_id: SRC-TST-1114 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_incident_postmortem
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_incident_postmortem.py
# [TTL] task_bound

from datetime import UTC, datetime

from zephyr.orchestrator.lifecycle.incident_postmortem import Incident, IncidentManager


class TestIncidentModel:
    def test_create_with_defaults(self):
        inc = Incident(incident_id="INC-001")
        assert inc.incident_id == "INC-001"
        assert inc.severity == "P2"
        assert inc.description == ""
        assert inc.timeline == []
        assert inc.root_cause == ""
        assert inc.action_items == []
        assert inc.created_at is not None

    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        inc = Incident(
            incident_id="INC-002",
            severity="P0",
            description="Critical failure",
            timeline=[{"event": "detected", "ts": now.isoformat()}],
            root_cause="config error",
            action_items=["fix config", "add test"],
            created_at=now,
        )
        assert inc.severity == "P0"
        assert inc.description == "Critical failure"
        assert len(inc.timeline) == 1
        assert inc.root_cause == "config error"
        assert len(inc.action_items) == 2

    def test_created_at_auto_populated(self):
        inc = Incident(incident_id="INC-003")
        assert isinstance(inc.created_at, datetime)


class TestIncidentManagerInstantiation:
    def test_create_manager(self):
        mgr = IncidentManager()
        assert mgr is not None

    def test_manager_has_create(self):
        mgr = IncidentManager()
        assert callable(mgr.create)

    def test_manager_has_add_action_item(self):
        mgr = IncidentManager()
        assert callable(mgr.add_action_item)


class TestIncidentManagerCreate:
    def test_create_incident(self):
        mgr = IncidentManager()
        inc = mgr.create("INC-100", "Database down", severity="P1")
        assert inc.incident_id == "INC-100"
        assert inc.description == "Database down"
        assert inc.severity == "P1"

    def test_create_incident_default_severity(self):
        mgr = IncidentManager()
        inc = mgr.create("INC-101", "Minor issue")
        assert inc.severity == "P2"

    def test_create_incident_stored(self):
        mgr = IncidentManager()
        inc = mgr.create("INC-102", "Test")
        retrieved = mgr._incidents.get("INC-102")
        assert retrieved is inc

    def test_create_incident_overwrites_existing(self):
        mgr = IncidentManager()
        inc1 = mgr.create("INC-200", "First", severity="P1")
        inc2 = mgr.create("INC-200", "Second", severity="P0")
        assert mgr._incidents["INC-200"].description == "Second"
        assert mgr._incidents["INC-200"].severity == "P0"


class TestIncidentManagerAddActionItem:
    def test_add_action_item_to_existing_incident(self):
        mgr = IncidentManager()
        mgr.create("INC-300", "Test incident")
        result = mgr.add_action_item("INC-300", "Run diagnostics")
        assert result is True
        assert "Run diagnostics" in mgr._incidents["INC-300"].action_items

    def test_add_action_item_to_nonexistent_incident(self):
        mgr = IncidentManager()
        result = mgr.add_action_item("INC-999", "Does not exist")
        assert result is False

    def test_add_multiple_action_items(self):
        mgr = IncidentManager()
        mgr.create("INC-301", "Test")
        mgr.add_action_item("INC-301", "Action 1")
        mgr.add_action_item("INC-301", "Action 2")
        mgr.add_action_item("INC-301", "Action 3")
        assert len(mgr._incidents["INC-301"].action_items) == 3

    def test_add_empty_action_item(self):
        mgr = IncidentManager()
        mgr.create("INC-302", "Test")
        result = mgr.add_action_item("INC-302", "")
        assert result is True
        assert "" in mgr._incidents["INC-302"].action_items
