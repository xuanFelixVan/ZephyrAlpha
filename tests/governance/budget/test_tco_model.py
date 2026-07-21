# [A_test] module_id: MOD-GOV_tco_model | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-infra_ops/budget-enforcer/blueprint.md
# [MODULE] tests.test_tco_model
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_tco_model.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.ops_governance.tco_model import (
    TCO_MODEL,
    BudgetColumn,
    column_summary,
    get_column,
    token_budget_distribution,
    total_annual,
    total_monthly,
    total_with_tolerance,
)


class TestBudgetColumn:
    def test_monthly_cost(self):
        col = BudgetColumn(
            name="test",
            annual_cost=1200.0,
            precision_budget=100.0,
            tolerance=50.0,
            token_share=0.5,
            description="test col",
        )
        assert col.monthly_cost == 100.0

    def test_exceeds_budget_false(self):
        col = BudgetColumn(
            name="test",
            annual_cost=1200.0,
            precision_budget=100.0,
            tolerance=200.0,
            token_share=0.5,
            description="test col",
        )
        assert col.exceeds_budget(1300.0) is False

    def test_exceeds_budget_true(self):
        col = BudgetColumn(
            name="test",
            annual_cost=1200.0,
            precision_budget=100.0,
            tolerance=200.0,
            token_share=0.5,
            description="test col",
        )
        assert col.exceeds_budget(1500.0) is True

    def test_exceeds_budget_exactly_at_tolerance(self):
        col = BudgetColumn(
            name="test",
            annual_cost=1200.0,
            precision_budget=100.0,
            tolerance=200.0,
            token_share=0.5,
            description="test col",
        )
        assert col.exceeds_budget(1400.0) is False

    def test_exceeds_budget_zero_spend(self):
        col = BudgetColumn(
            name="test",
            annual_cost=1200.0,
            precision_budget=100.0,
            tolerance=200.0,
            token_share=0.5,
            description="test col",
        )
        assert col.exceeds_budget(0.0) is False


class TestGetColumn:
    def test_get_existing_column(self):
        col = get_column("infra")
        assert col is not None
        assert col.name == "infra"

    def test_get_nonexistent_column(self):
        assert get_column("nonexistent") is None

    def test_get_all_known_columns(self):
        for key in ("infra", "dev", "ops", "risk", "metrics"):
            col = get_column(key)
            assert col is not None


class TestTotalAnnual:
    def test_total_annual_matches_sum(self):
        expected = sum(c.annual_cost for c in TCO_MODEL.values())
        assert total_annual() == pytest.approx(expected)

    def test_total_annual_positive(self):
        assert total_annual() > 0


class TestTotalMonthly:
    def test_total_monthly_equals_annual_over_12(self):
        assert total_monthly() == pytest.approx(total_annual() / 12, abs=0.01)


class TestTotalWithTolerance:
    def test_total_with_tolerance(self):
        expected = sum(c.annual_cost + c.tolerance for c in TCO_MODEL.values())
        assert total_with_tolerance() == pytest.approx(expected)

    def test_total_with_tolerance_greater_than_annual(self):
        assert total_with_tolerance() > total_annual()


class TestTokenBudgetDistribution:
    def test_distribution_sums_to_total(self):
        total_tokens = 100000
        dist = token_budget_distribution(total_tokens)
        assert sum(dist.values()) <= total_tokens

    def test_distribution_has_all_keys(self):
        dist = token_budget_distribution(10000)
        assert set(dist.keys()) == set(TCO_MODEL.keys())

    def test_distribution_zero_tokens(self):
        dist = token_budget_distribution(0)
        assert all(v == 0 for v in dist.values())


class TestColumnSummary:
    def test_column_summary_keys(self):
        summary = column_summary()
        assert set(summary.keys()) == set(TCO_MODEL.keys())

    def test_column_summary_inner_keys(self):
        summary = column_summary()
        for key, val in summary.items():
            assert "annual_cost" in val
            assert "monthly_cost" in val
            assert "precision_budget" in val
            assert "tolerance" in val
            assert "token_share" in val

    def test_column_summary_values_match_model(self):
        summary = column_summary()
        for key, val in summary.items():
            col = TCO_MODEL[key]
            assert val["annual_cost"] == col.annual_cost
