# [A_test] module_id: MOD-GOV_pipeline_cost_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_pipeline_cost_tracker
# [INVARIANTS] CostTracker.total_cost must return rounded float; estimate_cost uses ModelRouter pricing
# [MODIFY-GUARD] only when CostTracker public API changes
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import failure -> skip
# [TESTS] pytest tests/test_pipeline_cost_tracker.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.pipeline.cost_tracker import CostTracker
from zephyr.infrastructure.pipeline.models import CostRecord


class TestCostTrackerInit:
    def test_instantiation(self):
        ct = CostTracker()
        assert ct.total_cost() == 0.0
        assert ct.records == []

    def test_records_returns_copy(self):
        ct = CostTracker()
        ct.record_call("deepseek", 1000, 0.005)
        r = ct.records
        r.clear()
        assert len(ct.records) == 1


class TestCostTrackerRecordCall:
    def test_single_call(self):
        ct = CostTracker()
        ct.record_call("deepseek", 5000, 0.01305)
        assert ct.total_cost() == 0.0131
        assert len(ct.records) == 1

    def test_multiple_calls_accumulate(self):
        ct = CostTracker()
        ct.record_call("deepseek", 5000, 0.01)
        ct.record_call("claude", 3000, 0.05)
        ct.record_call("glm", 1000, 0.0)
        assert ct.total_cost() == 0.06
        assert len(ct.records) == 3

    def test_zero_cost_call(self):
        ct = CostTracker()
        ct.record_call("glm", 1000, 0.0)
        assert ct.total_cost() == 0.0
        assert len(ct.records) == 1

    def test_record_fields(self):
        ct = CostTracker()
        ct.record_call("deepseek", 5000, 0.01305)
        rec = ct.records[0]
        assert isinstance(rec, CostRecord)
        assert rec.model == "deepseek"
        assert rec.tokens_input == 5000
        assert rec.cost_usd == 0.01305

    def test_large_number_of_calls(self):
        ct = CostTracker()
        for i in range(200):
            ct.record_call("deepseek", 1000, 0.001)
        assert ct.total_cost() == 0.2
        assert len(ct.records) == 200


class TestCostTrackerEstimateCost:
    def test_deepseek_estimate(self):
        ct = CostTracker()
        cost = ct.estimate_cost("deepseek", 1000)
        assert cost > 0.0
        expected = (1000 / 1000.0) * 0.00174 + (1000 / 1000.0) * 0.00348
        assert abs(cost - round(expected, 6)) < 1e-9

    def test_claude_estimate(self):
        ct = CostTracker()
        cost = ct.estimate_cost("claude", 1000)
        assert cost > 0.0

    def test_glm_estimate_zero(self):
        ct = CostTracker()
        cost = ct.estimate_cost("glm", 1000)
        assert cost == 0.0

    def test_unknown_model_estimate_zero(self):
        ct = CostTracker()
        cost = ct.estimate_cost("unknown_model", 1000)
        assert cost == 0.0

    def test_zero_tokens(self):
        ct = CostTracker()
        cost = ct.estimate_cost("deepseek", 0)
        assert cost == 0.0

    def test_estimate_does_not_affect_total(self):
        ct = CostTracker()
        ct.estimate_cost("deepseek", 10000)
        assert ct.total_cost() == 0.0


class TestCostTrackerTotalCost:
    def test_empty_total(self):
        ct = CostTracker()
        assert ct.total_cost() == 0.0

    def test_rounding_to_4_decimals(self):
        ct = CostTracker()
        ct.record_call("deepseek", 1000, 0.00001)
        ct.record_call("deepseek", 1000, 0.00002)
        total = ct.total_cost()
        assert total == round(0.00003, 4)


class TestCostTrackerSummary:
    def test_empty_summary(self):
        ct = CostTracker()
        s = ct.summary()
        assert s["total_usd"] == 0.0
        assert s["by_model"] == {}
        assert s["record_count"] == 0

    def test_summary_by_model(self):
        ct = CostTracker()
        ct.record_call("deepseek", 1000, 0.01)
        ct.record_call("deepseek", 2000, 0.02)
        ct.record_call("claude", 1000, 0.05)
        s = ct.summary()
        assert s["total_usd"] == 0.08
        assert s["by_model"]["deepseek"] == 0.03
        assert s["by_model"]["claude"] == 0.05
        assert "glm" not in s["by_model"]
        assert s["record_count"] == 3

    def test_summary_glm_zero_cost_included(self):
        ct = CostTracker()
        ct.record_call("glm", 1000, 0.0)
        s = ct.summary()
        assert "glm" in s["by_model"]
        assert s["by_model"]["glm"] == 0.0
        assert s["record_count"] == 1

    def test_summary_rounding(self):
        ct = CostTracker()
        ct.record_call("deepseek", 1000, 0.00001)
        ct.record_call("deepseek", 1000, 0.00002)
        s = ct.summary()
        assert s["by_model"]["deepseek"] == round(0.00003, 4)


class TestCostTrackerSaveLoadState:
    def test_save_state_empty(self):
        ct = CostTracker()
        state = ct.save_state()
        assert state["total"] == 0.0
        assert state["records"] == []

    def test_save_state_with_records(self):
        ct = CostTracker()
        ct.record_call("deepseek", 1000, 0.01)
        ct.record_call("claude", 2000, 0.05)
        state = ct.save_state()
        assert abs(state["total"] - 0.06) < 1e-9
        assert len(state["records"]) == 2
        assert state["records"][0]["model"] == "deepseek"

    def test_save_state_caps_at_100(self):
        ct = CostTracker()
        for i in range(150):
            ct.record_call("deepseek", 100, 0.001)
        state = ct.save_state()
        assert len(state["records"]) == 100

    def test_load_state(self):
        ct = CostTracker()
        state = {
            "total": 0.05,
            "records": [
                {"model": "deepseek", "tokens_input": 1000, "tokens_output": 0, "cost_usd": 0.05, "estimated": True},
            ],
        }
        ct.load_state(state)
        assert ct.total_cost() == 0.05
        assert len(ct.records) == 1

    def test_load_state_empty(self):
        ct = CostTracker()
        ct.record_call("deepseek", 1000, 0.01)
        ct.load_state({"total": 0.0, "records": []})
        assert ct.total_cost() == 0.0
        assert len(ct.records) == 0

    def test_load_state_missing_keys(self):
        ct = CostTracker()
        ct.load_state({})
        assert ct.total_cost() == 0.0
        assert ct.records == []

    def test_save_load_roundtrip(self):
        ct = CostTracker()
        ct.record_call("deepseek", 5000, 0.01305)
        ct.record_call("claude", 3000, 0.09)
        state = ct.save_state()
        ct2 = CostTracker()
        ct2.load_state(state)
        assert ct2.total_cost() == ct.total_cost()
        assert len(ct2.records) == len(ct.records)
