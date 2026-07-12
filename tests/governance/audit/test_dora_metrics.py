# [A_test] module_id: SRC-TST-0763 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_dora_metrics
# [INVARIANTS] DORACollector properties; metric met/unmet logic
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.dora_metrics import DORACollector, DORATargets


class TestDORATargets:
    def test_default_values(self):
        targets = DORATargets()
        assert targets.deployment_frequency_weekly == 7
        assert targets.lead_time_hours == 1.0
        assert targets.change_failure_rate_pct == 5.0
        assert targets.mttr_hours == 1.0

    def test_custom_values(self):
        targets = DORATargets(
            deployment_frequency_weekly=14,
            lead_time_hours=0.5,
            change_failure_rate_pct=3.0,
            mttr_hours=0.5,
        )
        assert targets.deployment_frequency_weekly == 14


class TestDORACollectorInstantiation:
    def test_default_values(self):
        collector = DORACollector()
        assert collector.deployments_this_week == 0
        assert collector.avg_lead_time_hours == 0.0
        assert collector.failure_count == 0
        assert collector.total_changes == 0
        assert collector.incidents == 0
        assert collector.total_recovery_hours == 0.0
        assert collector.last_updated is None


class TestDORACollectorProperties:
    def test_df_met(self):
        collector = DORACollector()
        collector.deployments_this_week = 7
        assert collector.df_met is True

    def test_df_not_met(self):
        collector = DORACollector()
        collector.deployments_this_week = 3
        assert collector.df_met is False

    def test_lt_met(self):
        collector = DORACollector()
        collector.avg_lead_time_hours = 0.5
        assert collector.lt_met is True

    def test_lt_not_met(self):
        collector = DORACollector()
        collector.avg_lead_time_hours = 2.0
        assert collector.lt_met is False

    def test_cfr_zero_changes(self):
        collector = DORACollector()
        assert collector.cfr == 0.0

    def test_cfr_calculation(self):
        collector = DORACollector()
        collector.total_changes = 100
        collector.failure_count = 3
        assert collector.cfr == 3.0

    def test_cfr_met(self):
        collector = DORACollector()
        collector.total_changes = 100
        collector.failure_count = 2
        assert collector.cfr_met is True

    def test_cfr_not_met(self):
        collector = DORACollector()
        collector.total_changes = 100
        collector.failure_count = 10
        assert collector.cfr_met is False

    def test_mttr_zero_incidents(self):
        collector = DORACollector()
        assert collector.mttr == 0.0

    def test_mttr_calculation(self):
        collector = DORACollector()
        collector.incidents = 2
        collector.total_recovery_hours = 1.5
        assert collector.mttr == 0.75

    def test_mttr_met(self):
        collector = DORACollector()
        collector.incidents = 1
        collector.total_recovery_hours = 0.5
        assert collector.mttr_met is True

    def test_mttr_not_met(self):
        collector = DORACollector()
        collector.incidents = 1
        collector.total_recovery_hours = 2.0
        assert collector.mttr_met is False

    def test_all_met(self):
        collector = DORACollector()
        collector.deployments_this_week = 10
        collector.avg_lead_time_hours = 0.5
        collector.total_changes = 100
        collector.failure_count = 2
        collector.incidents = 1
        collector.total_recovery_hours = 0.5
        assert collector.all_met is True

    def test_all_met_false(self):
        collector = DORACollector()
        collector.deployments_this_week = 1
        assert collector.all_met is False


class TestDORACollectorRecordMethods:
    def test_record_deployment(self):
        collector = DORACollector()
        collector.record_deployment(count=3)
        assert collector.deployments_this_week == 3
        assert collector.last_updated is not None

    def test_record_change(self):
        collector = DORACollector()
        collector.record_change(lead_time_hours=0.5, failed=False)
        assert collector.total_changes == 1
        assert collector.avg_lead_time_hours == 0.5
        assert collector.failure_count == 0

    def test_record_change_failed(self):
        collector = DORACollector()
        collector.record_change(lead_time_hours=2.0, failed=True)
        assert collector.failure_count == 1

    def test_record_change_running_average(self):
        collector = DORACollector()
        collector.record_change(lead_time_hours=1.0)
        collector.record_change(lead_time_hours=2.0)
        assert collector.avg_lead_time_hours == 1.5

    def test_record_incident(self):
        collector = DORACollector()
        collector.record_incident(recovery_hours=0.5)
        assert collector.incidents == 1
        assert collector.total_recovery_hours == 0.5


class TestDORACollectorReport:
    def test_report_keys(self):
        collector = DORACollector()
        report = collector.report()
        assert "deployment_frequency" in report
        assert "lead_time" in report
        assert "change_failure_rate" in report
        assert "mttr" in report
        assert "all_met" in report
