# [A_test] module_id: SRC-TST-0541 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_cognitive_load_budget
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.cognitive_load_budget
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_cognitive_load_budget.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.cognitive_load_budget import (
    CognitiveLoadBudget,
    DecisionRecord,
)


class TestDecisionRecord:
    def test_default_fields(self):
        dr = DecisionRecord(decision_id="d1", severity=5)
        assert dr.decision_id == "d1"
        assert dr.severity == 5
        assert dr.timestamp > 0
        assert dr.resolved is False

    def test_custom_fields(self):
        dr = DecisionRecord(decision_id="d2", severity=10, timestamp=100.0, resolved=True)
        assert dr.timestamp == 100.0
        assert dr.resolved is True


class TestCognitiveLoadBudgetInstantiation:
    def test_default_params(self):
        clb = CognitiveLoadBudget()
        assert clb.max_decisions_per_hour == 12
        assert clb.max_decisions_per_day == 50
        assert clb.fatigue_weight_severity_high == 3.0
        assert clb.decisions_hourly == []
        assert clb.decisions_daily == []
        assert clb.fatigue_score == 0.0

    def test_custom_params(self):
        clb = CognitiveLoadBudget(max_decisions_per_hour=5, max_decisions_per_day=20)
        assert clb.max_decisions_per_hour == 5
        assert clb.max_decisions_per_day == 20


class TestCognitiveLoadBudgetRequest:
    def test_request_accepted_initially(self):
        clb = CognitiveLoadBudget()
        result = clb.request("d1", severity=5)
        assert result is True

    def test_request_records_timestamp(self):
        clb = CognitiveLoadBudget()
        clb.request("d1", severity=5)
        assert len(clb.decisions_hourly) == 1
        assert len(clb.decisions_daily) == 1

    def test_request_updates_fatigue_score(self):
        clb = CognitiveLoadBudget(max_decisions_per_hour=10)
        clb.request("d1", severity=5)
        assert clb.fatigue_score > 0

    def test_request_rejected_when_daily_exceeded(self):
        clb = CognitiveLoadBudget(max_decisions_per_day=2)
        clb.request("d1", severity=1)
        clb.request("d2", severity=1)
        result = clb.request("d3", severity=1)
        assert result is False

    def test_request_rejected_when_hourly_weighted_exceeded(self):
        clb = CognitiveLoadBudget(max_decisions_per_hour=1, fatigue_weight_severity_high=3.0)
        clb.request("d1", severity=10)
        result = clb.request("d2", severity=10)
        assert result is False

    def test_low_severity_accepted_more(self):
        clb = CognitiveLoadBudget(max_decisions_per_hour=12, fatigue_weight_severity_high=3.0)
        for i in range(5):
            result = clb.request(f"d{i}", severity=1)
        assert result is True


class TestCognitiveLoadBudgetDefer:
    def test_defer_does_not_crash(self):
        clb = CognitiveLoadBudget()
        clb.defer("d1", delay_seconds=60.0)

    def test_defer_on_empty_budget(self):
        clb = CognitiveLoadBudget()
        clb.defer("nonexistent", delay_seconds=0.0)


class TestCognitiveLoadBudgetBoundary:
    def test_zero_severity(self):
        clb = CognitiveLoadBudget()
        result = clb.request("d1", severity=0)
        assert result is True

    def test_negative_severity(self):
        clb = CognitiveLoadBudget()
        result = clb.request("d1", severity=-1)
        assert result is True

    def test_empty_decision_id(self):
        clb = CognitiveLoadBudget()
        result = clb.request("", severity=5)
        assert result is True

    def test_none_decision_id_accepted(self):
        clb = CognitiveLoadBudget()
        result = clb.request(None, severity=5)
        assert result is True

    def test_fatigue_score_bounded(self):
        clb = CognitiveLoadBudget(max_decisions_per_hour=100)
        for i in range(10):
            clb.request(f"d{i}", severity=5)
        assert 0.0 <= clb.fatigue_score <= 1.0
