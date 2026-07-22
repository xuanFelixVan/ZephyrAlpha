# [A_test] module_id: MOD-GOV_maintenance_window_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_maintenance_window_adapter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_maintenance_window_adapter.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.maintenance_window_adapter import MaintenanceWindowAdapter


class TestMaintenanceWindowAdapterInstantiation:
    def test_creates_instance_not_in_maintenance(self):
        adapter = MaintenanceWindowAdapter()
        assert adapter.in_maintenance is False

    def test_initial_state_is_false(self):
        adapter = MaintenanceWindowAdapter()
        assert adapter._in_maintenance is False


class TestStartMaintenance:
    def test_start_maintenance_sets_true(self):
        adapter = MaintenanceWindowAdapter()
        adapter.start_maintenance()
        assert adapter.in_maintenance is True

    def test_start_maintenance_idempotent(self):
        adapter = MaintenanceWindowAdapter()
        adapter.start_maintenance()
        adapter.start_maintenance()
        assert adapter.in_maintenance is True


class TestEndMaintenance:
    def test_end_maintenance_sets_false(self):
        adapter = MaintenanceWindowAdapter()
        adapter.start_maintenance()
        adapter.end_maintenance()
        assert adapter.in_maintenance is False

    def test_end_maintenance_when_not_started(self):
        adapter = MaintenanceWindowAdapter()
        adapter.end_maintenance()
        assert adapter.in_maintenance is False


class TestAdjustEscalation:
    def test_auto_guard_upgraded_to_autonomous_during_maintenance(self):
        adapter = MaintenanceWindowAdapter()
        adapter.start_maintenance()
        result = adapter.adjust_escalation("auto_guard")
        assert result == "autonomous"

    def test_auto_guard_unchanged_outside_maintenance(self):
        adapter = MaintenanceWindowAdapter()
        result = adapter.adjust_escalation("auto_guard")
        assert result == "auto_guard"

    def test_non_auto_guard_unchanged_during_maintenance(self):
        adapter = MaintenanceWindowAdapter()
        adapter.start_maintenance()
        assert adapter.adjust_escalation("human_gated") == "human_gated"
        assert adapter.adjust_escalation("immutable_core") == "immutable_core"

    def test_non_auto_guard_unchanged_outside_maintenance(self):
        adapter = MaintenanceWindowAdapter()
        assert adapter.adjust_escalation("human_gated") == "human_gated"
        assert adapter.adjust_escalation("immutable_core") == "immutable_core"

    def test_empty_string_level_unchanged(self):
        adapter = MaintenanceWindowAdapter()
        adapter.start_maintenance()
        assert adapter.adjust_escalation("") == ""

    def test_autonomous_level_unchanged_during_maintenance(self):
        adapter = MaintenanceWindowAdapter()
        adapter.start_maintenance()
        assert adapter.adjust_escalation("autonomous") == "autonomous"


class TestMaintenanceWindowAdapterBoundary:
    def test_start_end_start_cycle(self):
        adapter = MaintenanceWindowAdapter()
        adapter.start_maintenance()
        assert adapter.in_maintenance is True
        adapter.end_maintenance()
        assert adapter.in_maintenance is False
        adapter.start_maintenance()
        assert adapter.in_maintenance is True
        assert adapter.adjust_escalation("auto_guard") == "autonomous"

    def test_escalation_changes_with_maintenance_state(self):
        adapter = MaintenanceWindowAdapter()
        assert adapter.adjust_escalation("auto_guard") == "auto_guard"
        adapter.start_maintenance()
        assert adapter.adjust_escalation("auto_guard") == "autonomous"
        adapter.end_maintenance()
        assert adapter.adjust_escalation("auto_guard") == "auto_guard"
