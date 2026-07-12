# [A_test] module_id: SRC-TST-0843 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_error_budget
# [INVARIANTS] ErrorBudgetManager._budgets keyed by contract_id; consumed_minutes never negative
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.error_budget import ErrorBudget, ErrorBudgetManager


class TestErrorBudgetInstantiation:
    def test_default_values(self):
        b = ErrorBudget(contract_id="CT-001")
        assert b.contract_id == "CT-001"
        assert b.monthly_budget_minutes == 43.8
        assert b.consumed_minutes == 0.0
        assert b.burn_rate == 1.0
        assert b.exhausted is False
        assert b.escalated is False

    def test_custom_budget(self):
        b = ErrorBudget(contract_id="CT-002", monthly_budget_minutes=100.0)
        assert b.monthly_budget_minutes == 100.0


class TestErrorBudgetManagerInit:
    def test_init_budget(self):
        mgr = ErrorBudgetManager()
        budget = mgr.init_budget("CT-001")
        assert isinstance(budget, ErrorBudget)
        assert budget.contract_id == "CT-001"
        assert budget.consumed_minutes == 0.0

    def test_init_multiple_budgets(self):
        mgr = ErrorBudgetManager()
        b1 = mgr.init_budget("CT-001")
        b2 = mgr.init_budget("CT-002")
        assert b1.contract_id != b2.contract_id


class TestErrorBudgetManagerRecordConsumption:
    def test_record_consumption_basic(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        budget = mgr.record_consumption("CT-001", 10.0)
        assert budget is not None
        assert budget.consumed_minutes == 10.0

    def test_record_consumption_accumulates(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        mgr.record_consumption("CT-001", 10.0)
        budget = mgr.record_consumption("CT-001", 5.0)
        assert budget.consumed_minutes == 15.0

    def test_record_consumption_unknown_contract(self):
        mgr = ErrorBudgetManager()
        result = mgr.record_consumption("UNKNOWN", 10.0)
        assert result is None

    def test_record_consumption_exhausts_budget(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        budget = mgr.record_consumption("CT-001", 50.0)
        assert budget.exhausted is True

    def test_record_consumption_exact_budget(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        budget = mgr.record_consumption("CT-001", 43.8)
        assert budget.exhausted is True

    def test_record_consumption_escalates_high_burn_rate(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        budget = mgr.record_consumption("CT-001", 30.0)
        assert budget.burn_rate > 10.0
        assert budget.escalated is True

    def test_record_consumption_zero_minutes(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        budget = mgr.record_consumption("CT-001", 0.0)
        assert budget.consumed_minutes == 0.0
        assert budget.exhausted is False


class TestErrorBudgetManagerRemaining:
    def test_remaining_full(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        assert mgr.remaining("CT-001") == 43.8

    def test_remaining_partial(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        mgr.record_consumption("CT-001", 10.0)
        assert mgr.remaining("CT-001") == pytest.approx(33.8)

    def test_remaining_unknown_contract(self):
        mgr = ErrorBudgetManager()
        assert mgr.remaining("UNKNOWN") == 0.0

    def test_remaining_exhausted(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        mgr.record_consumption("CT-001", 50.0)
        assert mgr.remaining("CT-001") == 0.0


class TestErrorBudgetManagerIsExhausted:
    def test_not_exhausted_initially(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        assert mgr.is_exhausted("CT-001") is False

    def test_exhausted_after_overconsumption(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        mgr.record_consumption("CT-001", 50.0)
        assert mgr.is_exhausted("CT-001") is True

    def test_exhausted_unknown_contract(self):
        mgr = ErrorBudgetManager()
        assert mgr.is_exhausted("UNKNOWN") is False
