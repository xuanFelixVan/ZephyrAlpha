# [A_test] module_id: MOD-GOV_e_risk_matrix | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_risk_matrix
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest
from pydantic import ValidationError

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


class TestRiskCategory:
    def test_four_members(self):
        assert len(RiskCategory) == 4
        members = {m for m in RiskCategory}
        assert members == {
            RiskCategory.OPERATIONAL,
            RiskCategory.DATA,
            RiskCategory.LEGAL_COMPLIANCE,
            RiskCategory.ISOLATION,
        }

    def test_string_values(self):
        assert RiskCategory.OPERATIONAL.value == "OPERATIONAL"
        assert RiskCategory.DATA.value == "DATA"
        assert RiskCategory.LEGAL_COMPLIANCE.value == "LEGAL_COMPLIANCE"
        assert RiskCategory.ISOLATION.value == "ISOLATION"


class TestRiskLevel:
    def test_four_members(self):
        assert len(RiskLevel) == 4
        members = {m for m in RiskLevel}
        assert members == {RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL}

    def test_string_values(self):
        assert RiskLevel.LOW.value == "LOW"
        assert RiskLevel.MEDIUM.value == "MEDIUM"
        assert RiskLevel.HIGH.value == "HIGH"
        assert RiskLevel.CRITICAL.value == "CRITICAL"


class TestRiskItem:
    def test_instantiation_with_all_fields(self):
        item = RiskItem(
            name="测试风险",
            category=RiskCategory.OPERATIONAL,
            likelihood=3,
            impact=4,
            risk_level=RiskLevel.HIGH,
            description="测试描述",
            mitigation="测试缓解",
            mitigator="测试责任人",
            trigger_flags=["flag_a", "flag_b"],
            related_risks=["DATA"],
        )
        assert item.name == "测试风险"
        assert item.category == RiskCategory.OPERATIONAL
        assert item.likelihood == 3
        assert item.impact == 4
        assert item.risk_level == RiskLevel.HIGH
        assert item.description == "测试描述"
        assert item.mitigation == "测试缓解"
        assert item.mitigator == "测试责任人"
        assert item.trigger_flags == ["flag_a", "flag_b"]
        assert item.related_risks == ["DATA"]

    def test_risk_score_property(self):
        item = RiskItem(
            name="x",
            category=RiskCategory.OPERATIONAL,
            likelihood=4,
            impact=5,
            risk_level=RiskLevel.CRITICAL,
            description="x",
            mitigation="x",
            mitigator="x",
        )
        assert item.risk_score == 20
        assert isinstance(item.risk_score, int)

    def test_risk_score_various(self):
        cases = [
            (1, 1, 1),
            (2, 3, 6),
            (3, 4, 12),
            (5, 5, 25),
        ]
        for likelihood, impact, expected in cases:
            item = RiskItem(
                name="x",
                category=RiskCategory.DATA,
                likelihood=likelihood,
                impact=impact,
                risk_level=RiskLevel.LOW,
                description="x",
                mitigation="x",
                mitigator="x",
            )
            assert item.risk_score == expected

    def test_default_trigger_flags_and_related_risks(self):
        item = RiskItem(
            name="x",
            category=RiskCategory.ISOLATION,
            likelihood=1,
            impact=1,
            risk_level=RiskLevel.LOW,
            description="x",
            mitigation="x",
            mitigator="x",
        )
        assert item.trigger_flags == []
        assert item.related_risks == []
        assert isinstance(item.trigger_flags, list)
        assert isinstance(item.related_risks, list)

    def test_likelihood_constrained_ge_1(self):
        with pytest.raises(ValidationError):
            RiskItem(
                name="x",
                category=RiskCategory.OPERATIONAL,
                likelihood=0,
                impact=3,
                risk_level=RiskLevel.LOW,
                description="x",
                mitigation="x",
                mitigator="x",
            )

    def test_likelihood_constrained_le_5(self):
        with pytest.raises(ValidationError):
            RiskItem(
                name="x",
                category=RiskCategory.OPERATIONAL,
                likelihood=6,
                impact=3,
                risk_level=RiskLevel.LOW,
                description="x",
                mitigation="x",
                mitigator="x",
            )

    def test_impact_constrained_ge_1(self):
        with pytest.raises(ValidationError):
            RiskItem(
                name="x",
                category=RiskCategory.OPERATIONAL,
                likelihood=3,
                impact=0,
                risk_level=RiskLevel.LOW,
                description="x",
                mitigation="x",
                mitigator="x",
            )

    def test_impact_constrained_le_5(self):
        with pytest.raises(ValidationError):
            RiskItem(
                name="x",
                category=RiskCategory.OPERATIONAL,
                likelihood=3,
                impact=6,
                risk_level=RiskLevel.LOW,
                description="x",
                mitigation="x",
                mitigator="x",
            )

    def test_boundary_values_valid(self):
        item = RiskItem(
            name="x",
            category=RiskCategory.OPERATIONAL,
            likelihood=1,
            impact=5,
            risk_level=RiskLevel.LOW,
            description="x",
            mitigation="x",
            mitigator="x",
        )
        assert item.likelihood == 1
        assert item.impact == 5


