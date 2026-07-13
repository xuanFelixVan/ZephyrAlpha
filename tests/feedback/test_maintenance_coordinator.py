# [A_test] module_id: SRC-TST-1244 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_maintenance_coordinator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_maintenance_coordinator.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.reliability.maintenance_coordinator import MaintenanceCoordinator


class TestMaintenanceCoordinator:
    def test_default_construction(self):
        coord = MaintenanceCoordinator()
        assert coord.windows == []

    def test_custom_construction_with_windows(self):
        initial = [{"start": 1, "end": 2}]
        coord = MaintenanceCoordinator(windows=initial)
        assert len(coord.windows) == 1

    def test_schedule_appends_window(self):
        coord = MaintenanceCoordinator()
        coord.schedule({"start": "2026-01-01", "end": "2026-01-02", "type": "planned"})
        assert len(coord.windows) == 1
        assert coord.windows[0]["type"] == "planned"

    def test_schedule_multiple_windows(self):
        coord = MaintenanceCoordinator()
        coord.schedule({"start": 1, "end": 2})
        coord.schedule({"start": 3, "end": 4})
        coord.schedule({"start": 5, "end": 6})
        assert len(coord.windows) == 3

    def test_schedule_empty_window(self):
        coord = MaintenanceCoordinator()
        coord.schedule({})
        assert len(coord.windows) == 1

    def test_schedule_preserves_window_data(self):
        coord = MaintenanceCoordinator()
        window = {"start": 100, "end": 200, "system": "db", "impact": "read_only"}
        coord.schedule(window)
        assert coord.windows[0]["system"] == "db"
        assert coord.windows[0]["impact"] == "read_only"
