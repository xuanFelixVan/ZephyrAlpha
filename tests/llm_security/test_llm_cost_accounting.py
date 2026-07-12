# [A_test] module_id: SRC-TST-1230 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_llm_cost_accounting
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.llm_cost_accounting
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_llm_cost_accounting.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.collectors.llm_cost_accounting import LLMCostAccounting


class TestLLMCostAccountingInstantiation:
    def test_default_total_cost_zero(self):
        acc = LLMCostAccounting()
        assert acc.total_cost == 0.0

    def test_explicit_initial_cost(self):
        acc = LLMCostAccounting(total_cost=1.5)
        assert acc.total_cost == 1.5


class TestLLMCostAccountingRecord:
    def test_record_adds_cost(self):
        acc = LLMCostAccounting()
        acc.record("gpt-4", 1000)
        assert acc.total_cost == pytest.approx(0.01)

    def test_record_accumulates(self):
        acc = LLMCostAccounting()
        acc.record("gpt-4", 1000)
        acc.record("claude-3", 2000)
        assert acc.total_cost == pytest.approx(0.03)

    def test_record_with_zero_tokens(self):
        acc = LLMCostAccounting()
        acc.record("gpt-4", 0)
        assert acc.total_cost == 0.0

    def test_record_single_token(self):
        acc = LLMCostAccounting()
        acc.record("gpt-4", 1)
        assert acc.total_cost == pytest.approx(0.00001)

    def test_record_large_token_count(self):
        acc = LLMCostAccounting()
        acc.record("gpt-4", 1_000_000)
        assert acc.total_cost == pytest.approx(10.0)


class TestLLMCostAccountingBoundaries:
    def test_record_does_not_return_value(self):
        acc = LLMCostAccounting()
        result = acc.record("gpt-4", 100)
        assert result is None

    def test_multiple_records_precision(self):
        acc = LLMCostAccounting()
        for _ in range(100):
            acc.record("gpt-4", 1)
        assert acc.total_cost == pytest.approx(0.001)

    def test_cost_formula_tokens_times_00001(self):
        acc = LLMCostAccounting()
        tokens = 50000
        acc.record("model-x", tokens)
        assert acc.total_cost == pytest.approx(tokens * 0.00001)
