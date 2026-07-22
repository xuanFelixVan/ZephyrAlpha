# [A_test] module_id: MOD-GOV_risk_matrix | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_risk_matrix
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_risk_matrix.py -q
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.financial_governance.risk_matrix import (
    RISK_LEVEL_ORDER,
    RISK_MATRIX,
    RiskCategory,
    RiskItem,
    RiskLevel,
    _compute_risk_level,
    flagged_risks,
    get_interactions,
    get_risk,
    risks_sorted_by_level,
)


class TestRiskCategoryEnum:
    def test_operational_value(self):
        assert RiskCategory.OPERATIONAL == "OPERATIONAL"

    def test_data_value(self):
        assert RiskCategory.DATA == "DATA"

    def test_legal_compliance_value(self):
        assert RiskCategory.LEGAL_COMPLIANCE == "LEGAL_COMPLIANCE"

    def test_isolation_value(self):
        assert RiskCategory.ISOLATION == "ISOLATION"


class TestRiskLevelEnum:
    def test_all_levels_exist(self):
        assert RiskLevel.LOW == "LOW"
        assert RiskLevel.MEDIUM == "MEDIUM"
        assert RiskLevel.HIGH == "HIGH"
        assert RiskLevel.CRITICAL == "CRITICAL"


class TestComputeRiskLevel:
    def test_critical_threshold(self):
        assert _compute_risk_level(5, 4) == RiskLevel.CRITICAL
        assert _compute_risk_level(4, 5) == RiskLevel.CRITICAL

    def test_high_threshold(self):
        assert _compute_risk_level(3, 4) == RiskLevel.HIGH
        assert _compute_risk_level(4, 3) == RiskLevel.HIGH

    def test_medium_threshold(self):
        assert _compute_risk_level(2, 3) == RiskLevel.MEDIUM
        assert _compute_risk_level(3, 2) == RiskLevel.MEDIUM

    def test_low_threshold(self):
        assert _compute_risk_level(1, 1) == RiskLevel.LOW
        assert _compute_risk_level(1, 2) == RiskLevel.LOW

    def test_boundary_score_20_is_critical(self):
        assert _compute_risk_level(5, 4) == RiskLevel.CRITICAL
        assert _compute_risk_level(4, 5) == RiskLevel.CRITICAL

    def test_boundary_score_12_is_high(self):
        assert _compute_risk_level(3, 4) == RiskLevel.HIGH

    def test_boundary_score_6_is_medium(self):
        assert _compute_risk_level(2, 3) == RiskLevel.MEDIUM

    def test_boundary_score_5_is_low(self):
        assert _compute_risk_level(1, 5) == RiskLevel.LOW


class TestRiskItem:
    def test_risk_score_calculation(self):
        item = RiskItem(
            name="test",
            category=RiskCategory.OPERATIONAL,
            likelihood=3,
            impact=4,
            risk_level=RiskLevel.HIGH,
            description="desc",
            mitigation="mit",
            mitigator="team",
        )
        assert item.risk_score == 12

    def test_risk_score_boundary_minimum(self):
        item = RiskItem(
            name="min",
            category=RiskCategory.DATA,
            likelihood=1,
            impact=1,
            risk_level=RiskLevel.LOW,
            description="desc",
            mitigation="mit",
            mitigator="team",
        )
        assert item.risk_score == 1

    def test_risk_score_boundary_maximum(self):
        item = RiskItem(
            name="max",
            category=RiskCategory.OPERATIONAL,
            likelihood=5,
            impact=5,
            risk_level=RiskLevel.CRITICAL,
            description="desc",
            mitigation="mit",
            mitigator="team",
        )
        assert item.risk_score == 25

    def test_likelihood_validation_rejects_zero(self):
        with pytest.raises(Exception):
            RiskItem(
                name="bad",
                category=RiskCategory.OPERATIONAL,
                likelihood=0,
                impact=3,
                risk_level=RiskLevel.LOW,
                description="desc",
                mitigation="mit",
                mitigator="team",
            )

    def test_impact_validation_rejects_six(self):
        with pytest.raises(Exception):
            RiskItem(
                name="bad",
                category=RiskCategory.OPERATIONAL,
                likelihood=3,
                impact=6,
                risk_level=RiskLevel.LOW,
                description="desc",
                mitigation="mit",
                mitigator="team",
            )

    def test_default_trigger_flags_empty(self):
        item = RiskItem(
            name="test",
            category=RiskCategory.OPERATIONAL,
            likelihood=2,
            impact=2,
            risk_level=RiskLevel.LOW,
            description="desc",
            mitigation="mit",
            mitigator="team",
        )
        assert item.trigger_flags == []

    def test_default_related_risks_empty(self):
        item = RiskItem(
            name="test",
            category=RiskCategory.OPERATIONAL,
            likelihood=2,
            impact=2,
            risk_level=RiskLevel.LOW,
            description="desc",
            mitigation="mit",
            mitigator="team",
        )
        assert item.related_risks == []


