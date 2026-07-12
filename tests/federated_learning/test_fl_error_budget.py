# [A_test] module_id: SRC-TST-0957 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_error_budget
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.error_budget
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_error_budget.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.error_budget import ErrorBudget, ErrorBudgetManager


class TestErrorBudgetInstantiation:
    def test_creates_with_defaults(self):
        budget = ErrorBudget(contract_id="CT-001")
        assert budget.contract_id == "CT-001"
        assert budget.monthly_budget_minutes == 43.8
        assert budget.consumed_minutes == 0.0
        assert budget.exhausted is False
        assert budget.escalated is False


class TestErrorBudgetManagerInit:
    def test_creates_empty(self):
        mgr = ErrorBudgetManager()
        assert mgr._budgets == {}


class TestInitBudget:
    def test_init_creates_budget(self):
        mgr = ErrorBudgetManager()
        budget = mgr.init_budget("CT-001")
        assert budget.contract_id == "CT-001"
        assert "CT-001" in mgr._budgets


class TestRecordConsumption:
    def test_records_consumption(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        budget = mgr.record_consumption("CT-001", 10.0)
        assert budget.consumed_minutes == 10.0
        assert budget.exhausted is False

    def test_exhausts_budget(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        budget = mgr.record_consumption("CT-001", 50.0)
        assert budget.exhausted is True

    def test_returns_none_for_unknown_contract(self):
        mgr = ErrorBudgetManager()
        result = mgr.record_consumption("UNKNOWN", 5.0)
        assert result is None


class TestRemaining:
    def test_remaining_after_consumption(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        mgr.record_consumption("CT-001", 10.0)
        remaining = mgr.remaining("CT-001")
        assert remaining == pytest.approx(33.8)

    def test_remaining_unknown_contract(self):
        mgr = ErrorBudgetManager()
        assert mgr.remaining("UNKNOWN") == 0.0


class TestIsExhausted:
    def test_not_exhausted_initially(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        assert mgr.is_exhausted("CT-001") is False

    def test_exhausted_after_overconsumption(self):
        mgr = ErrorBudgetManager()
        mgr.init_budget("CT-001")
        mgr.record_consumption("CT-001", 50.0)
        assert mgr.is_exhausted("CT-001") is True

    def test_unknown_contract_not_exhausted(self):
        mgr = ErrorBudgetManager()
        assert mgr.is_exhausted("UNKNOWN") is False
