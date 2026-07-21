# [A_test] module_id: MOD-GOV_e_escalation_metrics | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_escalation_metrics
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import pytest

from zephyr.governance.escalation.escalation_metrics import EscalationMetrics


class TestEscalationMetricsInit:
    def test_all_counters_are_zero(self):
        m = EscalationMetrics()
        assert m._total_evals == 0
        assert m._blocks == 0
        assert m._auto_guards == 0
        assert m._autonomous == 0
        assert m._false_positives == 0
        assert m._latencies == []


class TestRecord:
    def test_record_blocked_increments_blocks_and_total(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0)
        assert m._total_evals == 1
        assert m._blocks == 1
        assert m._auto_guards == 0
        assert m._autonomous == 0

    def test_record_auto_guard_increments_auto_guards(self):
        m = EscalationMetrics()
        m.record(level="auto_guard", latency_s=0.5)
        assert m._total_evals == 1
        assert m._blocks == 0
        assert m._auto_guards == 1
        assert m._autonomous == 0

    def test_record_other_level_increments_autonomous(self):
        m = EscalationMetrics()
        m.record(level="some_other", latency_s=0.2)
        assert m._total_evals == 1
        assert m._blocks == 0
        assert m._auto_guards == 0
        assert m._autonomous == 1

    def test_record_was_false_positive_increments_false_positives(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0, was_false_positive=True)
        assert m._false_positives == 1

    def test_record_was_false_positive_false_does_not_increment(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0, was_false_positive=False)
        assert m._false_positives == 0

    def test_record_appends_latency(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=3.0)
        m.record(level="auto_guard", latency_s=1.5)
        assert m._latencies == [3.0, 1.5]


class TestEscalationRate:
    def test_rate_with_records(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0)
        m.record(level="blocked", latency_s=2.0)
        m.record(level="auto_guard", latency_s=0.5)
        assert m.escalation_rate() == 2.0 / 3.0

    def test_rate_with_no_records(self):
        m = EscalationMetrics()
        assert m.escalation_rate() == 0.0

    def test_rate_all_blocks(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0)
        m.record(level="blocked", latency_s=2.0)
        assert m.escalation_rate() == 1.0

    def test_rate_zero_blocks(self):
        m = EscalationMetrics()
        m.record(level="auto_guard", latency_s=0.5)
        m.record(level="autonomous", latency_s=0.3)
        assert m.escalation_rate() == 0.0


class TestAvgLatency:
    def test_avg_latency_with_records(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0)
        m.record(level="auto_guard", latency_s=3.0)
        m.record(level="blocked", latency_s=5.0)
        assert m.avg_latency() == 9.0 / 3.0

    def test_avg_latency_with_no_records(self):
        m = EscalationMetrics()
        assert m.avg_latency() == 0.0

    def test_avg_latency_single_record(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=7.0)
        assert m.avg_latency() == 7.0


class TestFalsePositiveRate:
    def test_rate_with_false_positives(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0, was_false_positive=True)
        m.record(level="blocked", latency_s=2.0)
        m.record(level="blocked", latency_s=3.0, was_false_positive=True)
        assert m.false_positive_rate() == 2.0 / 3.0

    def test_rate_with_no_blocks(self):
        m = EscalationMetrics()
        m.record(level="auto_guard", latency_s=0.5, was_false_positive=False)
        assert m.false_positive_rate() == 0.0

    def test_rate_all_false_positives(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0, was_false_positive=True)
        m.record(level="blocked", latency_s=2.0, was_false_positive=True)
        assert m.false_positive_rate() == 1.0

    def test_rate_zero_false_positives(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0)
        m.record(level="blocked", latency_s=2.0)
        assert m.false_positive_rate() == 0.0


class TestBoundary:
    def test_multiple_records_of_each_type(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0)
        m.record(level="blocked", latency_s=2.0)
        m.record(level="auto_guard", latency_s=0.5)
        m.record(level="auto_guard", latency_s=0.7)
        m.record(level="other", latency_s=0.1)
        m.record(level="other", latency_s=0.2)
        assert m._blocks == 2
        assert m._auto_guards == 2
        assert m._autonomous == 2
        assert m._total_evals == 6
        assert m.escalation_rate() == pytest.approx(2.0 / 6.0)
        assert m.avg_latency() == pytest.approx((1.0 + 2.0 + 0.5 + 0.7 + 0.1 + 0.2) / 6.0)

    def test_zero_latency(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=0.0)
        m.record(level="blocked", latency_s=0.0)
        assert m.avg_latency() == 0.0

    def test_very_large_latency(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1e9)
        m.record(level="auto_guard", latency_s=1e9)
        assert m.avg_latency() == 1e9

    def test_many_records_consistency(self):
        m = EscalationMetrics()
        for i in range(100):
            m.record(level="blocked", latency_s=float(i))
        assert m._total_evals == 100
        assert m._blocks == 100
        assert m.avg_latency() == pytest.approx(49.5)

    def test_false_positive_rate_equals_one(self):
        m = EscalationMetrics()
        m.record(level="blocked", latency_s=1.0, was_false_positive=True)
        m.record(level="blocked", latency_s=2.0, was_false_positive=True)
        m.record(level="blocked", latency_s=3.0, was_false_positive=True)
        assert m._false_positives == m._blocks
        assert m.false_positive_rate() == 1.0