class TestGetRisk:
    def test_returns_operational_risk(self):
        risk = get_risk(RiskCategory.OPERATIONAL)
        assert risk is not None
        assert risk.category == RiskCategory.OPERATIONAL

    def test_returns_data_risk(self):
        risk = get_risk(RiskCategory.DATA)
        assert risk is not None
        assert risk.category == RiskCategory.DATA

    def test_returns_none_for_nonexistent_key(self):
        result = get_risk("NONEXISTENT")
        assert result is None


class TestRisksSortedByLevel:
    def test_returns_all_risks(self):
        sorted_risks = risks_sorted_by_level()
        assert len(sorted_risks) == len(RISK_MATRIX)

    def test_first_risk_is_highest_level(self):
        sorted_risks = risks_sorted_by_level()
        highest_order = RISK_LEVEL_ORDER.get(sorted_risks[0].risk_level, -1)
        for risk in sorted_risks[1:]:
            assert highest_order >= RISK_LEVEL_ORDER.get(risk.risk_level, -1)

    def test_sorted_by_score_within_same_level(self):
        sorted_risks = risks_sorted_by_level()
        for i in range(len(sorted_risks) - 1):
            a, b = sorted_risks[i], sorted_risks[i + 1]
            if RISK_LEVEL_ORDER[a.risk_level] == RISK_LEVEL_ORDER[b.risk_level]:
                assert a.risk_score >= b.risk_score


class TestGetInteractions:
    def test_operational_and_data_do_not_interact_by_name(self):
        op = get_risk(RiskCategory.OPERATIONAL)
        data = get_risk(RiskCategory.DATA)
        assert get_interactions(op, data) is False

    def test_interaction_by_name_match(self):
        item_a = RiskItem(
            name="alpha",
            category=RiskCategory.OPERATIONAL,
            likelihood=2,
            impact=2,
            risk_level=RiskLevel.LOW,
            description="desc",
            mitigation="mit",
            mitigator="team",
            related_risks=["bravo"],
        )
        item_b = RiskItem(
            name="bravo",
            category=RiskCategory.DATA,
            likelihood=2,
            impact=2,
            risk_level=RiskLevel.LOW,
            description="desc",
            mitigation="mit",
            mitigator="team",
            related_risks=["alpha"],
        )
        assert get_interactions(item_a, item_b) is True
        assert get_interactions(item_b, item_a) is True

    def test_no_interaction_when_names_not_in_related(self):
        item_a = RiskItem(
            name="alpha",
            category=RiskCategory.OPERATIONAL,
            likelihood=2,
            impact=2,
            risk_level=RiskLevel.LOW,
            description="desc",
            mitigation="mit",
            mitigator="team",
            related_risks=["charlie"],
        )
        item_b = RiskItem(
            name="bravo",
            category=RiskCategory.DATA,
            likelihood=2,
            impact=2,
            risk_level=RiskLevel.LOW,
            description="desc",
            mitigation="mit",
            mitigator="team",
            related_risks=["delta"],
        )
        assert get_interactions(item_a, item_b) is False


class TestFlaggedRisks:
    def test_flag_build_failure_returns_operational(self):
        results = flagged_risks("build_failure")
        assert len(results) >= 1
        assert any(r.category == RiskCategory.OPERATIONAL for r in results)

    def test_flag_vendor_outage_returns_data(self):
        results = flagged_risks("vendor_outage")
        assert len(results) >= 1
        assert any(r.category == RiskCategory.DATA for r in results)

    def test_unknown_flag_returns_empty(self):
        results = flagged_risks("nonexistent_flag")
        assert results == []


class TestRiskMatrixCompleteness:
    def test_all_categories_present(self):
        for cat in RiskCategory:
            assert cat in RISK_MATRIX

    def test_each_risk_has_required_fields(self):
        for cat, risk in RISK_MATRIX.items():
            assert risk.name
            assert risk.category == cat
            assert 1 <= risk.likelihood <= 5
            assert 1 <= risk.impact <= 5
            assert isinstance(risk.risk_level, RiskLevel)
            assert risk.description
            assert risk.mitigation
            assert risk.mitigator

    def test_risk_level_matches_compute(self):
        for risk in RISK_MATRIX.values():
            expected = _compute_risk_level(risk.likelihood, risk.impact)
            assert risk.risk_level == expected
