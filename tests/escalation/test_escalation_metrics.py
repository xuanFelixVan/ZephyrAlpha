# [A_test] module_id: MOD-GOV_escalation_metrics | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_escalation_metrics
# [INVARIANTS] must test all public classes and methods of escalation_metrics
# [MODIFY-GUARD] escalation_metrics.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_escalation_metrics.py
# [TTL] task_bound

import pytest

from zephyr.governance.escalation.escalation_metrics import EscalationMetrics


class TestEscalationMetrics:
    def test_instantiation(self):
        m = EscalationMetrics()
        assert m.total_evals == 0
        assert m.blocks == 0
        assert m.auto_guards == 0
        assert m.autonomous == 0
        assert m.false_positives == 0
        assert m.latencies == []

    def test_record_blocked(self):
        m = EscalationMetrics()
        m.record("blocked", 0.5)
        assert m.blocks == 1
        assert m.total_evals == 1

    def test_record_auto_guard(self):
        m = EscalationMetrics()
        m.record("auto_guard", 0.3)
        assert m.auto_guards == 1
        assert m.total_evals == 1

    def test_record_autonomous(self):
        m = EscalationMetrics()
        m.record("autonomous", 0.1)
        assert m.autonomous == 1
        assert m.total_evals == 1

    def test_record_false_positive(self):
        m = EscalationMetrics()
        m.record("blocked", 0.5, was_false_positive=True)
        assert m.false_positives == 1

    def test_escalation_rate_empty(self):
        m = EscalationMetrics()
        assert m.escalation_rate() == 0.0

    def test_escalation_rate_with_data(self):
        m = EscalationMetrics()
        m.record("blocked", 0.5)
        m.record("autonomous", 0.1)
        assert m.escalation_rate() == pytest.approx(0.5)

    def test_avg_latency_empty(self):
        m = EscalationMetrics()
        assert m.avg_latency() == 0.0

    def test_avg_latency_with_data(self):
        m = EscalationMetrics()
        m.record("blocked", 0.2)
        m.record("autonomous", 0.4)
        assert m.avg_latency() == pytest.approx(0.3)

    def test_false_positive_rate_no_blocks(self):
        m = EscalationMetrics()
        assert m.false_positive_rate() == 0.0

    def test_false_positive_rate_with_data(self):
        m = EscalationMetrics()
        m.record("blocked", 0.5, was_false_positive=True)
        m.record("blocked", 0.3, was_false_positive=False)
        assert m.false_positive_rate() == pytest.approx(0.5)
