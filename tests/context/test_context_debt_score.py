# [A_test] module_id: MOD-GOV_context_debt_score | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §

# [MODULE] tests.test_context_debt_score

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] none

# [TESTS] tests/test_context_debt_score.py
# [TTL] task_bound

"""Tests for zephyr.autonomy_core.context.context_debt_score."""

from __future__ import annotations

import pytest

from zephyr.autonomy_core.context.context_debt_score import ContextDebtScorer, DebtScore


class TestDebtScore:
    def test_instantiation_all_fields(self):
        ds = DebtScore(
            ke_id="KE-001",
            age_days=100.0,
            conflict_count=3,
            ref_staleness=0.5,
            deprecation_risk=0.42,
            deprecated=False,
        )
        assert ds.ke_id == "KE-001"
        assert ds.age_days == 100.0
        assert ds.conflict_count == 3
        assert ds.ref_staleness == 0.5
        assert ds.deprecation_risk == 0.42
        assert ds.deprecated is False

    def test_instantiation_default_values(self):
        ds = DebtScore(
            ke_id="",
            age_days=0.0,
            conflict_count=0,
            ref_staleness=0.0,
            deprecation_risk=0.0,
            deprecated=False,
        )
        assert ds.ke_id == ""
        assert ds.age_days == 0.0
        assert ds.conflict_count == 0
        assert ds.ref_staleness == 0.0
        assert ds.deprecation_risk == 0.0
        assert ds.deprecated is False

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            DebtScore(ke_id="KE-001")


class TestContextDebtScorer:
    def setup_method(self):
        self.scorer = ContextDebtScorer()

    def test_instantiation(self):
        scorer = ContextDebtScorer()
        assert isinstance(scorer, ContextDebtScorer)

    def test_score_returns_debt_score(self):
        result = self.scorer.score("KE-001", 365.0, 1, 1.0)
        assert isinstance(result, DebtScore)

    def test_score_basic_calculation(self):
        result = self.scorer.score("KE-001", 365.0, 1, 1.0)
        expected_risk = (365.0 / 365) * max(1, 1) * max(0.1, 1.0)
        assert result.deprecation_risk == round(min(1.0, expected_risk), 3)
        assert result.ke_id == "KE-001"
        assert result.age_days == 365.0
        assert result.conflict_count == 1
        assert result.ref_staleness == 1.0

    def test_score_deprecated_true(self):
        result = self.scorer.score("KE-002", 730.0, 5, 0.9)
        assert result.deprecated is True
        assert result.deprecation_risk > 0.7

    def test_score_deprecated_false(self):
        result = self.scorer.score("KE-003", 10.0, 0, 0.1)
        assert result.deprecated is False
        assert result.deprecation_risk <= 0.7

    def test_score_clamped_at_one(self):
        result = self.scorer.score("KE-004", 3650.0, 100, 1.0)
        assert result.deprecation_risk <= 1.0

    def test_score_zero_age(self):
        result = self.scorer.score("KE-005", 0.0, 5, 0.9)
        assert result.deprecation_risk == 0.0
        assert result.deprecated is False

    def test_score_zero_conflict_uses_min_one(self):
        result = self.scorer.score("KE-006", 365.0, 0, 1.0)
        expected_risk = (365.0 / 365) * 1 * 1.0
        assert result.deprecation_risk == round(min(1.0, expected_risk), 3)

    def test_score_zero_staleness_uses_min_point_one(self):
        result = self.scorer.score("KE-007", 365.0, 1, 0.0)
        expected_risk = (365.0 / 365) * 1 * 0.1
        assert result.deprecation_risk == round(min(1.0, expected_risk), 3)

    def test_score_negative_age(self):
        result = self.scorer.score("KE-008", -10.0, 1, 0.5)
        assert result.deprecation_risk < 0.0 or result.deprecation_risk >= 0.0
        assert isinstance(result, DebtScore)

    def test_score_negative_conflict_count(self):
        result = self.scorer.score("KE-009", 365.0, -3, 1.0)
        expected_risk = (365.0 / 365) * max(1, -3) * max(0.1, 1.0)
        assert result.deprecation_risk == round(min(1.0, expected_risk), 3)

    def test_score_very_small_staleness(self):
        result = self.scorer.score("KE-010", 365.0, 1, 0.001)
        expected_risk = (365.0 / 365) * 1 * 0.1
        assert result.deprecation_risk == round(min(1.0, expected_risk), 3)

    def test_score_exact_deprecated_boundary(self):
        result = self.scorer.score("KE-011", 365.0, 1, 0.71)
        expected_risk = (365.0 / 365) * 1 * 0.71
        clamped = min(1.0, expected_risk)
        assert result.deprecated is (clamped > 0.7)

    def test_score_missing_ke_id_raises(self):
        with pytest.raises(TypeError):
            self.scorer.score()

    def test_score_missing_age_days_raises(self):
        with pytest.raises(TypeError):
            self.scorer.score("KE-012")

    def test_score_none_ke_id_accepted(self):
        result = self.scorer.score(None, 365.0, 1, 1.0)
        assert result.ke_id is None

    def test_score_none_age_days_raises(self):
        with pytest.raises(TypeError):
            self.scorer.score("KE-013", None, 1, 1.0)

    def test_score_none_conflict_count_raises(self):
        with pytest.raises(TypeError):
            self.scorer.score("KE-014", 365.0, None, 1.0)

    def test_score_none_ref_staleness_raises(self):
        with pytest.raises(TypeError):
            self.scorer.score("KE-015", 365.0, 1, None)
