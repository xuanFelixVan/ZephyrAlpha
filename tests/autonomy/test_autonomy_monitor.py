# [A_test] module_id: MOD-GOV_autonomy_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-349 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_autonomy_monitor
# [INVARIANTS] AutonomyLevel order: FULL>SUPERVISED>RESTRICTED>READ_ONLY; downgrade never goes up; upgrade never goes down
# [MODIFY-GUARD] 仅当autonomy_monitor公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_autonomy_monitor.py -q
# [TTL] task_bound


from zephyr.shared.maintenance.autonomy_monitor import (
    AutonomyLevel,
    AutonomyMonitor,
    AutonomyReport,
    AutonomyState,
)


class TestAutonomyMonitorInstantiation:
    def test_default_instantiation(self):
        monitor = AutonomyMonitor()
        assert monitor is not None
        assert monitor.get_level() == AutonomyLevel.SUPERVISED

    def test_instantiation_with_data_dir(self, tmp_path):
        monitor = AutonomyMonitor(data_dir=tmp_path / "autonomy")
        assert monitor is not None
        assert monitor.get_level() == AutonomyLevel.SUPERVISED

    def test_instantiation_with_none_data_dir(self):
        monitor = AutonomyMonitor(data_dir=None)
        assert monitor is not None


class TestAutonomyMonitorDowngrade:
    def test_downgrade_default(self):
        monitor = AutonomyMonitor()
        new_level = monitor.downgrade(reason="test failure")
        assert new_level == AutonomyLevel.RESTRICTED
        assert monitor.get_level() == AutonomyLevel.RESTRICTED

    def test_downgrade_to_specific_level(self):
        monitor = AutonomyMonitor()
        new_level = monitor.downgrade(reason="emergency", to_level=AutonomyLevel.READ_ONLY)
        assert new_level == AutonomyLevel.READ_ONLY
        assert monitor.get_level() == AutonomyLevel.READ_ONLY

    def test_downgrade_at_bottom_stays(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="r1")
        monitor.downgrade(reason="r2")
        monitor.downgrade(reason="r3")
        assert monitor.get_level() == AutonomyLevel.READ_ONLY
        result = monitor.downgrade(reason="already at bottom")
        assert result == AutonomyLevel.READ_ONLY

    def test_downgrade_increments_count(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="r1")
        monitor.downgrade(reason="r2")
        assert monitor._state.downgrade_count == 2

    def test_downgrade_updates_previous_level(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="r1")
        assert monitor._state.previous_level == AutonomyLevel.SUPERVISED

    def test_downgrade_logs_event(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="test reason")
        assert len(monitor._event_log) == 1
        assert monitor._event_log[0]["type"] == "DOWNGRADE"
        assert monitor._event_log[0]["reason"] == "test reason"


class TestAutonomyMonitorUpgrade:
    def test_upgrade_from_supervised(self):
        monitor = AutonomyMonitor()
        new_level = monitor.upgrade(reason="stable performance")
        assert new_level == AutonomyLevel.FULL
        assert monitor.get_level() == AutonomyLevel.FULL

    def test_upgrade_from_restricted(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="r1")
        new_level = monitor.upgrade(reason="recovered")
        assert new_level == AutonomyLevel.SUPERVISED

    def test_upgrade_at_top_stays(self):
        monitor = AutonomyMonitor()
        monitor.upgrade(reason="already at top")
        result = monitor.upgrade(reason="still at top")
        assert result == AutonomyLevel.FULL

    def test_upgrade_increments_count(self):
        monitor = AutonomyMonitor()
        monitor.upgrade(reason="r1")
        monitor.upgrade(reason="r2")
        assert monitor._state.upgrade_count == 2

    def test_upgrade_logs_event(self):
        monitor = AutonomyMonitor()
        monitor.upgrade(reason="test upgrade")
        assert len(monitor._event_log) == 1
        assert monitor._event_log[0]["type"] == "UPGRADE"


class TestAutonomyMonitorCanAutoExecute:
    def test_full_can_auto_execute(self):
        monitor = AutonomyMonitor()
        monitor.upgrade(reason="full autonomy")
        assert monitor.can_auto_execute() is True

    def test_supervised_can_auto_execute(self):
        monitor = AutonomyMonitor()
        assert monitor.can_auto_execute() is True

    def test_restricted_cannot_auto_execute(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="restricted")
        assert monitor.can_auto_execute() is False

    def test_read_only_cannot_auto_execute(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="r1", to_level=AutonomyLevel.READ_ONLY)
        assert monitor.can_auto_execute() is False


class TestAutonomyMonitorNeedsHumanApproval:
    def test_full_does_not_need_approval(self):
        monitor = AutonomyMonitor()
        monitor.upgrade(reason="full")
        assert monitor.needs_human_approval() is False

    def test_supervised_does_not_need_approval(self):
        monitor = AutonomyMonitor()
        assert monitor.needs_human_approval() is False

    def test_restricted_needs_approval(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="restricted")
        assert monitor.needs_human_approval() is True

    def test_read_only_needs_approval(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="r1", to_level=AutonomyLevel.READ_ONLY)
        assert monitor.needs_human_approval() is True


class TestAutonomyMonitorGenerateReport:
    def test_report_type(self):
        monitor = AutonomyMonitor()
        report = monitor.generate_report()
        assert isinstance(report, AutonomyReport)

    def test_report_level_matches_current(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="test")
        report = monitor.generate_report()
        assert report.level == AutonomyLevel.RESTRICTED

    def test_report_downgrade_history(self):
        monitor = AutonomyMonitor()
        monitor.downgrade(reason="r1")
        monitor.downgrade(reason="r2")
        report = monitor.generate_report()
        assert len(report.downgrade_history) == 2

    def test_report_downgrade_history_capped_at_10(self):
        monitor = AutonomyMonitor()
        for i in range(15):
            monitor.downgrade(reason=f"r{i}")
        report = monitor.generate_report()
        assert len(report.downgrade_history) == 10

    def test_report_recommendation_full(self):
        monitor = AutonomyMonitor()
        monitor.upgrade(reason="full")
        report = monitor.generate_report()
        assert "Full autonomy" in report.recommendation

    def test_report_recommendation_not_full(self):
        monitor = AutonomyMonitor()
        report = monitor.generate_report()
        assert "Human supervision" in report.recommendation

    def test_report_empty_history(self):
        monitor = AutonomyMonitor()
        report = monitor.generate_report()
        assert report.downgrade_history == []


class TestAutonomyState:
    def test_default_state(self):
        state = AutonomyState(current_level=AutonomyLevel.SUPERVISED)
        assert state.current_level == AutonomyLevel.SUPERVISED
        assert state.previous_level is None
        assert state.downgrade_count == 0
        assert state.upgrade_count == 0

    def test_state_last_changed_is_string(self):
        state = AutonomyState(current_level=AutonomyLevel.FULL)
        assert isinstance(state.last_changed, str)
