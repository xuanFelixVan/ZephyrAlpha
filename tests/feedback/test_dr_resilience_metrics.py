# [A_test] module_id: SRC-TST-0767 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_dr_resilience_metrics
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.dr_resilience_metrics
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_dr_resilience_metrics.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.diagnosers.dr_resilience_metrics import (
    DRDrillRecord,
    DRResilienceMetrics,
)


class TestDRDrillRecord:
    def test_creation_with_defaults(self):
        r = DRDrillRecord(
            drill_id="d1",
            timestamp=time.time(),
            rpo_seconds=200.0,
            rto_seconds=500.0,
            passed=True,
        )
        assert r.rpo_target == 300.0
        assert r.rto_target == 900.0

    def test_custom_targets(self):
        r = DRDrillRecord(
            drill_id="d2",
            timestamp=time.time(),
            rpo_seconds=100.0,
            rto_seconds=400.0,
            passed=True,
            rpo_target=600.0,
            rto_target=1800.0,
        )
        assert r.rpo_target == 600.0
        assert r.rto_target == 1800.0

    def test_passed_flag(self):
        r = DRDrillRecord(drill_id="d3", timestamp=0.0, rpo_seconds=0.0, rto_seconds=0.0, passed=False)
        assert r.passed is False


class TestDRResilienceMetricsInstantiation:
    def test_default_values(self):
        m = DRResilienceMetrics()
        assert len(m.history) == 0
        assert m.rpo_violations == 0
        assert m.rto_violations == 0
        assert m.target_drill_interval_days == 90

    def test_custom_values(self):
        m = DRResilienceMetrics(rpo_violations=2, rto_violations=1, target_drill_interval_days=30)
        assert m.rpo_violations == 2
        assert m.target_drill_interval_days == 30


class TestRecord:
    def test_record_appends_to_history(self):
        m = DRResilienceMetrics()
        r = DRDrillRecord(drill_id="d1", timestamp=time.time(), rpo_seconds=100.0, rto_seconds=400.0, passed=True)
        m.record(r)
        assert len(m.history) == 1

    def test_record_no_rpo_violation(self):
        m = DRResilienceMetrics()
        r = DRDrillRecord(drill_id="d1", timestamp=time.time(), rpo_seconds=200.0, rto_seconds=500.0, passed=True)
        m.record(r)
        assert m.rpo_violations == 0

    def test_record_rpo_violation(self):
        m = DRResilienceMetrics()
        r = DRDrillRecord(drill_id="d1", timestamp=time.time(), rpo_seconds=400.0, rto_seconds=500.0, passed=True)
        m.record(r)
        assert m.rpo_violations == 1

    def test_record_rto_violation(self):
        m = DRResilienceMetrics()
        r = DRDrillRecord(drill_id="d1", timestamp=time.time(), rpo_seconds=100.0, rto_seconds=1000.0, passed=True)
        m.record(r)
        assert m.rto_violations == 1

    def test_record_both_violations(self):
        m = DRResilienceMetrics()
        r = DRDrillRecord(drill_id="d1", timestamp=time.time(), rpo_seconds=400.0, rto_seconds=1000.0, passed=False)
        m.record(r)
        assert m.rpo_violations == 1
        assert m.rto_violations == 1

    def test_multiple_records_accumulate_violations(self):
        m = DRResilienceMetrics()
        for _ in range(3):
            m.record(
                DRDrillRecord(drill_id="d", timestamp=time.time(), rpo_seconds=400.0, rto_seconds=1000.0, passed=False)
            )
        assert m.rpo_violations == 3
        assert m.rto_violations == 3


class TestPassRate:
    def test_empty_history_returns_one(self):
        m = DRResilienceMetrics()
        assert m.pass_rate() == 1.0

    def test_all_passed(self):
        m = DRResilienceMetrics()
        for i in range(5):
            m.record(
                DRDrillRecord(
                    drill_id=f"d{i}", timestamp=time.time(), rpo_seconds=100.0, rto_seconds=500.0, passed=True
                )
            )
        assert m.pass_rate() == 1.0

    def test_none_passed(self):
        m = DRResilienceMetrics()
        for i in range(5):
            m.record(
                DRDrillRecord(
                    drill_id=f"d{i}", timestamp=time.time(), rpo_seconds=400.0, rto_seconds=1000.0, passed=False
                )
            )
        assert m.pass_rate() == 0.0

    def test_partial_pass_rate(self):
        m = DRResilienceMetrics()
        m.record(DRDrillRecord(drill_id="d1", timestamp=time.time(), rpo_seconds=100.0, rto_seconds=500.0, passed=True))
        m.record(
            DRDrillRecord(drill_id="d2", timestamp=time.time(), rpo_seconds=400.0, rto_seconds=1000.0, passed=False)
        )
        assert m.pass_rate() == 0.5


class TestDaysSinceLastDrill:
    def test_empty_history_returns_inf(self):
        m = DRResilienceMetrics()
        assert m.days_since_last_drill() == float("inf")

    def test_recent_drill_near_zero(self):
        m = DRResilienceMetrics()
        m.record(DRDrillRecord(drill_id="d1", timestamp=time.time(), rpo_seconds=100.0, rto_seconds=500.0, passed=True))
        assert m.days_since_last_drill() < 1.0

    def test_old_drill_large_days(self):
        m = DRResilienceMetrics()
        old_ts = time.time() - 200 * 86400
        m.record(DRDrillRecord(drill_id="d1", timestamp=old_ts, rpo_seconds=100.0, rto_seconds=500.0, passed=True))
        assert m.days_since_last_drill() > 199.0


class TestDrillOverdue:
    def test_empty_history_is_overdue(self):
        m = DRResilienceMetrics(target_drill_interval_days=90)
        assert m.drill_overdue() is True

    def test_recent_drill_not_overdue(self):
        m = DRResilienceMetrics(target_drill_interval_days=90)
        m.record(DRDrillRecord(drill_id="d1", timestamp=time.time(), rpo_seconds=100.0, rto_seconds=500.0, passed=True))
        assert m.drill_overdue() is False

    def test_old_drill_is_overdue(self):
        m = DRResilienceMetrics(target_drill_interval_days=90)
        m.record(
            DRDrillRecord(
                drill_id="d1", timestamp=time.time() - 100 * 86400, rpo_seconds=100.0, rto_seconds=500.0, passed=True
            )
        )
        assert m.drill_overdue() is True