class TestComputeRiskLevel:
    def test_critical(self):
        assert _compute_risk_level(4, 5) == RiskLevel.CRITICAL
        assert _compute_risk_level(5, 4) == RiskLevel.CRITICAL
        assert _compute_risk_level(5, 5) == RiskLevel.CRITICAL

    def test_high(self):
        assert _compute_risk_level(4, 3) == RiskLevel.HIGH
        assert _compute_risk_level(3, 4) == RiskLevel.HIGH
        assert _compute_risk_level(5, 3) == RiskLevel.HIGH

    def test_medium(self):
        assert _compute_risk_level(3, 2) == RiskLevel.MEDIUM
        assert _compute_risk_level(2, 3) == RiskLevel.MEDIUM
        assert _compute_risk_level(2, 4) == RiskLevel.MEDIUM

    def test_low(self):
        assert _compute_risk_level(2, 2) == RiskLevel.LOW
        assert _compute_risk_level(1, 3) == RiskLevel.LOW
        assert _compute_risk_level(1, 1) == RiskLevel.LOW

    def test_exact_thresholds(self):
        assert _compute_risk_level(4, 5) == RiskLevel.CRITICAL
        assert _compute_risk_level(3, 4) == RiskLevel.HIGH
        assert _compute_risk_level(2, 3) == RiskLevel.MEDIUM
        assert _compute_risk_level(2, 2) == RiskLevel.LOW


class TestRiskMatrix:
    def test_has_four_categories(self):
        assert len(RISK_MATRIX) == 4
        assert RiskCategory.OPERATIONAL in RISK_MATRIX
        assert RiskCategory.DATA in RISK_MATRIX
        assert RiskCategory.LEGAL_COMPLIANCE in RISK_MATRIX
        assert RiskCategory.ISOLATION in RISK_MATRIX

    def test_each_entry_is_risk_item(self):
        for category, item in RISK_MATRIX.items():
            assert isinstance(item, RiskItem), f"{category} entry is not a RiskItem"
            assert item.name
            assert item.description
            assert item.mitigation
            assert item.mitigator
            assert 1 <= item.likelihood <= 5
            assert 1 <= item.impact <= 5
            assert item.risk_level == _compute_risk_level(item.likelihood, item.impact)

    def test_entries_required_fields(self):
        required = ["name", "category", "likelihood", "impact", "risk_level", "description", "mitigation", "mitigator"]
        for category, item in RISK_MATRIX.items():
            for field in required:
                assert getattr(item, field) is not None, f"{category}.{field} is None"
            assert len(item.name) > 0
            assert len(item.description) > 0
            assert len(item.mitigation) > 0
            assert len(item.mitigator) > 0


class TestRiskLevelOrder:
    def test_correct_ordering(self):
        assert RISK_LEVEL_ORDER[RiskLevel.LOW] == 0
        assert RISK_LEVEL_ORDER[RiskLevel.MEDIUM] == 1
        assert RISK_LEVEL_ORDER[RiskLevel.HIGH] == 2
        assert RISK_LEVEL_ORDER[RiskLevel.CRITICAL] == 3

    def test_has_all_levels(self):
        assert set(RISK_LEVEL_ORDER.keys()) == {RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL}


class TestGetRisk:
    def test_valid_category_returns_risk_item(self):
        item = get_risk(RiskCategory.OPERATIONAL)
        assert isinstance(item, RiskItem)
        assert item.category == RiskCategory.OPERATIONAL

    def test_all_categories_return_risk_item(self):
        for category in RiskCategory:
            item = get_risk(category)
            assert isinstance(item, RiskItem)
            assert item.category == category

    def test_invalid_category_returns_none(self):
        assert get_risk(None) is None


class TestRisksSortedByLevel:
    def test_returns_list_of_risk_items(self):
        result = risks_sorted_by_level()
        assert isinstance(result, list)
        assert len(result) == 4
        for item in result:
            assert isinstance(item, RiskItem)

    def test_sorted_by_severity_desc(self):
        result = risks_sorted_by_level()
        orders = [RISK_LEVEL_ORDER[item.risk_level] for item in result]
        assert orders == sorted(orders, reverse=True), f"Not sorted desc: {orders}"

    def test_same_level_sorted_by_score_desc(self):
        result = risks_sorted_by_level()
        for i in range(len(result) - 1):
            a = result[i]
            b = result[i + 1]
            order_a = RISK_LEVEL_ORDER[a.risk_level]
            order_b = RISK_LEVEL_ORDER[b.risk_level]
            assert order_a >= order_b
            if order_a == order_b:
                assert a.risk_score >= b.risk_score


class TestGetInteractions:
    def test_no_interactions_found_due_to_name_vs_category_mismatch(self):
        operational = get_risk(RiskCategory.OPERATIONAL)
        data = get_risk(RiskCategory.DATA)
        assert get_interactions(operational, data) is False

    def test_no_cross_interactions(self):
        operational = get_risk(RiskCategory.OPERATIONAL)
        legal = get_risk(RiskCategory.LEGAL_COMPLIANCE)
        assert get_interactions(operational, legal) is False

    def test_symmetric(self):
        a = get_risk(RiskCategory.DATA)
        b = get_risk(RiskCategory.LEGAL_COMPLIANCE)
        assert get_interactions(a, b) == get_interactions(b, a)


class TestFlaggedRisks:
    def test_build_failure_returns_operational(self):
        result = flagged_risks("build_failure")
        assert len(result) == 1
        assert result[0].category == RiskCategory.OPERATIONAL

    def test_vendor_outage_returns_data(self):
        result = flagged_risks("vendor_outage")
        assert len(result) == 1
        assert result[0].category == RiskCategory.DATA

    def test_nonexistent_flag_returns_empty(self):
        result = flagged_risks("nonexistent")
        assert result == []

    def test_empty_string_returns_empty(self):
        result = flagged_risks("")
        assert result == []
